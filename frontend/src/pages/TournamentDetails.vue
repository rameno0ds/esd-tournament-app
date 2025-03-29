<template>
  <div class="tournament-details">
    <h1>{{ tournamentName }}</h1>
    <p><strong>Tournament:</strong> {{ tournamentName }}</p>

    <!-- Filter dropdown for matches -->
    <div class="filter-section">
      <label for="filterSelect">Filter matches:</label>
      <select id="filterSelect" v-model="selectedFilter">
        <option value="all">All matches</option>
        <option value="upcoming">Upcoming</option>
        <option value="completed">Completed</option>
      </select>
    </div>

    <!-- Matches grid/list -->
    <div class="matches-grid" v-if="matches.length">
      <div v-for="match in filteredMatches" :key="match.id" class="match-card">
        <h2>Match ID: {{ match.id }}</h2>
        <p>Status: {{ match.status }}</p>
        <p>Teams: {{ match.teamA }} vs {{ match.teamB }}</p>
        <!-- If match is upcoming, allow captain to submit availability -->
        <button v-if="match.status === 'upcoming'" @click="openAvailabilityModal(match)">
          Submit Availability
        </button>
      </div>
    </div>
    <div v-else class="no-matches">
      <p>No matches found for this tournament.</p>
    </div>

    <!-- Availability Modal -->
    <div v-if="showAvailabilityModal" class="modal-overlay">
      <div class="modal">
        <h2>Submit Availability for Match {{ selectedMatch.id }}</h2>
        <p>Select the days you are available:</p>
        <form @submit.prevent="submitAvailability">
          <div class="checkbox-group">
            <div v-for="day in daysOfWeek" :key="day" class="checkbox-item">
              <label>
                <input type="checkbox" :value="day" v-model="selectedDays" />
                {{ day }}
              </label>
            </div>
          </div>
          <div class="modal-buttons">
            <button type="submit">Submit Availability</button>
            <button type="button" @click="closeModal">Cancel</button>
          </div>
        </form>
        <div v-if="modalMessage" class="modal-message">
          {{ modalMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { db } from '../firebase'
import { doc, getDoc, collection, query, where, getDocs } from 'firebase/firestore'
import { getAuth, onAuthStateChanged } from 'firebase/auth'
import axios from 'axios'

const route = useRoute()
const tournamentId = route.params.id  // e.g. "BNck5GT9pQx8DVQ9x3sF"
const tournamentName = ref('Tournament Details')
const matches = ref([])

const selectedFilter = ref('all')
const filteredMatches = computed(() => {
  if (selectedFilter.value === 'all') return matches.value
  if (selectedFilter.value === 'upcoming') {
    return matches.value.filter(match => match.status === 'upcoming')
  }
  if (selectedFilter.value === 'completed') {
    return matches.value.filter(match => match.status === 'completed')
  }
  return matches.value
})

// Modal state
const showAvailabilityModal = ref(false)
const selectedMatch = ref(null)
const selectedDays = ref([])
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
const modalMessage = ref('')

// Reactive variable to hold the current player's team ID
const currentTeamId = ref(null)

// Get the current user and then fetch the team ID
const auth = getAuth()
onAuthStateChanged(auth, (user) => {
  if (user) {
    // Here, replace the next line with a call to your teams service
    // to fetch the team info for the current tournament.
    // For this example, we simulate that the player's team is "SMUBEST".
    currentTeamId.value = "SMUBEST"
  }
})

// Load tournament details and matches
onMounted(async () => {
  try {
    const tourneyRef = doc(db, 'tournaments', tournamentId)
    const tourneySnap = await getDoc(tourneyRef)
    if (tourneySnap.exists()) {
      const data = tourneySnap.data()
      tournamentName.value = data.tournamentName || data.name || `Tournament ${tournamentId}`
    }
    const matchesRef = collection(db, 'matches')
    const q = query(matchesRef, where('tournamentId', '==', tournamentId))
    const snapshot = await getDocs(q)
    matches.value = snapshot.docs.map(docSnap => ({
      id: docSnap.id,
      ...docSnap.data()
    }))
  } catch (error) {
    console.error('Error loading tournament/matches:', error)
  }
})

// Open modal
function openAvailabilityModal(match) {
  selectedMatch.value = match
  selectedDays.value = []
  modalMessage.value = ''
  showAvailabilityModal.value = true
}

// Close modal
function closeModal() {
  showAvailabilityModal.value = false
  selectedMatch.value = null
  selectedDays.value = []
  modalMessage.value = ''
}

// Submit availability using the dynamic team ID
async function submitAvailability() {
  if (!selectedMatch.value) return
  if (!currentTeamId.value) {
    modalMessage.value = "Team info not loaded."
    return
  }
  try {
    const payload = {
      teamId: currentTeamId.value,
      availableDays: selectedDays.value,  // e.g. ["Tuesday"]
      roundNumber: 2
    }
    const response = await axios.post(`http://localhost:5005/schedule/${tournamentId}/availability`, payload)
    modalMessage.value = response.data.message || "Availability submitted successfully!"
    setTimeout(() => { closeModal() }, 2000)
  } catch (error) {
    console.error('Error submitting availability:', error)
    modalMessage.value = "Failed to submit availability. Please try again."
  }
}
</script>

<style scoped>
/* (Styles remain unchanged) */
.tournament-details {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 1rem;
}
.filter-section {
  margin: 1rem 0;
}
.matches-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  margin-top: 1rem;
}
.match-card {
  border: 1px solid #ddd;
  background-color: #fff;
  padding: 1rem;
  border-radius: 6px;
}
.no-matches {
  margin-top: 2rem;
  text-align: center;
  font-style: italic;
}
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal {
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  max-width: 400px;
  width: 90%;
}
.checkbox-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}
.checkbox-item {
  margin: 0.25rem 0;
}
.modal-buttons {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}
.modal-message {
  margin-top: 1rem;
  font-weight: bold;
  text-align: center;
  color: green;
}
</style>
