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
        <h2>{{ match.scheduledTime }}</h2>
        <p>Match ID: {{ match.id }}</p>
        <p :class="['status', match.status]">Status: {{ match.status }}</p>
        <p>Teams: {{ match.teamAName }} vs {{ match.teamBName }}</p>
      </div>
    </div>
    <div v-else class="no-matches">
      <p>No matches found for this tournament.</p>
    </div>



    <div class="availability-form" style="display: flex; flex-direction: column; gap: 10px;">

      <!-- Week Dropdown -->
      <select v-model="selectedWeek" style="border: 1px solid red">
        <option disabled value="">Select a Week</option>
        <option v-for="week in weeks" :key="week" :value="week">{{ week }}</option>
      </select>


      <!-- Checkbox List -->
      <div class="checkboxes" style="display: flex; flex-direction: column;">
        <label v-for="day in days" :key="day">
          <input type="checkbox" :value="day" v-model="selectedDays" />
          {{ day }}
        </label>
      </div>

      <!-- Submit Button -->
      <button @click="submitAvailability" class="submit-btn">
        Submit Availability
      </button>

      <!-- Success Message -->
      <div v-if="showMessage" class="message">
        Availability submitted!
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
// const showAvailabilityModal = ref(false)
// const selectedMatch = ref(null)
// const selectedDays = ref([])
// const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
// const modalMessage = ref('')

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
    console.log("📦 Fetching tournament data...");
    const tourneyRef = doc(db, 'tournaments', tournamentId)
    const tourneySnap = await getDoc(tourneyRef)
    if (tourneySnap.exists()) {
      const data = tourneySnap.data()
      tournamentName.value = data.tournamentName || data.name || `Tournament ${tournamentId}`
    }

    console.log("📦 Fetching matches...");
    const matchesRef = collection(db, 'matches')
    const q = query(matchesRef, where('tournamentId', '==', tournamentId))
    const snapshot = await getDocs(q)

    console.log("🎯 Total matches found:", snapshot.docs.length)

    const enrichedMatches = await Promise.all(
      snapshot.docs.map(async (docSnap) => {
        const matchData = docSnap.data()
        const teamAId = matchData.teamAId
        const teamBId = matchData.teamBId

        console.log(`🔍 Getting team names for ${teamAId} vs ${teamBId}`)

        try {
          const teamARef = doc(db, 'teams', teamAId)
          const teamBRef = doc(db, 'teams', teamBId)

          const [teamASnap, teamBSnap] = await Promise.all([getDoc(teamARef), getDoc(teamBRef)])

          const teamAName = teamASnap.exists() ? teamASnap.data().name : teamAId
          const teamBName = teamBSnap.exists() ? teamBSnap.data().name : teamBId

          return {
            id: docSnap.id,
            ...matchData,
            teamAName,
            teamBName
          }
        } catch (err) {
          console.error("❌ Error fetching team names:", err)
          return {
            id: docSnap.id,
            ...matchData,
            teamAName: teamAId,
            teamBName: teamBId
          }
        }
      })
    )

    console.log("✅ Final enriched matches:", enrichedMatches)
    matches.value = enrichedMatches
  } catch (error) {
    console.error('🔥 Error loading tournament/matches:', error)
  }
})


// Open modal



const weeks = [
  "Week 1", "Week 2", "Week 3", "Week 4",
  "Week 5", "Week 6", "Week 7", "Week 8"
]
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

const selectedWeek = ref('')
const selectedDays = ref([])
const showMessage = ref(false)

function submitAvailability() {
  if (selectedWeek.value && selectedDays.value.length > 0) {
    showMessage.value = true
    setTimeout(() => {
      showMessage.value = false
    }, 3000)
  } else {
    alert("Please select a week and at least one day.")
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


.checkbox-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.checkbox-item {
  margin: 0.25rem 0;
}



.availability-form {
  /* Optional: move this here instead of using inline style */
  display: flex;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}


.submit-btn {
  margin-left: 20px;
  padding: 6px 14px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
}

.message {
  margin-left: 20px;
  color: green;
  font-weight: bold;
}

.status {
  font-weight: bold;
  margin: 0.3rem 0;
}

.status.ongoing {
  color: #f39c12; /* orange-ish */
}

.status.completed {
  color: #27ae60; /* green */
}

</style>
