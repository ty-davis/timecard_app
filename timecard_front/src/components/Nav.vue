<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();

</script>

<template>
  <nav>
    <RouterLink to="/">Home</RouterLink>
    <button v-if="auth.isLoggedIn" @click="auth.logout">Logout</button>
  </nav>
</template>
