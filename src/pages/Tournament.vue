<template>
  <div>
    <h1>Tournaments</h1>
    <ul>
      <li v-for="tournament in tournaments" :key="tournament.id">
        <router-link :to="'/match/' + tournament.id">{{ tournament.name }}</router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import { db } from '@/firebase';
import { collection, getDocs } from 'firebase/firestore';

export default {
  data() {
    return {
      tournaments: []
    };
  },
  async created() {
    const querySnapshot = await getDocs(collection(db, 'tournament'));
    this.tournaments = querySnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
  }
};
</script>
