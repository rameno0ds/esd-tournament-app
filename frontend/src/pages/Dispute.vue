<template>
  <div class="dispute-form">
    <h1>Submit Dispute</h1>
    <div class="form-section">
      <label>Match ID:</label>
      <input v-model="matchId" placeholder="by7mQposbRruQ9igYHIQ" class="input-field" />
    </div>
    <div class="form-section">
      <label>Team ID:</label>
      <input v-model="teamId" placeholder="by7mQposbRruQ9igYHIQ" class="input-field" />
    </div>
    <div class="form-section">
      <label>Reason:</label>
      <input v-model="reason" placeholder="Describe the issue" class="input-field" />
    </div>
    <div class="form-section">
      <label>Evidence URL:</label>
      <input v-model="evidenceUrl" placeholder="https://example.com/video.mp4" class="input-field" />
    </div>
    <button @click="submitDispute" class="submit-button">Submit Dispute</button>
    <p v-if="message" class="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { getAuth, onAuthStateChanged } from 'firebase/auth'

const auth = getAuth()
const currentUser = ref(null)

// Listen for authentication state changes
onAuthStateChanged(auth, (user) => {
  currentUser.value = user
  console.log("Current user updated:", user)
})

const matchId = ref("")
const teamId = ref("")
const reason = ref("")
const evidenceUrl = ref("")
const message = ref("")

async function submitDispute() {
  try {
    const payload = {
      matchId: matchId.value,
      status: "pending",
      teamId: teamId.value,
      raisedBy: currentUser.value.uid,
      reason: reason.value,
      evidenceUrl: evidenceUrl.value
    }
    // Composite dispute service endpoint
    const compositeUrl = "http://localhost:5008/dispute/new";      
    const response = await axios.post(compositeUrl, payload)
    if (response.data.status === "success") {
      message.value = "Dispute submitted successfully!"
      console.log("Dispute submitted successfully:", response.data)
    } else {
      message.value = "Failed to submit dispute."
      console.log("Error in response:", response.data)
    }
    // Clear form fields
    matchId.value = "";
    teamId.value = "";
    reason.value = "";
    evidenceUrl.value = "";
  } catch (error) {
    console.error("Error submitting dispute:", error)
    message.value = "Failed to submit dispute."
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600&display=swap');

.dispute-form {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1.5rem;
  background: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  font-family: 'Oswald', sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 1.5rem;
  font-size: 1.75rem;
}

.form-section {
  margin-bottom: 1rem;
}

.form-section label {
  display: block;
  font-weight: bold;
  margin-bottom: 0.3rem;
  color: #333;
  font-size: 1rem;
}

.input-field {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
  transition: border-color 0.3s;
}

.input-field:focus {
  border-color: #1e90ff;
  outline: none;
}

.submit-button {
  width: 100%;
  padding: 0.75rem;
  background-color: #4caf50;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover {
  background-color: #45a049;
}

.message {
  margin-top: 1rem;
  text-align: center;
  font-size: 0.95rem;
  color: green;
}
</style>

