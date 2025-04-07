<template>
  <!-- Render only if user data is loaded -->
  <div v-if="currentUser" class="home-page">
    <h1>Welcome, {{ username }}!</h1>

    <div class="tournament-columns">
      <div class="tournament-section">
        <h2>All Ongoing Tournaments</h2>
        <button @click="logToken">Log Token</button>

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
              <!-- Not joined but ongoing -->
              <div v-else-if="tourney.status === 'ongoing'">
                <button @click="viewTournament(tourney)">View Tournament</button>
              </div>
              <!-- Otherwise, only view -->
              <div v-else>
                <button @click="viewTournament(tourney)">View Tournament</button>
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
            <!-- Discord Channel Invitation -->
            <div v-if="tourney.status === 'upcoming'" class="discord-invite">
              <p>
                🔔 Before you join the tournament, hop into our
                <a :href="discordInviteUrl" target="_blank" rel="noopener">
                  Discord Community
                </a>
                for real‑time updates, match‑making help, and to meet fellow teams and competitors!
              </p>
            </div>
            <button @click="viewUpcomingTournament(tourney)">View Details</button>
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
import axios from 'axios'

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

const discordInviteUrl = 'https://discord.gg/e6a7aVNe'

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

// Call to your Teams microservice
async function loadMyTeams() {
  if (!currentUser.value) return
  try {
    const token = await currentUser.value.getIdToken()
    const response = await axios.get("http://localhost:5003/teams", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    myTeams.value = response.data.teams.map(team => ({
      id: team.id,
      name: team.name,
      captain_id: team.captain_id,
      players: team.players,
      tournaments_id: team.tournament_id?.[0] || null  // adjust if multiple tournaments allowed
    }))

    console.log("Loaded myTeams (via microservice):", myTeams.value)
  } catch (error) {
    console.error("Error loading user teams from microservice:", error)
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
    console.log(`Discord Notification: User ${currentUser.value.uid} joined tournament ${tournamentId} with team ${selectedTeamId.value}`)
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

// View tournament details
function viewTournament(tournament) {
  router.push({ name: 'TournamentDetails', params: { id: tournament.id } })
}

// View upcoming tournament details
function viewUpcomingTournament(tournament) {
  router.push({ name: 'UpcomingTournamentDetails', params: { id: tournament.id } })
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

import { getAuth } from "firebase/auth";

function logToken() {
  const user = getAuth().currentUser;
  if (user) {
    user.getIdToken(true).then(token => {
      console.log("🔥 ID Token:", token);
    });
  } else {
    console.log("❌ No user logged in.");
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&display=swap');

.home-page {
  font-family: 'Oswald', sans-serif;
  max-width: 1200px;
  margin: 1rem auto;
  padding: 1.5rem;
  background: #fefefe;
  color: #333;
}

/* Loader styling */
.loader {
  text-align: center;
  font-size: 1.5rem;
  margin-top: 4rem;
}

/* Headings */
h1 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
}

/* Tournament Columns & Section */
.tournament-columns {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.tournament-section {
  background: #fff;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* Tournament Grid */
.tournament-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

/* Tournament Card */
.tournament-card {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.tournament-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.tournament-card h2 {
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
  color: #222;
}
.tournament-card p {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #555;
}

/* Button Styling */
button {
  padding: 0.5rem 1rem;
  margin: 0.3rem;
  border: none;
  border-radius: 6px;
  background: linear-gradient(90deg, #6a5af9, #9e6af8);
  color: #fff;
  font-weight: 500;
  cursor: pointer;
  transition: filter 0.2s ease, background 0.2s ease;
}
button:hover {
  filter: brightness(1.1);
}
button:disabled {
  background: #ccc;
  color: #666;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Join Options */
.join-options {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #fff;
  text-align: left;
}
.join-options select {
  margin-right: 0.5rem;
  padding: 0.3rem;
  font-size: 0.9rem;
}
.join-options h3 {
  margin-top: 1rem;
  font-size: 1rem;
}

/* Confirmation Message */
.confirmation {
  margin-top: 0.8rem;
  padding: 0.5rem;
  background: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  font-weight: 500;
  color: #0050b3;
}

/* Announcements, Profile Summary, and Quick Actions */
.announcements,
.profile-summary,
.quick-actions {
  margin-top: 2rem;
  padding: 1rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.announcements h2,
.profile-summary h2,
.quick-actions h2 {
  margin-bottom: 1rem;
  font-size: 1.3rem;
  color: #333;
}
ul {
  list-style: none;
  padding: 0;
}
ul li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #ddd;
  font-size: 0.9rem;
}
ul li:last-child {
  border-bottom: none;
}

/* Quick Actions Buttons */
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}
.actions button {
  flex: 1 1 auto;
}

/* Discord Invite */
.discord-invite {
  margin: 0.75rem 0;
  padding: 0.75rem;
  background: #f0f4ff;
  border-left: 4px solid #5865f2;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #2c2f33;
}
.discord-invite a {
  color: #5865f2;
  font-weight: 600;
  text-decoration: none;
}
.discord-invite a:hover {
  text-decoration: underline;
}
</style>

