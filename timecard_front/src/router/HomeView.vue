<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import TimecardForm from '@/components/TimecardForm.vue';
import type { TimeRecord, RecordAttribute } from '@/types';
import { toLocalDateTimeString } from '@/utils/timeUtils';

const auth = useAuthStore();
const recentRecords = ref<TimeRecord[]>([]);
const openRecords = ref<TimeRecord[]>([]);
const recordAttributes = ref<RecordAttribute[]>([]);
const newRecord = ref<TimeRecord>({
  id: null,
  domain_id: null,
  category_id: null,
  title_id: null,
  timein: null,
  timeout: null
});

const getTimeRecords = async () => {
  try {
    const response = await axios.get('/api/timerecords');
    recentRecords.value = response.data;
    openRecords.value = response.data.filter(r => r.timeout === null);
  } catch (error) {
    console.error('Request failed:', error.response?.data);

    if (error.response?.status === 401) {
      auth.logout();
    }
  }
}

const getRecordAttributes = async () => {
  try {
    const response = await axios.get('/api/recordattributes');
    recordAttributes.value = response.data;
  } catch (error) {
    console.error('Request failed:', error.response?.data);
  }
}

const handleSaveRecord = async (updatedRecord: TimeRecord) => {
  try {
    const method = updatedRecord.id ? 'put' : 'post';
    const url = updatedRecord.id ? `/api/timerecords/${updatedRecord.id}` : '/api/timerecords';
    console.log(updatedRecord);
    const response = await axios[method](url, updatedRecord);
    
    console.log('Record saved successfully:', response.data);
    
    // Refresh the time records to show updated data
    await getTimeRecords();
    
  } catch (error) {
    console.error('Failed to save record:', error.response?.data);
    
    if (error.response?.status === 401) {
      auth.logout();
    }
  }
};


const populateNewRecordInfo = () => {
  newRecord.value.domain_id = 1;
  newRecord.value.category_id = 2;
  newRecord.value.title_id = 3;

  newRecord.value.timein = toLocalDateTimeString(new Date());
}

const timeDifference = (record: TimeRecord) => {
  if (!(record.timein && record.timeout)) {
    return '';
  }
  let diff = Math.abs(new Date(record.timein) - new Date(record.timeout));
  diff = diff / 1000;
  const hours = Math.floor(diff / 3600);
  if (hours) { diff = diff - hours * 3600; }

  const minutes = Math.floor(diff / 60);
  if (minutes) { diff = diff - minutes * 60 }

  return `${hours}:${minutes}:${diff}`
}

watch(recordAttributes, (newVal) => {
  if (newVal && newVal.length > 0) {
    nextTick(() => {
      populateNewRecordInfo();
    });
  }
});

onMounted(async () => {
  if (auth.isLoggedIn) {
    await getRecordAttributes();
    await getTimeRecords();

  }
})
</script>

<template>
  <div class="content">
    <div v-if="auth.isLoggedIn">
      <!-- TODO: maybe use Panel -->
      <Panel class="main-card" header="New record" toggleable :collapsed="openRecords.length > 0">
        <TimecardForm
          :recordAttributes="recordAttributes"
          :timeRecord="newRecord"
          @save-record="handleSaveRecord"
        />
      </Panel>

      <Panel class="main-card" :header="`Open timecard${ openRecords.length > 1 ? 's' : ''}`">
        <template v-for="openRecord in openRecords">
          <TimecardForm
            :recordAttributes="recordAttributes"
            :timeRecord="openRecord"
            @save-record="handleSaveRecord"
          />
        </template>
      </Panel>

      <Panel class="main-card" header="History">
        <template v-for="record in recentRecords">
          <div>
            {{ recordAttributes.find(ra => ra.id === record.domain_id)?.name }} -
            {{ recordAttributes.find(ra => ra.id === record.category_id)?.name }} -
            {{ recordAttributes.find(ra => ra.id === record.title_id)?.name }}
            {{ timeDifference(record) }}
          </div>
        </template>
      </Panel>
    </div>
    <div v-else>
      <Card>
        <template #title>
          You are not logged in 
        </template>
        <template #content>
          <RouterLink to="/login">Login</RouterLink> or <RouterLink to="/register">Create an Account</RouterLink>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.content {
  margin-top: 1rem;
}
.main-card {
  margin-top: 1rem;
}
</style>
