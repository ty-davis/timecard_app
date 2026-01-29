<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import JiraConnectionSetup from '@/components/JiraConnectionSetup.vue';

const auth = useAuthStore();
const router = useRouter();

onMounted(() => {
  if (!auth.isLoggedIn) {
    router.push('/login');
  }
});
</script>

<template>
  <div class="settings-container">
    <div class="settings-content">
      <h1>JIRA Integration Settings</h1>
      <p class="description">
        Connect your JIRA account to automatically sync time records as worklogs.
      </p>
      
      <JiraConnectionSetup />
    </div>
  </div>
</template>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings-content {
  background: var(--surface-card);
  border-radius: 8px;
  padding: 24px;
}

h1 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 1.75rem;
  font-weight: 600;
}

.description {
  color: var(--text-color-secondary);
  margin-bottom: 24px;
  font-size: 0.95rem;
}
</style>
