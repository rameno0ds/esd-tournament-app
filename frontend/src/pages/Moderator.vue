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
          <h2>{{ tourney.name }}</h2>
          <p>Tournament ID: {{ tourney.id }}</p>
          <p>Status: {{ tourney.status }}</p>

          <!-- Button to toggle weeks display -->
          <button @click="toggleWeeks(tourney.id)">
            {{ tourney.showWeeks ? 'Hide Weeks' : 'View Weeks' }}
          </button>

          <!-- If showWeeks is true, list the weeks -->
          <div v-if="tourney.showWeeks" class="weeks-section">
            <h3>Weeks</h3>
            <ul>
              <li v-for="week in tourney.weeks" :key="week.number" class="week-item">
                <strong>Week {{ week.number }}</strong> — Status: {{ week.status }}

                <!-- If completed, show "Match Record" button -->
                <button v-if="week.status === 'completed'" @click="viewMatchRecord(tourney.id, week.number)">
                  Match Record
                </button>

                <!-- If upcoming, show "Create Matches" button -->
                <button v-else-if="week.status === 'upcoming'" @click="createMatches(tourney.id, week.number)">
                  Create Matches
                </button>

                <!-- If in_progress, you could show "View Matches" or something else -->
                <button v-else-if="week.status === 'in_progress'" @click="viewMatches(tourney.id, week.number)">
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

    const response = await axios.get('http://localhost:5002/tournament', {
      headers: {
        'Authorization': `Bearer ${idToken}`
      }
    })
    console.log('response.data:', response.data)
    ongoingTournaments.value = response.data.map(t => ({
      ...t,
      showWeeks: false  // For toggling the display of weeks
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
  // For demonstration, just alert
  alert(`Viewing match record for Tournament ${tournamentId}, Week ${weekNumber}`)
}

// If upcoming => "Create Matches" button
async function createMatches(tournamentId, weekNumber) {
  try {
    const auth = getAuth()
    const user = auth.currentUser
    if (!user) {
      errorMessage.value = 'You must be logged in as a moderator.'
      return
    }
    const idToken = await user.getIdToken()

    // POST to /matchmaking
    const response = await axios.post('http://localhost:5005/matchmaking', 
      {
        tournamentId,
        weekNumber
      },
      {
        headers: {
          'Authorization': `Bearer ${idToken}`
        }
      }
    )
    // Expect response.data to have a success message or updated matches
    alert(`Matches for Week ${weekNumber} created!`)
    
    // Optionally, update the week status to 'in_progress'
    const tourney = ongoingTournaments.value.find(t => t.id === tournamentId)
    if (tourney) {
      const week = tourney.weeks.find(w => w.number === weekNumber)
      if (week) {
        week.status = 'in_progress'
      }
    }
  } catch (error) {
    console.error('Error creating matches:', error)
    errorMessage.value = 'Failed to create matches.'
  }
}

// If in_progress => "View Matches" button
function viewMatches(tournamentId, weekNumber) {
  alert(`Viewing matches for Tournament ${tournamentId}, Week ${weekNumber}`)
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
