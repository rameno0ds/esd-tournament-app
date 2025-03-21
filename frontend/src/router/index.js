import { createRouter, createWebHistory } from "vue-router";
import Home from "@/pages/Home.vue";
import Tournament from "@/pages/Tournament.vue";
import Match from "@/pages/Match.vue";
import Dispute from "@/pages/Dispute.vue";
import Login from "@/pages/Login.vue";
import Register from "@/pages/Register.vue";
import Schedule from "@/pages/Schedule.vue";
import Teams from '@/pages/Teams.vue';
import TournamentDetails from '@/pages/TournamentDetails.vue';
import { getAuth } from 'firebase/auth'; // Import Firebase Authentication


const routes = [
  {
    path: "/login",
    name: "login",
    component: Login,
  },
  {
    path: "/",
    name: "home", // Ensure this name matches the one you're using in the login redirection
    component: Home,
    meta: { requiresAuth: true }, // Make sure the Home route is protected
  },
  { path: "/tournaments", component: Tournament, meta: { requiresAuth: true } },
  { path: "/match/:id", component: Match, meta: { requiresAuth: true } },
  { path: "/dispute", component: Dispute, meta: { requiresAuth: true } },
  { path: "/schedule", component: Schedule, meta: { requiresAuth: true } },
  { path: '/teams', name: 'Teams', component: Teams, meta: { requiresAuth: true } }, 
  { path: '/tournament/:id', name: 'TournamentDetails', component: TournamentDetails, meta: { requiresAuth: true } }, 

  { path: "/register", component: Register },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});
// Route Guard to check if the user is logged in before accessing protected routes
router.beforeEach((to, from, next) => {
  const user = getAuth().currentUser;  // Get the current user from Firebase Authentication
  if (to.meta.requiresAuth && !user) {
    // If the route requires authentication and the user is not logged in, redirect to login
    next({ name: 'login' });
  } else {
    next(); // Allow navigation
  }
});
export default router;