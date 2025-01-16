<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import Analytics from "@/components/Analytics.vue";
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
