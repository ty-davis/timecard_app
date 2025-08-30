<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/stores/auth';
import TimecardForm from '@/components/TimecardForm.vue';
import LittleRecord from '@/components/LittleRecord.vue';
import type { TimeRecord, RecordAttribute } from '@/types';
import { toLocalDateTimeString, showTimeDifference } from '@/utils/timeUtils';
import { useConfirm } from 'primevue/useconfirm';

const confirm = useConfirm();

const auth = useAuthStore();
const isFirstLoading = ref(true);
const recentRecords = ref<TimeRecord[]>([]);
const openRecords = ref<TimeRecord[]>([]);
const recordAttributes = ref<RecordAttribute[]>([]);
const newRecord = ref<TimeRecord>({
  id: undefined,
  domain_id: '',
  category_id: '',
  title_id: '',
  timein: new Date(),
  timeout: null
});

const getRecordAttributes = async () => {
  try {
    const response = await axios.get('/api/recordattributes');
    recordAttributes.value = response.data;
  } catch (error: any) {
    console.error('Request failed:', error.response?.data);
  }
}

const getTimeRecords = async () => {
  try {
    const response = await axios.get('/api/timerecords');
    recentRecords.value = response.data;
    openRecords.value = response.data.filter((r: TimeRecord) => r.timeout === null);
  } catch (error: any) {
    console.error('Request failed:', error.response?.data);

    if (error.response?.status === 401) {
      auth.logout();
    }
  }
}

const handleSaveRecord = async (updatedRecord: TimeRecord) => {
  console.log(updatedRecord);
  try {
    const method = updatedRecord.id ? 'put' : 'post';
    const url = updatedRecord.id ? `/api/timerecords/${updatedRecord.id}` : '/api/timerecords';
    const response = await axios[method](url, updatedRecord);
    
    
    // Refresh the time records to show updated data
    await getRecordAttributes();
    await getTimeRecords();
    newRecord.value = {
      id: undefined,
      domain_id: '',
      category_id: '',
      title_id: '',
      timein: new Date(),
      timeout: null
    };
    
  } catch (error: any) {
    console.error('Failed to save record:', error.response?.data);
    
    if (error.response?.status === 401) {
      auth.logout();
    }
  }
};

const deleteTimeRecord = async (recordToDelete: TimeRecord) => {
  try {
    console.log("deleting:", recordToDelete);
    await axios.delete(`/api/timerecords/${recordToDelete.id}`);
    
    await getTimeRecords();
  } catch (error: any) {
    console.error('Failed to delete record:', error.response?.data);

    if (error.response?.status === 401) {
      auth.logout();
    }
  }
}

const deleteConfirm = (record: TimeRecord) => {
  confirm.require({
    message: 'Do you want to delete this record?',
    header: 'Delete Confirmation',
    icon: 'pi pi-info-circle',
    acceptClass: 'p-button-danger',
    accept: () => {
      deleteTimeRecord(record);
    }
  })
}

const populateNewRecordInfo = () => {
  newRecord.value.domain_id = '';
  newRecord.value.category_id = '';
  newRecord.value.title_id = '';

  newRecord.value.timein = toLocalDateTimeString(new Date());
}

watch(recordAttributes, async (newVal) => {
  if (newVal && newVal.length > 0) {
    await nextTick();
    populateNewRecordInfo();
  }
});

onMounted(async () => {
  if (auth.isLoggedIn) {
    await getRecordAttributes();
    await getTimeRecords();
    isFirstLoading.value = false;

  }
})
</script>

<template>
  <div class="">
    <div v-if="auth.isLoggedIn">
      <Panel class="" header="New record" toggleable :collapsed="openRecords.length > 0 || isFirstLoading">
        <TimecardForm
          :recordAttributes="recordAttributes"
          :timeRecord="newRecord"
          @save-record="handleSaveRecord"
        />
      </Panel>

      <Panel class="mt-6" :header="`Open timecard${ openRecords.length > 1 ? 's' : ''}`">
        <div class="flex flex-col gap-16">
          <template v-for="openRecord in openRecords">
            <TimecardForm
              :recordAttributes="recordAttributes"
              :timeRecord="openRecord"
              @save-record="handleSaveRecord"
              @delete-record="deleteTimeRecord"
            />
          </template>
        </div>
      </Panel>

      <Panel class="mt-6" header="History">
        <template v-for="record in recentRecords.sort((a, b) => new Date(b.timein).getTime() - new Date(a.timein).getTime())">
          <LittleRecord :record="record" :recordAttributes="recordAttributes" @delete-record="deleteConfirm(record)"/>
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
</style>
