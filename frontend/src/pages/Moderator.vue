<template>
  <div class="moderator-home">
    <h1>Moderator Home</h1>

    <!-- Error message if any -->
    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

    <!-- Loader while fetching data -->
    <div v-if="loading" class="loader">Loading tournaments...</div>

    <!-- List of ongoing tournaments -->
    <div v-else>
      <div v-if="ongoingTournaments.length" class="tournament-list">
        <div v-for="tourney in ongoingTournaments" :key="tourney.id" class="tournament-card">
          <h2>{{ tourney.tournamentName }}</h2>
          <p>Status: {{ tourney.status }}</p>

          <!-- Button to toggle weeks display -->
          <button @click="toggleWeeks(tourney.id)">
            {{ tourney.showWeeks ? 'Hide Weeks' : 'View Weeks' }}
          </button>

          <!-- If showWeeks is true, list the "weeks" or "rounds" -->
          <div v-if="tourney.showWeeks" class="weeks-section">
            <h3>Weeks/Rounds</h3>
            <ul>
              <li v-for="week in tourney.weeks" :key="week.number" class="week-item">
                <strong>Round {{ week.number }}</strong> — Status: {{ week.status }}

                <!-- If completed, show "Match Record" button -->
                <button v-if="week.status === 'completed'" @click="viewMatchRecord(tourney.id, week.number)">
                  Match Record
                </button>

                <!-- If upcoming, show "Create Matches" button -->
                <button v-else-if="week.status === 'upcoming'" @click="createMatches(tourney.id, week.number)">
                  Create Matches
                </button>

                <!-- If ongoing, you could show "View Matches" or something else -->
                <button v-else-if="week.status === 'ongoing'" @click="viewMatches(tourney.id, week.number)">
                  View Matches
                </button>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div v-else>
        <p>No ongoing tournaments found.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { getAuth } from 'firebase/auth'

// Reactive variables
const ongoingTournaments = ref([])  // Array of tournaments
const loading = ref(true)
const errorMessage = ref('')

// On mount, fetch the ongoing tournaments
onMounted(() => {
  fetchOngoingTournaments()
})

async function fetchOngoingTournaments() {
  try {
    const auth = getAuth()
    const user = auth.currentUser
    if (!user) {
      errorMessage.value = 'You must be logged in as a moderator.'
      loading.value = false
      return
    }
    const idToken = await user.getIdToken()

    // Example: fetch all tournaments with status "ongoing"
    const response = await axios.get('http://localhost:5002/tournaments?status=ongoing', {
      headers: {
        Authorization: `Bearer ${idToken}`
      }
    })
    // Suppose the response has a structure like:
    // [
    //   { id: "BNck5GT9pQx8DVQ9x3sF", name: "MyTournament", status: "ongoing", ... }
    // ]
    ongoingTournaments.value = response.data.map(t => ({
      ...t,
      showWeeks: false,
      weeks: [
        // Example data for demonstration:
        { number: 1, status: 'completed' },
        { number: 2, status: 'upcoming' },
        { number: 3, status: 'ongoing' }
      ]
    }))
    
  } catch (error) {
    console.error('Error fetching tournaments:', error)
    errorMessage.value = 'Failed to load tournaments.'
  } finally {
    loading.value = false
  }
}

// Toggle the weeks display for a given tournament
function toggleWeeks(tournamentId) {
  const tourney = ongoingTournaments.value.find(t => t.id === tournamentId)
  if (tourney) {
    tourney.showWeeks = !tourney.showWeeks
  }
}

// If completed => "Match Record" button
function viewMatchRecord(tournamentId, weekNumber) {
  alert(`Viewing match record for Tournament ${tournamentId}, Round ${weekNumber}`)
}

// If upcoming => "Create Matches" button
async function createMatches(tournamentId, roundNumber) {
  try {
    // Option A: Directly call the schedule service's create_matches endpoint:
    // const response = await axios.post(`http://localhost:5003/schedule/${tournamentId}/round/${roundNumber}/create_matches`)

    // Option B: Call the composite "Make a Match" service:
    const response = await axios.post('http://localhost:5006/make_matches', {
      tournamentId,
      roundNumber
    })

    console.log('Matches created:', response.data)
    alert(response.data.message)
  } catch (error) {
    console.error('Error creating matches:', error)
    alert('Failed to create matches. Check console for details.')
  }
}

// If ongoing => "View Matches" button
function viewMatches(tournamentId, weekNumber) {
  alert(`Viewing matches for Tournament ${tournamentId}, Round ${weekNumber}`)
  // e.g., navigate to a page that lists all matches for that round
}
</script>

<style scoped>
.moderator-home {
  padding: 2rem;
  max-width: 1000px;
  margin: 2rem auto;
}

.error {
  color: red;
  margin-bottom: 1rem;
  text-align: center;
}

.loader {
  text-align: center;
  font-size: 1.5rem;
}

.tournament-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tournament-card {
  border: 1px solid #ddd;
  background-color: #fff;
  padding: 1rem;
  border-radius: 6px;
}

.weeks-section {
  margin-top: 1rem;
  padding-left: 1rem;
  border-left: 3px solid #ccc;
}

.week-item {
  margin-bottom: 1rem;
}

button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(90deg, #6a5af9, #9e6af8);
  color: #fff;
  font-weight: 500;
  cursor: pointer;
  transition: filter 0.2s ease;
  margin-top: 0.5rem;
}

button:hover {
  filter: brightness(1.1);
}
</style>
