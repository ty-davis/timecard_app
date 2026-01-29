<script setup lang="ts">
import { useAuthStore } from '@/stores/auth';
import { useJiraStore } from '@/stores/jira';
import Nav from '@/components/Nav.vue';
import { computed, watch, onMounted } from 'vue';

const authStore = useAuthStore();
const jiraStore = useJiraStore();

const isPopupWindow = computed(() => window.opener !== null);

// Load JIRA connections when logged in
const loadJiraConnections = async () => {
  if (authStore.isLoggedIn) {
    try {
      await jiraStore.getConnections();
    } catch (error) {
      // Silently fail - user can still use the app
      console.error('Failed to load JIRA connections:', error);
    }
  }
};

// Load on mount if already logged in
onMounted(loadJiraConnections);

// Watch for login state changes
watch(() => authStore.isLoggedIn, (isLoggedIn) => {
  if (isLoggedIn) {
    loadJiraConnections();
  }
});
</script>

<template>
  <ConfirmDialog></ConfirmDialog>
  <Toast />
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
