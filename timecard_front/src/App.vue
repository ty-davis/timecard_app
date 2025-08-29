<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import Nav from '@/components/Nav.vue';

</script>

<template>
  <ConfirmDialog></ConfirmDialog>
  <div class="main">
    <Nav/>
    <main>
      <RouterView/>
    </main>
  </div>
</template>

<style scoped>
.main {
  min-height: 100dvh;
  max-width: 768px;
  margin-left: auto;
  margin-right: auto;
  padding: 8px 32px;
}
</style>
