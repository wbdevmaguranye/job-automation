import { useUserStore } from "@/stores/userStore";

export default function authMiddleware(redirectCallback) {
  const userStore = useUserStore();

  if (!userStore.isAuthenticated) {
    // Call the redirect callback to navigate to login
    redirectCallback("/login");
  } else {
    // Call the redirect callback with no arguments to proceed
    redirectCallback();
  }
}
