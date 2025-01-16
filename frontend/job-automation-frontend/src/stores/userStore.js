// stores/userStore.js
import { defineStore } from "pinia";
import { useDataStore } from "./dataStore";

export const useUserStore = defineStore("user", {
  state: () => ({
    user: null,
    token: localStorage.getItem("token") || null,
  }),
  actions: {
    async register(name, email, password) {
      const dataStore = useDataStore();
      const response = await dataStore.postData("/register", { name, email, password });

      if (response.success) {
        alert(response.data.message);
      } else {
        console.error("Registration error:", response.data.message);
      }
    },

    async login(email, password) {
      const dataStore = useDataStore();
      const response = await dataStore.postData("/login", { email, password });

      if (response.success) {
        this.token = response.data.access_token;
        localStorage.setItem("token", this.token);
        await this.fetchUserProfile();
      } else {
        console.error("Login error:", response.data.message);
      }
    },

    async fetchUserProfile() {
      const dataStore = useDataStore();
      const response = await dataStore.getData('/profile');
    
      if (response.success) {
        this.user = response.data; // Set user data
        console.log(response.data)
      } else {
        console.error('Fetch profile error:', response.data.message);
        if (response.status === 401) {
          this.logout(); // Clear user state if unauthorized
        }
      }
    },
    
    logout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem("token");
    },
  },
  getters: {
    isAuthenticated(state) {
      return !!state.token;
    },
  },
});
