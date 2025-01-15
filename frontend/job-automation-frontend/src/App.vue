<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

</script>

<template>
  <header>
    

    <div class="wrapper">
      <HelloWorld msg="You did it!" />

      <NavBar />
    </div>
  </header>

  <RouterView />
</template>

<style scoped>

</style>
