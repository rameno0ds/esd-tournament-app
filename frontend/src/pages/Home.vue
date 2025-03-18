<template>
  <div>
      <nav>
        <router-link to="/" v-if="user">Home</router-link>
        <router-link to="/tournament" v-if="user">Tournaments</router-link>
        <router-link to="/dispute" v-if="user">Disputes</router-link>
      </nav>
      <router-view />
  </div>
  <div>
    <h2>Welcome to the Home Page!</h2>
    <p>This is the content of the home page, shown after login.</p>
    <!-- Add additional content for the home page -->
  </div>
</template>

<script>
import { getAuth } from "firebase/auth";  // Import Firebase Authentication

export default {
  name: "Home",
  // Home page-specific logic can go here
  setup() {
    const user = getAuth().currentUser; // Get the current user from Firebase Authentication

    return { user };
  }
  
};
</script>

<style scoped>
/* Home page specific styling */
</style>
