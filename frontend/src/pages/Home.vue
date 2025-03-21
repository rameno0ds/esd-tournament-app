<template>
  <!-- Only render the home page if the user has loaded -->
  <div v-if="currentUser" class="home-page">
    <h1>Welcome, {{ username }}!</h1>
    <h2>All Ongoing Tournaments</h2>

    <!-- Loader while fetching tournaments -->
    <div v-if="loading" class="loader">Loading tournaments...</div>
    <div v-else>
      <div class="tournament-grid">
        <div class="tournament-card" v-for="tournament in tournaments" :key="tournament.id">
          <h2>{{ tournament.name }}</h2>
          <p>ID: {{ tournament.id }}</p>
          <p>Status: {{ tournament.status }}</p>

          <!-- If the user has already joined this tournament -->
          <div v-if="hasJoined(tournament)">
            <button disabled>Joined</button>
            <button @click="viewTournament(tournament)">View Tournament</button>
          </div>
          <!-- Otherwise, show the join button only -->
          <div v-else>
            <button @click="joinTournament(tournament)">Join Tournament</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Announcements / News -->
    <section class="announcements">
      <h2>Announcements / News</h2>
      <ul>
        <li v-for="(announcement, index) in announcements" :key="index">
          {{ announcement }}
        </li>
      </ul>
    </section>

    <!-- Profile Summary / Stats -->
    <section class="profile-summary">
      <h2>Profile Summary / Stats</h2>
      <p><strong>Rank:</strong> {{ profile.rank }}</p>
      <p><strong>Points:</strong> {{ profile.points }}</p>
      <p><strong>Recent Activity:</strong> {{ profile.recentActivity }}</p>
    </section>

    <!-- Quick Actions -->
    <section class="quick-actions">
      <h2>Quick Actions</h2>
      <div class="actions">
        <button @click="createTeam">Create a Team</button>
        <button @click="goToTournaments">Join a Tournament</button>
        <button @click="submitAvailability">Submit Availability</button>
        <button @click="reportMatch">Report a Match</button>
      </div>
    </section>
  </div>

  <!-- Fallback loader if user not loaded -->
  <div v-else class="loader">Loading user...</div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { onAuthStateChanged } from 'firebase/auth'
import { auth, db } from '../firebase'
import {
  collection,
  query,
  where,
  getDocs,
  updateDoc,
  doc,
  arrayUnion
} from 'firebase/firestore'

// Router and reactive state
const router = useRouter()
const currentUser = ref(null)
const loading = ref(true)

// Data for tournaments, announcements, and profile (dummy for now)
const tournaments = ref([])
const announcements = ref([
  'Patch 1.1 released: New map added.',
  'New rules implemented for fair play.',
  'Upcoming event: Esports Championship 2025.'
])
const profile = ref({
  rank: 'Silver',
  points: 1500,
  recentActivity: 'Won a match in Tournament A.'
})

// Computed username (displayName or email)
const username = computed(() => {
  if (currentUser.value) {
    return currentUser.value.displayName || currentUser.value.email || 'User'
  }
  return ''
})

// Listen for Firebase Auth state changes
onAuthStateChanged(auth, (user) => {
  console.log("Auth state changed:", user)
  if (!user) {
    router.push('/login')
  } else {
    currentUser.value = user
    loadOngoingTournaments()
  }
})

// Function to load all ongoing tournaments from Firestore
async function loadOngoingTournaments() {
  try {
    const tournamentsRef = collection(db, 'tournaments')
    const q = query(tournamentsRef, where('status', '==', 'ongoing'))
    const snapshot = await getDocs(q)
    tournaments.value = snapshot.docs.map(docSnap => ({
      id: docSnap.id,
      ...docSnap.data()
    }))
    console.log("Fetched tournaments:", tournaments.value)
  } catch (error) {
    console.error('Error loading tournaments:', error)
  } finally {
    loading.value = false
  }
}

// Helper function to check if the user has joined a tournament
function hasJoined(tournament) {
  return tournament.players && tournament.players.includes(currentUser.value.uid)
}

// Function to join a tournament
async function joinTournament(tournament) {
  if (!currentUser.value) return
  try {
    if (!tournament.players || !tournament.players.includes(currentUser.value.uid)) {
      const tournamentDocRef = doc(db, 'tournaments', tournament.id)
      await updateDoc(tournamentDocRef, {
        players: arrayUnion(currentUser.value.uid)
      })
      alert(`Successfully joined ${tournament.name}!`)
      // Update the local tournament data so the UI reflects the change immediately.
      if (!tournament.players) tournament.players = []
      tournament.players.push(currentUser.value.uid)
    } else {
      alert('You have already joined this tournament.')
    }
  } catch (error) {
    console.error('Error joining tournament:', error)
    alert('Failed to join tournament. Check console for details.')
  }
}

// Function to view tournament details (redirects to a route showing matches)
function viewTournament(tournament) {
  router.push({ name: 'TournamentDetails', params: { id: tournament.id } })
}

// Quick action functions
function createTeam() {
  router.push('/teams')
}
function goToTournaments() {
  router.push('/tournaments')
}
function submitAvailability() {
  router.push('/schedule')
}
function reportMatch() {
  router.push('/dispute')
}
</script>

<style scoped>
.home-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.loader {
  text-align: center;
  font-size: 1.5rem;
  margin-top: 4rem;
}

h1 {
  color: var(--color-heading);
  margin-bottom: 2rem;
}

/* Tournament Grid */
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

button:disabled {
  background: #ccc;
  color: #666;
  cursor: not-allowed;
  filter: none;
  box-shadow: none;
  opacity: 0.6;
}

/* Announcements, Profile, Quick Actions Sections */
.announcements,
.profile-summary,
.quick-actions {
  margin-bottom: 2rem;
  padding: 1rem;
  background-color: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
}

ul {
  list-style: none;
  padding: 0;
}

ul li {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}

ul li:last-child {
  border-bottom: none;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
</style>
