<template>
    <div class="dispute-review">
        <h1>Dispute Review</h1>
        <div>
            <button @click="fetchPendingDisputes">Refresh Pending Disputes</button>
        </div>
        <div v-if="disputes.length" class="disputes-list">
            <div v-for="dispute in disputes" :key="dispute.matchId" class="dispute-card">
                
                <h3>Match ID: {{ dispute.matchId }}</h3>
                <p>Raised By: {{ dispute.raisedBy }}</p>
                <p>Reason: {{ dispute.reason }}</p>
                <p>Evidence: <a :href="dispute.evidenceUrl" target="_blank">{{ dispute.evidenceUrl }}</a></p>
                  <!-- Display match details if they exist -->
                <div v-if="dispute.matchData">
                  <h3>Match Details</h3>
                  <p>Status: {{ dispute.matchData.result }}</p>
                  <p>Score: {{ dispute.matchData.score.teamA }} - {{ dispute.matchData.score.teamB }}</p>
                  <p>TeamA: {{ dispute.matchData.teamAId }}</p>
                  <p>TeamB: {{ dispute.matchData.teamBId }}</p>
                </div>
                <div class="resolution-section" v-if="dispute.status === 'Pending'">
                    <label>Resolution Message:</label>
                    <input v-model="dispute.resolution" placeholder="Enter resolution" />
                      <!-- New: Let moderator update match result -->
                    <label>Result:</label>
                    <input v-model="dispute.matchData.result" placeholder="e.g., 'TeamA won'" />

                    <!-- New: Let moderator update the team scores -->
                    <label>Team A Score:</label>
                    <input type="number" v-model="dispute.matchData.score.teamA" />

                    <label>Team B Score:</label>
                    <input type="number" v-model="dispute.matchData.score.teamB" />
                    <button @click="resolveDispute(dispute, 'resolved')">Resolve</button>
                    <button @click="resolveDispute(dispute, 'rejected')">Reject</button>
                </div>
                <p v-else>Status: {{ dispute.status }} ({{ dispute.resolution }})</p>
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
      const response = await axios.get(`http://localhost:5004/match/${matchId}`);
      return response.data;
    } catch (error) {
      // console.error("Error fetching match details:", error);
      console.error("No match data found for ID:", matchId);
      return null;
    }
  }

  async function fetchPendingDisputes() {
  try {
    // 1. Fetch pending disputes from OutSystems
    const response = await axios.get(
      "https://personal-xxidmbev.outsystemscloud.com/disputeAPI/rest/v1/disputes?status=pending"
    );
    let rawDisputes = response.data.Disputes || [];

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
    disputes.value = updatedDisputes;
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
        raisedBy: dispute.raisedBy,  // might need for notifications
      }
      const compositeUrl = "http://localhost:5008/dispute/resolve";
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
  .dispute-review {
    max-width: 800px;
    margin: 2rem auto;
  }
  .disputes-list {
    margin-top: 1rem;
  }
  .dispute-card {
    border: 1px solid #ddd;
    background-color: #fff;
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
  }
  .resolution-section {
    margin-top: 0.5rem;
  }
  
</style>
  