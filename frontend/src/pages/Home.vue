<template>
  <!-- Render only if user data is loaded -->
  <div v-if="currentUser" class="home-page">
    <h1>Welcome, {{ username }}!</h1>

    <div class="tournament-columns">
      <div class="tournament-section">
        <h2>All Ongoing Tournaments</h2>


        <!-- Loader while fetching tournaments -->
        <div v-if="loading" class="loader">Loading tournaments...</div>
        <div v-else>
          <div class="tournament-grid">
            <div class="tournament-card" v-for="tourney in tournaments" :key="tourney.id">
              <h2>{{ tourney.tournamentName }}</h2>
              <p>ID: {{ tourney.id }}</p>
              <p>Status: {{ tourney.status }}</p>

              <!-- If the user has already joined this tournament -->
              <div v-if="hasJoined(tourney)">
                <button disabled>Joined</button>
                <button @click="viewTournament(tourney)">View Tournament</button>
              </div>
              <!-- Otherwise, show the join button which toggles the join UI -->
              <div v-else>
                <button @click="toggleJoin(tourney.id)">Join Tournament</button>
              </div>

              <!-- Inline UI for joining (shown only for the expanded tournament) -->
              <div v-if="expandedJoin === tourney.id" class="join-options">
                <h3>Join with an Existing Team</h3>
                <label for="teamSelect">Select a Team:</label>
                <select id="teamSelect" v-model="selectedTeamId">
                  <option disabled value="">-- Choose a team --</option>
                  <option v-for="team in availableTeams(tourney.id)" :key="team.id" :value="team.id">
                    {{ team.name }} (ID: {{ team.id }})
                  </option>
                </select>
                <button @click="joinWithTeam(tourney.id)" :disabled="!selectedTeamId">
                  Confirm
                </button>
                <h3>Or Auto-Create a Team</h3>
                <button @click="autoTeam(tourney.id)">Auto Team</button>
                <!-- Confirmation message for this tournament's join action -->
                <div v-if="confirmation[tourney.id]" class="confirmation">
                  {{ confirmation[tourney.id] }}
                </div>
              </div>
            </div>
          </div>
        </div>




        <h2>Upcoming Tournaments</h2>
        <div class="tournament-grid">
          <div class="tournament-card" v-for="tourney in upcomingTournaments" :key="tourney.id">
            <h2>{{ tourney.tournamentName }}</h2>
            <p>ID: {{ tourney.id }}</p>
            <p>Status: {{ tourney.status }}</p>
            <button @click="viewTournament(tourney)">View Details</button>
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
  addDoc,
  arrayUnion
} from 'firebase/firestore'

// Router and reactive state
const router = useRouter()
const currentUser = ref(null)
const loading = ref(true)

// Tournaments and join confirmation messages (keyed by tournament id)
const tournaments = ref([])
const confirmation = ref({})
const upcomingTournaments = ref([])


// List of teams the user belongs to
const myTeams = ref([])

// UI state for the join flow
const expandedJoin = ref('')
const selectedTeamId = ref('')

// Dummy announcements and profile
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

// Computed username
const username = computed(() => {
  if (currentUser.value) {
    return currentUser.value.displayName || currentUser.value.email || 'User'
  }
  return ''
})

// Listen for auth state changes
onAuthStateChanged(auth, (user) => {
  console.log("Auth state changed:", user)
  if (!user) {
    router.push('/login')
  } else {
    currentUser.value = user
    loadOngoingTournaments()
    loadUpcomingTournaments()
    loadMyTeams()
  }
})

// Load ongoing tournaments from Firestore
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

async function loadUpcomingTournaments() {
  try {
    const tournamentsRef = collection(db, 'tournaments')
    const q = query(tournamentsRef, where('status', '==', 'upcoming'))
    const snapshot = await getDocs(q)
    upcomingTournaments.value = snapshot.docs.map(docSnap => ({
      id: docSnap.id,
      ...docSnap.data()
    }))
    console.log("Fetched upcoming tournaments:", upcomingTournaments.value)
  } catch (error) {
    console.error('Error loading upcoming tournaments:', error)
  }
}


// Load user's teams from Firestore
async function loadMyTeams() {
  if (!currentUser.value) return
  try {
    const teamsRef = collection(db, 'teams')
    const q = query(teamsRef, where('players_id', 'array-contains', currentUser.value.uid))
    const snapshot = await getDocs(q)
    myTeams.value = snapshot.docs.map(docSnap => ({
      id: docSnap.id,
      ...docSnap.data()
    }))
    console.log("Loaded myTeams:", myTeams.value)
  } catch (error) {
    console.error('Error loading user teams:', error)
  }
}

// Helper: Return teams not already in the tournament
function availableTeams(tournamentId) {
  return myTeams.value.filter(team => !team.tournaments_id || team.tournaments_id !== tournamentId)
}

// Check if user has joined a tournament (by checking if their uid is in tournament.players)
function hasJoined(tournament) {
  return tournament.players && tournament.players.includes(currentUser.value.uid)
}

// Toggle the join UI for a specific tournament
function toggleJoin(tournamentId) {
  expandedJoin.value = (expandedJoin.value === tournamentId) ? '' : tournamentId
  selectedTeamId.value = ''
  // Clear any previous confirmation message for this tournament
  confirmation.value[tournamentId] = ''
}

// Join with an existing team for a given tournament
async function joinWithTeam(tournamentId) {
  if (!selectedTeamId.value || !currentUser.value) return
  try {
    const teamDocRef = doc(db, 'teams', selectedTeamId.value)
    await updateDoc(teamDocRef, {
      tournaments_id: tournamentId,
      players_id: arrayUnion(currentUser.value.uid)
    })
    // Also update tournament doc: add user to players array
    const tournamentDocRef = doc(db, 'tournaments', tournamentId)
    await updateDoc(tournamentDocRef, {
      players: arrayUnion(currentUser.value.uid)
    })
    confirmation.value[tournamentId] = `Successfully joined with team ${selectedTeamId.value}!`
    // Simulate Discord notification
    console.log(`Discord Notification: User ${currentUser.value.uid} joined tournament ${tournamentId} with team ${selectedTeamId.value}`)
    // Optionally, update the local tournament object's players array
    if (!tournaments.value.find(t => t.id === tournamentId).players) {
      tournaments.value.find(t => t.id === tournamentId).players = []
    }
    tournaments.value.find(t => t.id === tournamentId).players.push(currentUser.value.uid)
  } catch (error) {
    console.error('Error joining with team:', error)
    alert('Failed to join. Check console for details.')
  }
}

// Auto-create a new team and join the tournament
async function autoTeam(tournamentId) {
  if (!currentUser.value) return
  try {
    const randomSuffix = Math.floor(Math.random() * 1000)
    const newTeamName = `AutoTeam${randomSuffix}`
    const docRef = await addDoc(collection(db, 'teams'), {
      name: newTeamName,
      captain_id: currentUser.value.uid,
      players_id: [currentUser.value.uid],
      tournaments_id: tournamentId
    })
    // Also update tournament doc: add user to players array
    const tournamentDocRef = doc(db, 'tournaments', tournamentId)
    await updateDoc(tournamentDocRef, {
      players: arrayUnion(currentUser.value.uid)
    })
    confirmation.value[tournamentId] = `Successfully created ${newTeamName} and joined tournament ${tournamentId}!`
    console.log(`Discord Notification: User ${currentUser.value.uid} auto-created team ${newTeamName} for tournament ${tournamentId}`)
  } catch (error) {
    console.error('Error auto-creating team:', error)
    alert('Failed to auto-create team. Check console for details.')
  }
  expandedJoin.value = ''
}

// View tournament details (redirect to page showing matches)
function viewTournament(tournament) {
  router.push({ name: 'TournamentDetails', params: { id: tournament.id } })
}

// Quick actions
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

/* Inline join UI */
.join-options {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background-color: var(--color-background);
  text-align: left;
}

.join-options select {
  margin-right: 0.5rem;
  padding: 0.25rem;
  font-size: 0.9rem;
}

.join-options h3 {
  margin-top: 1rem;
}

.confirmation {
  margin-top: 1rem;
  padding: 0.5rem;
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  font-weight: 500;
  color: #0050b3;
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

.tournament-columns {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  margin-top: 2rem;
}

.tournament-section {
  flex: 1;
  min-width: 300px;
}

.tournament-grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;
}

.tournament-card {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #ccc;
}

</style>
