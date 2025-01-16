import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("@/views/Dashboard.vue"),
  },
  // Jobs Route
  {
    path: "/jobs",
    name: "Jobs",
    component: () => import("@/views/JobsView.vue"),
  },
  // CVs Route
  {
    path: "/cvs",
    name: "CVs",
    component: () => import("@/views/CVsView.vue"),
  },
  // Applications Route
  {
    path: "/applications",
    name: "Applications",
    component: () => import("@/views/ApplicationsView.vue"),
  },
  // Analytics Route
  {
    path: "/analytics",
    name: "Analytics",
    component: () => import("@/views/AnalyticsView.vue"),
  },
  // Login Route
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/LoginView.vue"),
  },
  // Register Route
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/RegisterView.vue"),
  },
  // Profile Route
  {
    path: "/profile",
    name: "Profile",
    component: () => import("@/views/ProfileView.vue"),
  },
  // Catch-all for undefined routes, redirect to Dashboard
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
