<template>
  <div id="app">
    <!-- Loader while waiting for Firebase Auth to resolve -->
    <div v-if="!isAuthResolved" class="loader">Loading...</div>
    <div v-else>
      <!-- NAVIGATION: depends on userRole and if user is logged in (showNavbar) -->
      <!-- Player Navbar -->
      <header v-if="userRole === 'player' && showNavbar" class="navbar">
        <div class="navbar-left">
          <router-link to="/" class="nav-link">Home</router-link>
          <router-link to="/teams" class="nav-link">Teams</router-link>
          <router-link to="/tournaments" class="nav-link">My Tournaments</router-link>
          <router-link to="/dispute" class="nav-link">Dispute</router-link>
        </div>

        <div class="navbar-right">
          <button class="icon-button" @click="openNotifications">
            <span class="material-icons">notifications</span>
          </button>
          <div class="profile-menu">
            <div class="profile-avatar" @click="toggleProfileDropdown">
              <template v-if="currentUser.value && currentUser.value.displayName">
                <span class="avatar-initial">
                  {{ currentUser.value.displayName.charAt(0).toUpperCase() }}
                </span>
              </template>
              <template v-else>
                <span class="material-icons">account_circle</span>
              </template>
            </div>
            <div v-if="showProfileDropdown" class="dropdown">
              <ul>
                <li @click="goToProfile">My Profile</li>
                <li @click="goToNotifications">Notifications</li>
                <li @click="goToSettings">Settings</li>
                <li @click="logout">Logout</li>
              </ul>
            </div>
          </div>
        </div>
      </header>

      <!-- Moderator Navbar -->
      <header v-else-if="userRole === 'moderator' && showNavbar" class="navbar moderator-nav">
        <div class="navbar-left">
          <router-link to="/moderator" class="nav-link">Home</router-link>
          <router-link to="/mod-disputes" class="nav-link">Disputes</router-link>
        </div>
        <div class="navbar-right">
          <button class="icon-button" @click="logout">
            <span class="material-icons">logout</span>
          </button>
        </div>
      </header>

      <!-- Main content from <router-view /> -->
      <router-view />
    </div>

    <!-- Role Toggle Buttons at bottom-left -->
    <div class="role-toggle">
      <button class="toggle-btn" :class="{ active: userRole === 'player' }" @click="setUserRole('player')">
        Player
      </button>
      <button class="toggle-btn" :class="{ active: userRole === 'moderator' }" @click="setUserRole('moderator')">
        Moderator
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { onAuthStateChanged, signOut } from 'firebase/auth'
import { auth } from './firebase'

// Reactive references
const currentUser = ref(null)
const isAuthResolved = ref(false)

// Track the user role: "player" or "moderator"
const userRole = ref('player') // default to "player" for the UI toggle

// Listen for auth changes
onAuthStateChanged(auth, (user) => {
  currentUser.value = user
  isAuthResolved.value = true
})

const route = useRoute()
const router = useRouter()

// Show the navbar if the user is logged in and not on /login or /register
const showNavbar = computed(() => {
  return currentUser.value && !['/login', '/register'].includes(route.path)
})

// Profile dropdown
const showProfileDropdown = ref(false)
function toggleProfileDropdown() {
  showProfileDropdown.value = !showProfileDropdown.value
}

// Handlers for dropdown menu
function goToProfile() {
  showProfileDropdown.value = false
  router.push('/profile')
}
function goToNotifications() {
  showProfileDropdown.value = false
  router.push('/notifications')
}
function goToSettings() {
  showProfileDropdown.value = false
  router.push('/settings')
}
async function logout() {
  try {
    await signOut(auth)
    showProfileDropdown.value = false
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}
function openNotifications() {
  router.push('/notifications')
}

// Toggle role and navigate to the appropriate home page
function setUserRole(role) {
  userRole.value = role
  if (role === 'player') {
    router.push('/') // Player home (Home.vue)
  } else if (role === 'moderator') {
    router.push('/moderator') // Moderator home (Moderator.vue)
  }
}
</script>

<style>
/* Basic global styling */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  min-height: 100vh;
  position: relative;
  margin: 0;
}

/* Loader styling while auth state is unresolved */
.loader {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  font-size: 1.5rem;
}

/* Navbar container */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: var(--color-background-soft);
  border-bottom: 1px solid var(--color-border);
}
.moderator-nav {
  background-color: #ffe5b4; /* sample moderator navbar color */
}

/* Left nav links */
.navbar-left {
  display: flex;
  gap: 1rem;
}
.nav-link {
  text-decoration: none;
  color: var(--color-heading);
  font-weight: 500;
}
.nav-link:hover {
  text-decoration: underline;
}

/* Right side icons */
.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.icon-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  font-size: 1.5rem;
  border-radius: 50%;
  transition: background-color 0.2s ease;
}
.icon-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

/* Profile menu styling */
.profile-menu {
  position: relative;
}
.profile-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background-color: #eee;
  cursor: pointer;
  overflow: hidden;
}
.avatar-initial {
  font-weight: bold;
  font-size: 1rem;
  color: #555;
}
.dropdown {
  position: absolute;
  top: 110%;
  right: 0;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  width: 200px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 0.5rem 0;
}
.dropdown ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.dropdown li {
  padding: 0.75rem 1rem;
  cursor: pointer;
  font-weight: 500;
  color: #333;
}
.dropdown li:hover {
  background-color: #f5f5f5;
}

/* Material icons styling */
.material-icons {
  font-family: 'Material Icons';
  font-style: normal;
  font-weight: normal;
  font-size: inherit;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  direction: ltr;
  -webkit-font-smoothing: antialiased;
}

/* Role Toggle at bottom-left */
.role-toggle {
  position: fixed;
  bottom: 1rem;
  left: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.toggle-btn {
  padding: 0.5rem 1rem;
  background: #ccc;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.toggle-btn.active {
  background: #6a5af9;
  color: #fff;
}
</style>
