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
 
      } else {
        console.error("Registration error:", response.data.message);
      }
    },

    async login(email, password) {
      const dataStore = useDataStore();
      try {
        const response = await dataStore.postData("/login", { email, password });
    
        if (response.success) {
          this.token = response.data.access_token;
          localStorage.setItem("token", this.token);
        } else {
          // Throw an error to propagate it to the component
          throw new Error(response.data.message);
        }
      } catch (error) {
        
        throw error;
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