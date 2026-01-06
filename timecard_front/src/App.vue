<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import Nav from '@/components/Nav.vue';
import { computed } from 'vue';

const isPopupWindow = computed(() => window.opener !== null);
</script>

<template>
  <ConfirmDialog></ConfirmDialog>
  <div class="main" :class="{ 'popup-mode': isPopupWindow }">
    <Nav v-if="$route.path !== '/clock'"/>
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

.popup-mode {
  padding: 4px 8px;
  max-width: none;
}
</style>
