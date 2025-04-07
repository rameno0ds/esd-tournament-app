<template>
  <div class="dispute-review">
    <h1 class="header">Dispute Review</h1>
    <button class="refresh-btn" @click="fetchPendingDisputes">Refresh Disputes</button>

    <transition-group name="fade" tag="div" class="list">
      <div v-for="dispute in disputes" :key="dispute.matchId" class="card">
        <div class="card-top">
          <div class="match-id">Match #{{ dispute.matchId }}</div>
          <div :class="['status', dispute.status.toLowerCase()]">{{ dispute.status }}</div>
        </div>
        <div class="card-body">
          <p><strong>Raised By:</strong> {{ dispute.raisedBy }}</p>
          <p><strong>Reason:</strong> {{ dispute.reason }}</p>
          <p><strong>Evidence:</strong> <a :href="dispute.evidenceUrl" target="_blank">{{ dispute.evidenceUrl }}</a></p>
          <div v-if="dispute.status === 'Pending'" class="actions">
            <input v-model="dispute.resolution" placeholder="Enter resolution message" class="resolution-input" />
            <button class="btn resolve" @click="resolveDispute(dispute, 'resolved')">Resolve</button>
            <button class="btn reject" @click="resolveDispute(dispute, 'rejected')">Reject</button>
          </div>
        </div>
      </div>
    </transition-group>

    <p v-if="!disputes.length" class="no-data">No pending disputes found.</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const moderatorId = "mods/modId"
const disputes = ref([])

async function fetchPendingDisputes() {
  try {
    const response = await axios.get(
      "https://personal-xxidmbev.outsystemscloud.com/disputeAPI/rest/v1/disputes?status=pending"
    )
    disputes.value = (response.data.Disputes || []).map(d => ({ ...d, resolution: "" }))
  } catch (error) {
    console.error("Error fetching disputes:", error)
  }
}

async function resolveDispute(dispute, action) {
  try {
    const payload = {
      matchId: dispute.matchId,
      status: action,
      resolution: dispute.resolution || "",
    }
    await axios.put(
      "https://personal-xxidmbev.outsystemscloud.com/disputeAPI/rest/v1/disputes/",
      payload
    )
    fetchPendingDisputes()
  } catch (error) {
    console.error("Error resolving dispute:", error)
  }
}

// Initial fetch
fetchPendingDisputes()
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

:root {
  --bg: #f4f7fa;
  --card-bg: #ffffff;
  --accent: #007bff;
  --accent-hover: #0056b3;
  --text: #333333;
  --border: #e0e0e0;
  --neon: #00dffc;
}

.dispute-review {
  font-family: 'Roboto', sans-serif;
  background: var(--bg);
  min-height: 100vh;
  padding: 2rem;
  color: var(--text);
}

.header {
  text-align: center;
  color: var(--accent);
  font-size: 2.5rem;
  margin-bottom: 1rem;
  text-shadow: 0 0 8px var(--neon);
}

.refresh-btn {
  display: block;
  margin: 0 auto 1.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s, box-shadow 0.3s;
}
.refresh-btn:hover {
  background: var(--accent-hover);
  box-shadow: 0 0 10px var(--neon);
}

.list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1rem;
}

.card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: visible; /* allow buttons to show fully */
  transition: transform 0.3s, box-shadow 0.3s;
}
.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: linear-gradient(90deg, var(--accent), var(--neon));
  color: #fff;
}
.match-id {
  font-weight: 700;
}
.status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
  font-size: 0.75rem;
}
.status.pending {
  background: #ffc107;
  color: #333;
}
.status.resolved {
  background: #28a745;
}
.status.rejected {
  background: #dc3545;
}

.card-body {
  padding: 1rem;
}

.actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: nowrap; /* keep buttons on same line */
}

.resolution-input {
  flex: 1 1 auto;
  min-width: 0;
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 4px;
}

.btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  color: #fff;
  cursor: pointer;
  white-space: nowrap;
  transition: box-shadow 0.3s;
}
.btn.resolve {
  background: #28a745;
}
.btn.resolve:hover {
  box-shadow: 0 0 8px #28a745;
}
.btn.reject {
  background: #dc3545;
}
.btn.reject:hover {
  box-shadow: 0 0 8px #dc3545;
}

.no-data {
  text-align: center;
  font-size: 1.25rem;
  margin-top: 2rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.5s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>