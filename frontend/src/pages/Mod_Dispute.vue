<template>
    <div class="dispute-review">
        <h1>Dispute Review</h1>
        <div>
            <button @click="fetchPendingDisputes">Refresh Pending Disputes</button>
        </div>
        <div v-if="disputes.length" class="disputes-list">
            <div v-for="dispute in disputes" :key="dispute.disputeId" class="dispute-card">
                <h3>Dispute ID: {{ dispute.disputeId }}</h3>
                <p>Match ID: {{ dispute.matchId }}</p>
                <p>Raised By: {{ dispute.raisedBy }}</p>
                <p>Reason: {{ dispute.reason }}</p>
                <p>Evidence: <a :href="dispute.evidenceUrl" target="_blank">{{ dispute.evidenceUrl }}</a></p>
                <div class="resolution-section" v-if="dispute.status === 'pending'">
                    <label>Resolution Message:</label>
                    <input v-model="dispute.resolution" placeholder="Enter resolution" />
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
  
  const disputes = ref([])
  
  async function fetchPendingDisputes() {
    try {
      const response = await axios.get("http://localhost:5008/disputes?status=pending")
      disputes.value = response.data
    } catch (error) {
      console.error("Error fetching disputes:", error)
    }
  }
  
  async function resolveDispute(dispute, action) {
    try {
      const payload = {
        status: action,               // "resolved" or "rejected"
        resolution: dispute.resolution || "",
        moderatorId
      }
      await axios.put(`http://localhost:5008/dispute/${dispute.disputeId}`, payload)
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
  