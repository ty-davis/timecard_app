<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useJiraStore } from '@/stores/jira';
import Drawer from 'primevue/drawer';

const auth = useAuthStore();
const jiraStore = useJiraStore();

const visible = ref(false);

const closeDrawer = () => { visible.value = false };

</script>

<template>
  <nav>
    <div class="navbar flex items-baseline sm:mb-2">
      <Drawer v-model:visible="visible" header="Menu" position="right" class="sm:hidden">
        <div class="flex flex-col gap-3">
          <RouterLink v-if="auth.isLoggedIn" to="/report" @click="closeDrawer">Report</RouterLink>
          <RouterLink v-if="auth.isLoggedIn" to="/settings/jira" @click="closeDrawer">
            JIRA Settings
            <i v-if="jiraStore.hasActiveConnection" class="pi pi-check-circle" style="color: var(--green-500); margin-left: 4px;"></i>
          </RouterLink>
          <Button v-if="auth.isLoggedIn" @click="auth.logout">Logout</Button>
        </div>
      </Drawer>
      <RouterLink to="/" class="page-title">Timecard</RouterLink>
      <div class="hidden sm:flex gap-2">
        <Button text><RouterLink v-if="auth.isLoggedIn" to="/report">Report</RouterLink></Button>
        <Button text>
          <RouterLink v-if="auth.isLoggedIn" to="/settings/jira" class="jira-link">
            JIRA
            <i v-if="jiraStore.hasActiveConnection" class="pi pi-check-circle" style="color: var(--green-500); margin-left: 4px;"></i>
          </RouterLink>
        </Button>
        <Button v-if="auth.isLoggedIn" @click="auth.logout">Logout</Button>
      </div>
      <div class="block sm:hidden">
        <Button icon="pi pi-bars" @click="visible = !visible" link/>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
}
.page-title {
  font-size: xx-large;
  font-weight: 700;
  text-decoration: none;
  color: inherit;
}
.jira-link {
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
