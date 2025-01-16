<template>
  <b-navbar toggleable="lg" type="light" class="mb-4 bg-success text-white">
    <!-- Job Portal Brand -->
    <b-navbar-brand href="#" class="custom-padding text-white">
       Portal
    </b-navbar-brand>

    <!-- Navbar Toggle for small screens -->
    <b-navbar-toggle target="nav-collapse" class="mr-3"></b-navbar-toggle>

    <!-- Collapsible Navbar -->
    <b-collapse id="nav-collapse" is-nav>
      <!-- Left Navigation Links -->
      <b-navbar-nav>
        <b-nav-item href="/" class="text-white">Dashboard</b-nav-item>
        <b-nav-item href="/jobs" class="text-white">Jobs</b-nav-item>
        <b-nav-item href="/analytics">Job Analytics</b-nav-item>
        <b-nav-item href="/cvs" class="text-white">CVs</b-nav-item>
        <b-nav-item href="/applications" class="text-white">Applications</b-nav-item>
    
      </b-navbar-nav>

  <!-- Right "Account" Dropdown -->
  <b-navbar-nav class="ml-auto custom-padding2">
      <b-nav-item-dropdown text="Account" right>
        <!-- <b-dropdown-item to="/profile" v-if="isAuthenticated">Profile</b-dropdown-item> -->
<b-dropdown-item to="/register" v-if="!isAuthenticated">Register</b-dropdown-item>
<b-dropdown-item to="/login" v-if="!isAuthenticated">Login</b-dropdown-item>
<b-dropdown-item @click="logout" v-if="isAuthenticated">Logout</b-dropdown-item>

      </b-nav-item-dropdown>
    </b-navbar-nav>
    </b-collapse>
  </b-navbar>
</template>

<script setup>
import { computed } from "vue";
import { useUserStore } from "@/stores/userStore";

const userStore = useUserStore();
const isAuthenticated = computed(() => userStore.isAuthenticated);
const logout = () => userStore.logout();
</script>

<style scoped>

.bg-success {
  background-color: #198754 !important; 
}
.custom-padding {
padding-left: 4rem; 
}
.custom-padding2 {
padding-right: 4rem; 
}
.text-white {
  color: white !important; 
}

.pl-3 {
  padding-left: 1rem !important; 
}

.ml-auto {
  margin-left: auto !important; /* Push Account dropdown to the far right */
}


.b-nav-item-dropdown button {
  color: white !important;
}
.b-nav-item-dropdown button:hover {
  color: #d4edda !important; 
}


.b-navbar-nav a {
  color: white !important;
}
.b-navbar-nav a:hover {
  color: #d4edda !important; 
}
</style>
