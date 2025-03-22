<template>
  <div class="teams-page">
    <h1>My Teams</h1>
    <div v-if="loading" class="loader">Loading your teams...</div>
    <div v-else>
      <div v-if="teams.length" class="teams-grid">
        <div
          v-for="team in teams"
          :key="team.id"
          class="team-card"
        >
          <h2>{{ team.name }}</h2>
          <p><strong>Team ID:</strong> {{ team.team_id }}</p>
          <p><strong>Captain ID:</strong> {{ team.captain_id }}</p>
          <p><strong>Players:</strong>
            <!-- If players_id is an array, join them with commas -->
            <span v-if="Array.isArray(team.players_id)">
              {{ team.players_id.join(', ') }}
            </span>
            <span v-else>
              {{ team.players_id }}
            </span>
          </p>
          <p><strong>Wins:</strong> {{ team.wins }}</p>
          <p><strong>Losses:</strong> {{ team.losses }}</p>

          <!-- If tournaments_id is an array or single value -->
          <p v-if="team.tournaments_id">
            <strong>Tournaments:</strong>
            <span v-if="Array.isArray(team.tournaments_id)">
              {{ team.tournaments_id.join(', ') }}
            </span>
            <span v-else>
              {{ team.tournaments_id }}
            </span>
          </p>
        </div>
      </div>
      <div v-else>
        <p>You have not joined any teams yet.</p>
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
const teams = ref([])
const currentUser = ref(null)

// Listen for auth state; if not logged in, redirect
onAuthStateChanged(auth, (user) => {
  if (!user) {
    router.push('/login')
  } else {
    currentUser.value = user
    loadTeams()
  }
})

// Query the "Team" collection for teams where players_id includes the user
async function loadTeams() {
  try {
    // Adjust if your collection is named "teams" instead of "Team"
    const teamsRef = collection(db, 'Team')
    const q = query(teamsRef, where('players_id', 'array-contains', currentUser.value.uid))
    const snapshot = await getDocs(q)
    teams.value = snapshot.docs.map((docSnap) => ({
      id: docSnap.id,
      ...docSnap.data()
    }))
  } catch (error) {
    console.error('Error loading user teams:', error)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.teams-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loader {
  text-align: center;
  font-size: 1.5rem;
  margin-bottom: 2rem;
}

.teams-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
}

.team-card {
  border: 1px solid #ddd;
  background-color: #fff;
  padding: 1rem;
  border-radius: 8px;
}

.team-card h2 {
  margin-bottom: 0.5rem;
}
</style>
