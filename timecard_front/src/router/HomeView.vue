<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const recentRecords = ref([]);

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      const response = await axios.get('/api/timerecords');
      recentRecords.value = response.data;
    } catch (error) {
      console.error('Request failed:', error.response?.data);

      if (error.response?.status === 401) {
        auth.logout();
      }
    }
  }
})
</script>



<template>
  This is the home view.
  <div v-if="auth.isLoggedIn">
    <template v-for="record in recentRecords">
      <div>
        {{ record.domain }} - {{ record.category }} - {{ record.title }}
      </div>
    </template>
  </div>
  <div v-else>
    You are not logged in. <RouterLink to="/login">Login</RouterLink> or <RouterLink to="/register">Create an Account</RouterLink>
  </div>
</template>
