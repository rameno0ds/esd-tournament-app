import { createRouter, createWebHistory } from "vue-router";
import Home from "@/pages/Home.vue";
import Tournament from "@/pages/Tournament.vue";
import Match from "@/pages/Match.vue";
import Dispute from "@/pages/Dispute.vue";

const routes = [
  { path: "/", component: Home },
  { path: "/tournament", component: Tournament },
  { path: "/match/:id", component: Match },
  { path: "/dispute", component: Dispute },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;