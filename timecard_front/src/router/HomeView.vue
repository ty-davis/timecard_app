<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const recentRecords = ref([]);

onMounted(async () => {
  const token = localStorage.getItem('jwt');

  if (token) {
    // Decode JWT payload to inspect it (without verification)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    
    try {
      const response = await axios.get('/api/timerecords');
      recentRecords.value = response.data;
    } catch (error) {
      console.error('Request failed:', error.response?.data);
    }
  }
})
</script>



<template>
  This is the home view.
  <template v-for="record in recentRecords">
    <div>
      {{ record.domain }} - {{ record.category }} - {{ record.title }}
    </div>
  </template>
</template>
