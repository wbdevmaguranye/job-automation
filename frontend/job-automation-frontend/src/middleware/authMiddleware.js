// middleware/authMiddleware.js

import { useUserStore } from "@/stores/userStore";

export function authMiddleware(to, from, next) {
  const userStore = useUserStore();

  if (!userStore.isAuthenticated) {
    next("/login");
  } else {
    next();
  }
}
