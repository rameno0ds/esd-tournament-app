<template>
    <div class="submit-availability">
      <h1>Submit Availability</h1>
      <p>Please select the days/times you are available for Round {{ roundNumber }}.</p>
  
      <!-- Availability Form -->
      <form @submit.prevent="handleSubmit" class="availability-form">
        <!-- Example checkboxes for days of the week -->
        <label v-for="(day, index) in daysOfWeek" :key="index" class="day-label">
          <input
            type="checkbox"
            :value="day"
            v-model="selectedDays"
          />
          {{ day }}
        </label>
  
        <!-- Example timeslots (optional) -->
        <div class="time-slots">
          <label v-for="(slot, idx) in timeSlots" :key="idx" class="slot-label">
            <input
              type="checkbox"
              :value="slot"
              v-model="selectedSlots"
            />
            {{ slot }}
          </label>
        </div>
  
        <button type="submit">Submit Availability</button>
      </form>
  
      <!-- Confirmation Message -->
      <div v-if="confirmationMessage" class="confirmation">
        <p>{{ confirmationMessage }}</p>
        <router-link to="/dashboard">Back to Dashboard</router-link>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { onAuthStateChanged } from 'firebase/auth'
  import { auth, db } from '../firebase'
  import {
    collection,
    addDoc
  } from 'firebase/firestore'
  
  // Example round number (you might get this from route params or store)
  const roundNumber = 2
  
  const router = useRouter()
  const currentUser = ref(null)
  
  // Auth check
  onAuthStateChanged(auth, (user) => {
    if (!user) {
      router.push('/login')
    } else {
      currentUser.value = user
    }
  })
  
  // Example data for days of the week
  const daysOfWeek = [
    'Monday', 
    'Tuesday', 
    'Wednesday', 
    'Thursday', 
    'Friday', 
    'Saturday', 
    'Sunday'
  ]
  
  // Example timeslots
  const timeSlots = [
    'Morning (8am - 12pm)',
    'Afternoon (12pm - 4pm)',
    'Evening (4pm - 8pm)',
    'Night (8pm - 12am)'
  ]
  
  // Reactive arrays for selected days and times
  const selectedDays = ref([])
  const selectedSlots = ref([])
  
  // Confirmation message
  const confirmationMessage = ref('')
  
  // Handle form submission
  async function handleSubmit() {
    if (!currentUser.value) {
      alert('You must be logged in to submit availability.')
      return
    }
  
    try {
      // For demo, we store in a "schedules" collection
      // with fields: userId, round, days, times, etc.
      const schedulesRef = collection(db, 'schedules')
  
      await addDoc(schedulesRef, {
        userId: currentUser.value.uid,
        round: roundNumber,
        days: selectedDays.value,
        times: selectedSlots.value,
        submittedAt: new Date().toISOString()
      })
  
      confirmationMessage.value = `Availability for Round ${roundNumber} submitted successfully!`
      // Clear selections
      selectedDays.value = []
      selectedSlots.value = []
    } catch (error) {
      console.error('Error submitting availability:', error)
      alert('Failed to submit availability. Check console for details.')
    }
  }
  </script>
  
  <style scoped>
  .submit-availability {
    padding: 2rem;
    max-width: 800px;
    margin: 2rem auto;
    background-color: var(--color-background-soft);
    border: 1px solid var(--color-border);
    border-radius: 8px;
  }
  
  h1 {
    color: var(--color-heading);
    margin-bottom: 1rem;
  }
  
  p {
    color: var(--color-text);
    margin-bottom: 1rem;
  }
  
  .availability-form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .day-label,
  .slot-label {
    display: inline-block;
    margin-right: 1rem;
    color: var(--color-text);
  }
  
  button {
    width: fit-content;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    background: linear-gradient(90deg, #6a5af9, #9e6af8);
    color: #fff;
    font-weight: 500;
    cursor: pointer;
    transition: filter 0.2s ease;
  }
  
  button:hover {
    filter: brightness(1.1);
  }
  
  .confirmation {
    margin-top: 2rem;
    padding: 1rem;
    background-color: var(--color-background);
    border: 1px solid var(--color-border);
    border-radius: 6px;
    text-align: center;
  }
  </style>
  