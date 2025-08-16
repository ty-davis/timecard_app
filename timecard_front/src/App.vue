<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import Nav from '@/components/Nav.vue';

</script>

<template>
  <Nav/>
  <main>
    <RouterView/>
  </main>
</template>

<style scoped></style>
