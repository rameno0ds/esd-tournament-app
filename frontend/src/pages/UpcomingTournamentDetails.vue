<template>
    <div class="tournament-details">
        <h1>{{ tournamentName }}</h1>
        <p><strong>Sign ups have open!</strong></p>
        <h2>Registered Teams</h2>
        <div class="team-grid" v-if="enrichedTeams.length">
            <div class="team-card" v-for="team in enrichedTeams" :key="team.teamId">
                <h3>{{ team.name || 'Unnamed Team' }}</h3>
                <p><strong>Team ID:</strong> {{ team.teamId }}</p>
                <p><strong>Players Joined:</strong> {{ team.players ? Object.keys(team.players).length : 0 }}</p>
                <p><strong>Players:</strong>
                <ul>
                    <li v-for="(name, uid) in team.players" :key="uid">{{ name }}</li>
                    <button v-if="Object.keys(team.players || {}).length < 5 && !userInAnyTeam"
                        @click="joinTeam(team.teamId)">
                        Join Team
                    </button>
                </ul>
                </p>
            </div>
        </div>
        <div v-else>
            <p>No teams have joined this tournament yet.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getAuth } from 'firebase/auth'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const tournamentId = route.params.id
const tournamentName = ref('Upcoming Tournament Details')
const enrichedTeams = ref([])
const user = getAuth().currentUser
const userInAnyTeam = ref(false)

const fetchUserTeams = async () => {
    try {
        const token = await user.getIdToken()
        const response = await axios.get(`http://localhost:5006/composite/check_if_already_in_team`, {
            params: { tournamentId },
            headers: { Authorization: `Bearer ${token}` }
        })

        userInAnyTeam.value = response.data.inTeam === true
    } catch (err) {
        console.error("Error checking user team status:", err)
        userInAnyTeam.value = false
    }
}

const fetchTournamentDetails = async () => {
    try {
        const response = await axios.get(
            `http://localhost:5006/composite/tournament_details_with_teams/${tournamentId}`
        )

        tournamentName.value = response.data.tournamentName || `Tournament ${tournamentId}`
        enrichedTeams.value = response.data.enrichedTeams || []
    } catch (error) {
        console.error('Error loading tournament from composite service:', error)
    }
}

const joinTeam = async (teamId) => {
  try {
    const token = await user.getIdToken(); // Declare and assign token

    await axios.post("http://localhost:5006/composite/join_team", {
      teamId: teamId,
      tournamentId: tournamentId
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    alert("Successfully joined the team!")
    window.location.reload()
  } catch (err) {
    alert("Failed to join team: " + (err.response?.data?.error || err.message))
    console.error("Join team error:", err)
  }
}



onMounted(async () => {
    if (user) {
        await fetchUserTeams()
        await fetchTournamentDetails()
    }
})
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

.team-grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    margin-top: 1.5rem;
}

.team-card {
    border: 1px solid #ccc;
    background-color: #fdfdfd;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

ul {
    list-style: none;
    padding: 0;
    margin: 0;
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
</style>
