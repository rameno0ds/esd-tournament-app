<template>
  <div class="dispute-form">
    <h1>Submit Dispute</h1>
    <div class="form-section">
      <label>Match ID:</label>
      <input v-model="matchId" placeholder="by7mQposbRruQ9igYHIQ" />
    </div>
    <div class="form-section">
      <label>Reason:</label>
      <input v-model="reason" placeholder="Describe the issue" />
    </div>
    <div class="form-section">
      <label>Evidence URL:</label>
      <input v-model="evidenceUrl" placeholder="https://example.com/video.mp4" />
    </div>
    <button @click="submitDispute">Submit Dispute</button>

    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

// In a real app, you might get the playerId from auth or store
const playerId = "players/playerId"

const matchId = ref("")
const reason = ref("")
const evidenceUrl = ref("")
const message = ref("")

async function submitDispute() {
  try {
    const payload = {
      matchId: matchId.value,
      raisedBy: playerId,
      reason: reason.value,
      evidenceUrl: evidenceUrl.value
    }
    const response = await axios.post("http://localhost:5008/dispute", payload)
    message.value = response.data.message + " (ID: " + response.data.disputeId + ")"
    // Clear form
    matchId.value = ""
    reason.value = ""
    evidenceUrl.value = ""
  } catch (error) {
    console.error("Error submitting dispute:", error)
    message.value = "Failed to submit dispute."
  }
}
</script>

<style scoped>
.dispute-form {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
}
.form-section {
  margin-bottom: 1rem;
}
.message {
  margin-top: 1rem;
  color: green;
}
</style>

