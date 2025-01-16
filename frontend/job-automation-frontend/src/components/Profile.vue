<template>
    <b-container>
      <h1>Profile</h1>
      <div v-if="userStore.user">
        <p><strong>Name:</strong> {{ userStore.user.name }}</p>
        <p><strong>Email:</strong> {{ userStore.user.email }}</p>
        <b-button @click="logout" variant="danger">Logout</b-button>
      </div>
      <div v-else>
        <p>Please log in to view your profile.</p>
      </div>
    </b-container>
  </template>
  
  <script setup>
  import { useUserStore } from '@/stores/userStore';
  
  const userStore = useUserStore();
  const logout = () => userStore.logout();
  </script>
  