// router/index.js

import { createRouter, createWebHistory } from "vue-router";
import { authMiddleware } from "@/middleware/authMiddleware";

const routes = [
  {
    path: "/dashboard",
    name: "Dashboard",
    component: () => import("@/views/DashboardView.vue"),
    beforeEnter: authMiddleware,
  },
  {
    path: "/jobs",
    name: "Jobs",
    component: () => import("@/views/JobsView.vue"),
  },
  {
    path: "/cvs",
    name: "CVs",
    component: () => import("@/views/CVsView.vue"),
    beforeEnter: authMiddleware, 
  },
  {
    path: "/applications",
    name: "Applications",
    component: () => import("@/views/ApplicationsView.vue"),
    beforeEnter: authMiddleware, 
  },
  {
    path: "/analytics",
    name: "Analytics",
    component: () => import("@/views/AnalyticsView.vue"),
    beforeEnter: authMiddleware, 
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("@/views/LoginView.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("@/views/RegisterView.vue"),
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/dashboard",
  },
];

export default createRouter({
  history: createWebHistory(),
  routes,
});
