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
          <!-- <p><strong>Team ID:</strong> {{ team.team_id }}</p> -->
          <!-- <p><strong>Captain ID:</strong> {{ team.captain_id }}</p> -->
          <p><strong>Captain Name:</strong> {{ team.captain_name }}</p>
          <!-- <p><strong>Players:</strong> -->
            <!-- If players_id is an array, join them with commas -->
            <!-- <span v-if="Array.isArray(team.players_id)">
              {{ team.players_id.join(', ') }}
            </span>
            <span v-else>
              {{ team.players_id }}
            </span>
          </p> -->

          <p><strong>Players:</strong>
            <!-- If players_name is an array, join them with commas -->
            <span v-if="Array.isArray(team.players_name)">
              {{ team.players_name.join(', ') }}
            </span>
            <span v-else>
              {{ team.players_name }}
            </span>
          </p>
          <!-- <p><strong>Wins:</strong> {{ team.wins }}</p>
          <p><strong>Losses:</strong> {{ team.losses }}</p> -->

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

<script>
  import { ref, onMounted } from 'vue';
  import axios from 'axios';
  import { getAuth } from 'firebase/auth';

  export default {
    setup() {
      const teams = ref([]);  // Store teams the user is part of
      const loading = ref(true);  // Loading state
      const errorMessage = ref('');  // Error message if any

      // Get the current logged-in user's ID from Firebase Authentication
      const auth = getAuth();
      const user = auth.currentUser;
      const userId = user ? user.uid : null;

      // Fetch the user's teams from the backend service
      const getUserTeams = async () => {
        if (!userId) {
          console.error('User is not logged in.');
          return;
        }

        try {
          // Get the Firebase ID token for the current user
          const idToken = await user.getIdToken();

          // Send the ID token as part of the Authorization header
          const response = await axios.get('http://localhost:5002/teams', {
            headers: {
              'Authorization': `Bearer ${idToken}`,  // Pass the ID token in the header
            }
          });

          // Assuming response contains the teams data
          teams.value = response.data.teams;  // This should be an array of team objects
        } catch (error) {
          console.error('Error fetching teams: ', error);
          errorMessage.value = 'Error fetching teams.';
        } finally {
          loading.value = false;
        }
      };

      // Load the teams when the component is mounted
      onMounted(() => {
        getUserTeams();
      });

      return {
        teams,
        loading,
        errorMessage,
      };
    }
  };
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
