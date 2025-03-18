<template>
  <div>
    <!-- Navbar is shown only if the user is logged in and the current route is not '/login' -->
    <nav v-if="user && $route.name !== 'login'">
      <router-link to="/login" v-if="!user">Login</router-link>
      <router-link to="/" v-if="user">Home</router-link>
      <router-link to="/tournament" v-if="user">Tournaments</router-link>
      <router-link to="/dispute" v-if="user">Disputes</router-link>
    </nav>
    
    <!-- Main content rendered by the route -->
    <router-view />
  </div>
</template>

<script>
import { getAuth } from "firebase/auth";  // Import Firebase Authentication

export default {
  setup() {
    const user = getAuth().currentUser; // Get the current user from Firebase Authentication

    return { user };
  }
};
</script>

<style scoped>
nav {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding: 10px;
  background: #eee;
}
</style>
