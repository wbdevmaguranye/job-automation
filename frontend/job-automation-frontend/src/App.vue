<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useUserStore } from "@/stores/userStore";

</script>

<template>
  <header>
    <NavBar />
  </header>

  <main>
    <RouterView />
  </main>
</template>


<style scoped>

</style>
