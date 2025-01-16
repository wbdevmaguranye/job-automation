<template>
    <b-container class="d-flex justify-content-center align-items-center vh-100">
      <b-card class="text-center p-4 custom-card">
        <h2 class="text-success">Register</h2>
        <b-form @submit.prevent="onRegister">
          <b-form-group label="Name" label-for="name-input">
            <b-form-input
              id="name-input"
              v-model="name"
              placeholder="Enter your name"
              class="custom-input"
              required
            ></b-form-input>
          </b-form-group>
          <b-form-group label="Email" label-for="email-input">
            <b-form-input
              id="email-input"
              v-model="email"
              type="email"
              placeholder="Enter your email"
              class="custom-input"
              required
            ></b-form-input>
          </b-form-group>
          <b-form-group label="Password" label-for="password-input">
            <b-form-input
              id="password-input"
              v-model="password"
              type="password"
              placeholder="Enter your password"
              class="custom-input"
              required
            ></b-form-input>
          </b-form-group>
          <b-button type="submit" variant="success" block>Register</b-button>
        </b-form>
        <p class="mt-3">
          Already have an account? <router-link to="/login" class="text-success">Login</router-link>
        </p>
      </b-card>
    </b-container>
  </template>
  
  <script setup>
  import { ref } from "vue";
  import { useUserStore } from "@/stores/userStore";
  import { useRouter } from "vue-router";
  
  const name = ref("");
  const email = ref("");
  const password = ref("");
  const userStore = useUserStore();
  const router = useRouter();
  
  const onRegister = async () => {
    try {
      await userStore.register(name.value, email.value, password.value);
      router.push("/login");
    } catch (error) {
      console.error("Registration failed:", error);
    }
  };
  </script>
  
  <style scoped>
  .custom-card {
    max-width: 400px;
    border: 1px solid #28a745;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }
  
  .custom-input {
    border: 1px solid #28a745;
    border-radius: 5px;
  }
  
  h2 {
    margin-bottom: 20px;
  }
  </style>
  