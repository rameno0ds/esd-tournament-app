<template>
    <div class="tournament-details">
        <h1>{{ tournamentName }}</h1>
        <!-- <h1>{{ tournamentId }}</h1> -->
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
import { useRoute } from 'vue-router'
import { db } from '../firebase'
import { doc, getDoc } from 'firebase/firestore'

const route = useRoute()
const tournamentId = route.params.id
const tournamentName = ref('Upcoming Tournament Details')
const teams = ref([])

import axios from 'axios'

const enrichedTeams = ref([])

onMounted(async () => {
    try {
        const tourneyRef = doc(db, 'tournaments', tournamentId)
        const tourneySnap = await getDoc(tourneyRef)

        if (tourneySnap.exists()) {
            const data = tourneySnap.data()
            tournamentName.value = data.tournamentName || `Tournament ${tournamentId}`

            const rawTeams = data.teams || []

            // For each team, fetch details from team microservice
            const enriched = await Promise.all(
                rawTeams.map(async (team) => {
                    try {
                        const response = await axios.get(`http://localhost:5003/team/${team.teamId}`)
                        return {
                            ...team,
                            name: response.data.name,
                            players: response.data.players  // array of player IDs or names
                        }
                    } catch (err) {
                        console.error(`Failed to fetch team ${team.teamId}`, err)
                        return team  // fallback to raw data
                    }
                })
            )

            enrichedTeams.value = enriched
        }
    } catch (error) {
        console.error('Error loading tournament details:', error)
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

</style>