<template>
  <div class="dispute-review">
    <h1>Dispute Review</h1>
    <div class="refresh-container">
      <button @click="fetchPendingDisputes" class="refresh-button">
        Refresh Pending Disputes
      </button>
    </div>
    <div v-if="disputes.length" class="disputes-list">
      <div v-for="dispute in disputes" :key="dispute.matchId" class="dispute-card">
        <h3>Match ID: {{ dispute.matchId }}</h3>
        <p>Raised By: {{ dispute.raisedBy }}</p>
        <p>Reason: {{ dispute.reason }}</p>
        <p>
          Evidence:
          <a :href="dispute.evidenceUrl" target="_blank">
            {{ dispute.evidenceUrl }}
          </a>
        </p>
        <!-- Display match details if they exist -->
        <div v-if="dispute.matchData">
          <h3>Match Details</h3>
          <p>Status: {{ dispute.matchData.result }}</p>
          <p>
            Score: {{ dispute.matchData.score.teamA }} -
            {{ dispute.matchData.score.teamB }}
          </p>
          <div style="display: flex; gap: 30px;">
            <p>TeamA: {{ dispute.matchData.teamAId }}</p>
            <p>TeamB: {{ dispute.matchData.teamBId }}</p>
          </div>
        </div>
        <div class="resolution-section" v-if="dispute.status.toLowerCase() === 'pending'">
          <label>Resolution Message:</label>
          <input v-model="dispute.resolution" placeholder="Enter resolution" class="input-field" />
          <!-- Let moderator update match result -->
          <label>Result:</label>
          <input v-model="dispute.matchData.result" placeholder="e.g., 'TeamA won'" class="input-field" />
          <!-- Inline Team Scores -->
          <div class="score-row">
            <div class="score-group">
              <label>Team A Score:</label>
              <input type="number" v-model="dispute.matchData.score.teamA" class="input-field" />
            </div>
            <div class="score-group">
              <label>Team B Score:</label>
              <input type="number" v-model="dispute.matchData.score.teamB" class="input-field" />
            </div>
          </div>
          <div class="action-buttons">
            <button @click="resolveDispute(dispute, 'resolved')" class="action-button resolve">
              Resolve
            </button>
            <button @click="resolveDispute(dispute, 'rejected')" class="action-button reject">
              Reject
            </button>
          </div>
        </div>
        <p v-else>
          Status: {{ dispute.status }} ({{ dispute.resolution }})
        </p>
      </div>
    </div>
    <div v-else>
      <p>No pending disputes found.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// In a real app, you might get moderatorId from auth or store
const moderatorId = "mods/modId"
const modAction = ref([])
const disputes = ref([])

async function fetchMatchDetails(matchId) {
  try {
    // If your match-service runs on port 5004:
    const response = await axios.get(`http://localhost:8010/match/${matchId}`);
    return response.data;
  } catch (error) {
    console.error("No match data found for ID:", matchId);
    return null;
  }
}

async function fetchPendingDisputes() {
  try {
    // 1. Fetch pending disputes from OutSystems
    const response = await axios.get("http://localhost:8010/dispute");
    let rawDisputes = response.data.Disputes || [];

    console.log("Fetched disputes:", rawDisputes);

    // 2. For each dispute, fetch match details in parallel
    const updatedDisputes = await Promise.all(
      rawDisputes.map(async (dispute) => {
        // Create a default matchData object
        dispute.matchData = {
          result: "",
          score: { teamA: 0, teamB: 0 },
        }
        if (dispute.matchId) {
          const matchData = await fetchMatchDetails(dispute.matchId)
          if (matchData) {
            // Add match data to the dispute
            dispute.matchData = matchData
          }
          // Ensure matchData has the fields we need
          if (!dispute.matchData.score) {
            dispute.matchData.score = { teamA: 0, teamB: 0 }
          }
        }
        return dispute;
      })
    );

    // 3. Set the updated disputes array
    // disputes.value = updatedDisputes;
    disputes.value = updatedDisputes.filter(d => d.status === "Pending");
  } catch (error) {
    console.error("Error fetching disputes:", error);
  }

    
}


async function resolveDispute(dispute, action) {
  try {
    const payload = {
      matchId: dispute.matchId,
      status: action,               // "resolved" or "rejected"
      result: dispute.matchData.result, //to be edited by front-end
      score: {
        teamA: dispute.matchData.score.teamA,
        teamB: dispute.matchData.score.teamB
      },
      raisedBy: dispute.raisedBy, // might need for notifications
    }
    const compositeUrl = "http://localhost:8010/dispute/resolve";
    const response = await axios.post(compositeUrl, payload)
    console.log("Dispute resolved:", response.data)
    // Refresh the list or update local state
    fetchPendingDisputes()
  } catch (error) {
    console.error("Error resolving dispute:", error)
  }
}

// On mount, fetch the pending disputes
fetchPendingDisputes()
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&display=swap');

.dispute-review {
  max-width: 900px;
  margin: 1rem auto;
  font-family: 'Oswald', sans-serif;
  padding: 1rem;
  border-radius: 10px;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

/* Refresh Button */
.refresh-container {
  text-align: center;
  margin-bottom: 1rem;
}

.refresh-button {
  background-color: rgba(39, 39, 215, 0.818);
  color: #fff;
  border: none;
  padding: 0.6rem 1rem;
  border-radius: 5px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.refresh-button:hover {
  background-color: rgb(16, 16, 156);
}

/* Disputes List */
.disputes-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.dispute-card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.dispute-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.dispute-card h3 {
  color: #222;
  margin-bottom: 0.3rem;
  font-size: 1.1rem;
}

.dispute-card p {
  color: #555;
  line-height: 1.4;
  margin: 0.3rem 0;
}

.dispute-card a {
  color: #1e90ff;
  text-decoration: none;
}

.dispute-card a:hover {
  text-decoration: underline;
}

/* Resolution Section */
.resolution-section {
  margin-top: 0.8rem;
  background: #f0f8ff;
  padding: 1.2rem;
  border-radius: 6px;
  border: 1px solid #cce7ff;
}

.resolution-section label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.2rem;
  color: #333;
  font-size: 0.9rem;
}

/* Input fields */
.input-field {
  width: 100%;
  padding: 0.4rem;
  margin-bottom: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.3s;
}

.input-field:focus {
  border-color: #1e90ff;
  outline: none;
}

/* Inline Score Fields */
.score-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.6rem;
}
.score-group {
  flex: 1;
}

/* Action Buttons */
.action-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 0.6rem;
}

.action-button {
  flex: 1;
  margin: 0 0.2rem;
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.action-button.resolve {
  background-color: #4caf50;
  color: #fff;
}

.action-button.resolve:hover {
  background-color: #45a049;
}

.action-button.reject {
  background-color: #f44336;
  color: #fff;
}

.action-button.reject:hover {
  background-color: #e53935;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .action-buttons {
    flex-direction: column;
  }
  .action-button {
    margin: 0.3rem 0;
  }
}
</style>

