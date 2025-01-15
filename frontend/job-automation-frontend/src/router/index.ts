import { createRouter, createWebHistory } from 'vue-router';
import Dashboard from '../views/Dashboard.vue';
import Jobs from '../views/Jobs.vue';

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/jobs', name: 'Jobs', component: Jobs },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
