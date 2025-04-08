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

                <button
                  v-if="week.status === 'completed'"
                  @click="viewMatchRecord(tourney.id, week.number)"
                >
                  Match Record
                </button>

                <button
                  v-else-if="week.status === 'upcoming'"
                  @click="createMatches(tourney.id, week.number)"
                >
                  Create Matches
                </button>

                <button
                  v-else-if="week.status === 'ongoing'"
                  @click="viewMatches(tourney.id, week.number)"
                >
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

const ongoingTournaments = ref([])
const loading = ref(true)
const errorMessage = ref('')

// Fetch tournaments on mount
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

    const response = await axios.get('http://localhost:5002/tournaments?status=ongoing', {
      headers: {
        Authorization: `Bearer ${idToken}`
      }
    })

    ongoingTournaments.value = response.data.map(t => {
      const curRound = t.curRound ?? 0
      const totalRounds = 3

      const weeks = Array.from({ length: totalRounds }, (_, i) => {
        const round = i + 1
        let status = ''
        if (round < curRound) status = 'completed'
        else if (round === curRound) status = 'ongoing'
        else status = 'upcoming'

        return { number: round, status }
      })

      return {
        ...t,
        curRound,
        showWeeks: false,
        weeks
      }
    })
  } catch (error) {
    console.error('Error fetching tournaments:', error)
    errorMessage.value = 'Failed to load tournaments.'
  } finally {
    loading.value = false
  }
}

function toggleWeeks(tournamentId) {
  const tourney = ongoingTournaments.value.find(t => t.id === tournamentId)
  if (tourney) {
    tourney.showWeeks = !tourney.showWeeks
  }
}

function viewMatchRecord(tournamentId, weekNumber) {
  alert(`Viewing match record for Tournament ${tournamentId}, Round ${weekNumber}`)
}

async function createMatches(tournamentId, roundNumber) {
  try {
    const response = await axios.post('http://localhost:8010/make-match', {
      tournamentId,
      roundNumber
    })

    alert(response.data.message)
    console.log('Matches created:', response.data)

    // Update tournament curRound and regenerate weeks
    const tourney = ongoingTournaments.value.find(t => t.id === tournamentId)
    if (tourney) {
      tourney.curRound = roundNumber

      tourney.weeks = Array.from({ length: 3 }, (_, i) => {
        const round = i + 1
        let status = ''
        if (round < tourney.curRound) status = 'completed'
        else if (round === tourney.curRound) status = 'ongoing'
        else status = 'upcoming'

        return { number: round, status }
      })
    }

  } catch (error) {
    console.error('Error creating matches:', error)
    alert('Failed to create matches. Check console for details.')
  }
}

function viewMatches(tournamentId, weekNumber) {
  alert(`Viewing matches for Tournament ${tournamentId}, Round ${weekNumber}`)
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
