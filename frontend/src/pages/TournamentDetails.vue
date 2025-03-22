<template>
    <div class="tournament-details">
      <h1>{{ tournamentName }}</h1>
      <!-- <h1>{{ tournamentId }}</h1> -->

      <!-- <p><strong>Tournament ID:</strong> {{ tournamentId }}</p> -->
      <p><strong>Tournament:</strong> {{ tournamentName }}</p>


      <!-- Filter dropdown -->
      <div class="filter-section">
        <label for="filterSelect">Filter matches:</label>
        <select id="filterSelect" v-model="selectedFilter">
          <option value="all">All matches</option>
          <option value="upcoming">Upcoming</option>
          <option value="completed">Completed</option>
        </select>
      </div>
  
      <!-- Matches grid/list -->
      <div class="matches-grid" v-if="matches.length">
        <div
          v-for="match in filteredMatches"
          :key="match.id"
          class="match-card"
        >
          <h2>Match ID: {{ match.id }}</h2>
          <p>Status: {{ match.status }}</p>
          <p>Teams: {{ match.teamA }} vs {{ match.teamB }}</p>
        </div>
      </div>
      <div v-else class="no-matches">
        <p>No matches found for this tournament.</p>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useRoute } from 'vue-router'
  import { db } from '../firebase'
  import { doc, getDoc, collection, query, where, getDocs } from 'firebase/firestore'
  
  const route = useRoute()
  const tournamentId = route.params.id  // The tournament's doc ID from the route
  const tournamentName = ref('Tournament Details')
  const matches = ref([])
  
  // For filtering matches
  const selectedFilter = ref('all')
  
  // On mount, load the tournament document and its matches
  onMounted(async () => {
    try {
      // Fetch the tournament document
      const tourneyRef = doc(db, 'tournaments', tournamentId)
      const tourneySnap = await getDoc(tourneyRef)
      if (tourneySnap.exists()) {
        const data = tourneySnap.data()
        tournamentName.value = data.tournamentName || `Tournament ${tournamentId}`
      }
  
      // Query matches from the top-level "matches" collection
      const matchesRef = collection(db, 'matches')
      // Ensure that match documents store tournamentId as a simple string, e.g., "BNck5GT9pQx8DVQ9x3sF"
      const q = query(matchesRef, where('tournamentId', '==', tournamentId))
      const snapshot = await getDocs(q)
      matches.value = snapshot.docs.map(docSnap => ({
        id: docSnap.id,
        ...docSnap.data()
      }))
    } catch (error) {
      console.error('Error loading tournament/matches:', error)
    }
  })
  
  // Compute filtered matches based on selectedFilter
  const filteredMatches = computed(() => {
    if (selectedFilter.value === 'all') return matches.value
    if (selectedFilter.value === 'upcoming') {
      return matches.value.filter(match => match.status === 'upcoming')
    }
    if (selectedFilter.value === 'completed') {
      return matches.value.filter(match => match.status === 'completed')
    }
    return matches.value
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
  
  .filter-section {
    margin: 1rem 0;
  }
  
  .matches-grid {
    display: grid;
    gap: 1rem;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    margin-top: 1rem;
  }
  
  .match-card {
    border: 1px solid #ddd;
    background-color: #fff;
    padding: 1rem;
    border-radius: 6px;
  }
  
  .no-matches {
    margin-top: 2rem;
    text-align: center;
    font-style: italic;
  }
  </style>
  