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
        This is in the drawer.
      </Drawer>
      <RouterLink to="/" class="page-title">Timecard</RouterLink>
      <Button icon="pi pi-bars" @click="visible = !visible"/>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  padding: 8px 32px;
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
