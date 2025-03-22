<template>
  <div class="my-tournaments-page">
    <h1>My Tournaments</h1>
    <div v-if="loading" class="loader">Loading your tournaments...</div>
    <div v-else>
      <div v-if="tournaments.length" class="tournament-grid">
        <div
          class="tournament-card"
          v-for="tournament in tournaments"
          :key="tournament.id"
        >
          <h2>{{ tournament.tournamentName }}</h2>
          <p>ID: {{ tournament.id }}</p>
          <p>Status: {{ tournament.status }}</p>

          <!-- Example: Just a "View Tournament" button to see details -->
          <button @click="viewTournament(tournament)">View Tournament</button>
        </div>
      </div>

      <div v-else>
        <p>You have not joined any tournaments yet.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { onAuthStateChanged } from 'firebase/auth'
import { auth, db } from '../firebase'
import { collection, query, where, getDocs } from 'firebase/firestore'

const router = useRouter()
const loading = ref(true)
const tournaments = ref([])
const currentUser = ref(null)

// Check authentication; if not logged in, redirect to /login
onAuthStateChanged(auth, (user) => {
  if (!user) {
    router.push('/login')
  } else {
    currentUser.value = user
    loadMyTournaments()
  }
})

// Query tournaments where the player's UID is in the "players" array
async function loadMyTournaments() {
  try {
    const tournamentsRef = collection(db, 'tournaments')
    // Find any tournaments where this user is a participant
    const q = query(tournamentsRef, where('players', 'array-contains', currentUser.value.uid))
    const snapshot = await getDocs(q)
    tournaments.value = snapshot.docs.map((docSnap) => ({
      id: docSnap.id,
      ...docSnap.data()
    }))
  } catch (error) {
    console.error('Error loading user tournaments:', error)
  } finally {
    loading.value = false
  }
}

// Navigate to a tournament details page
function viewTournament(tournament) {
  console.log(tournament.id);
  router.push({ name: 'TournamentDetails', params: { id: tournament.id } })
}
</script>

<style scoped>
.my-tournaments-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loader {
  text-align: center;
  font-size: 1.5rem;
  margin-bottom: 2rem;
}

/* Reuse the same grid/card styles from your Home page if you like */
.tournament-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  margin-bottom: 2rem;
}

.tournament-card {
  border: 1px solid var(--color-border);
  background-color: var(--color-background-soft);
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.tournament-card h2 {
  color: var(--color-heading);
  margin-bottom: 0.5rem;
}

.tournament-card p {
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

button {
  padding: 0.5rem 1rem;
  margin: 0.5rem 0.25rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(90deg, #6a5af9, #9e6af8);
  color: #fff;
  font-weight: 500;
  cursor: pointer;
  transition: filter 0.2s ease;
}

button:hover {
  filter: brightness(1.1);
}
</style>
