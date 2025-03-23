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
import axios from 'axios'

const route = useRoute()
const tournamentId = route.params.id  // Tournament doc ID from route
const tournamentName = ref('Tournament Details')
const matches = ref([])

// Filter state for matches
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

// Modal state for availability submission
const showAvailabilityModal = ref(false)
const selectedMatch = ref(null)
const selectedDays = ref([])
// Days of the week for checkboxes
const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

// Message to display after submission
const modalMessage = ref('')

// Load tournament details and matches on mount
onMounted(async () => {
  try {
    // Load tournament details
    const tourneyRef = doc(db, 'tournaments', tournamentId)
    const tourneySnap = await getDoc(tourneyRef)
    if (tourneySnap.exists()) {
      const data = tourneySnap.data()
      tournamentName.value = data.tournamentName || data.name || `Tournament ${tournamentId}`
    }
    // Query matches from the "matches" collection for this tournament
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

// Open the modal for a specific match
function openAvailabilityModal(match) {
  selectedMatch.value = match
  selectedDays.value = []      // reset selections
  modalMessage.value = ''      // clear previous messages
  showAvailabilityModal.value = true
}

// Close the modal
function closeModal() {
  showAvailabilityModal.value = false
  selectedMatch.value = null
  selectedDays.value = []
  modalMessage.value = ''
}

// Submit availability to the scheduling microservice
async function submitAvailability() {
  if (!selectedMatch.value) return
  try {
    // Build payload: you may need to adjust this based on your schedule_service.py
    const payload = {
      matchId: selectedMatch.value.id,
      tournamentId: tournamentId,
      availableDays: selectedDays.value
    }
    // POST to your availability endpoint
    const response = await axios.post(`http://localhost:5003/schedule/${tournamentId}/availability`, payload)
    modalMessage.value = response.data.message || "Availability submitted successfully!"
    // Optionally close the modal after a short delay
    setTimeout(() => {
      closeModal()
    }, 2000)
  } catch (error) {
    console.error('Error submitting availability:', error)
    modalMessage.value = "Failed to submit availability. Please try again."
  }
}
</script>

<style scoped>
.tournament-details {
  max-width: 1000px;
  margin: 2rem auto;
  padding: 1rem;
}
h1 {
  margin-bottom: 0.5rem;
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

/* Modal styles */
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
