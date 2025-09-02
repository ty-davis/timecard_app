<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '@/stores/auth';
import Drawer from 'primevue/drawer';

const auth = useAuthStore();

const visible = ref(false);

</script>

<template>
  <nav>
    <div class="navbar">
      <Drawer v-model:visible="visible" header="Menu" position="right">
        <div class="flex flex-col gap-3">
          <RouterLink v-if="auth.isLoggedIn" to="/report">Report</RouterLink>
          <Button v-if="auth.isLoggedIn" @click="auth.logout">Logout</Button>
        </div>
      </Drawer>
      <RouterLink to="/" class="page-title">Timecard</RouterLink>
      <Button icon="pi pi-bars" @click="visible = !visible" link/>
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
</style>
