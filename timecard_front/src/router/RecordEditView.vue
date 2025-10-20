<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useRecordAttributesStore } from '@/stores/recordattributes';
import { useTimeRecordsStore } from '@/stores/timerecords';
import { useRouter } from 'vue-router';
import TimecardForm from '@/components/TimecardForm.vue';
import { useRoute } from 'vue-router';
import type { TimeRecord, RecordAttribute } from '@/types';

const auth = useAuthStore();
const router = useRouter();

const defaultTimeRecord: TimeRecord = {
  id: undefined,
  domain_id: '',
  category_id: '',
  title_id: '',
  timein: new Date(),
  timeout: null,
  external_link: '',
  notes: '',
}

const recordAttributesStore = useRecordAttributesStore();
const timeRecordsStore = useTimeRecordsStore();
const { recordAttributes } = storeToRefs(recordAttributesStore);
const {
  timeRecords,
  filteredRecords,
  start,
  end } = storeToRefs(timeRecordsStore);

const loading = ref(true);

const route = useRoute();
const recordId = computed(() => parseInt(route.params.id as string, 10));

const record = computed(() => {
  if (loading.value || !timeRecords.value) {
    return undefined;
  }
  return timeRecords.value.find((r: TimeRecord) => r.id === recordId.value);
})

const handleSaveRecord = async (updatedRecord: TimeRecord) => {
  try {
    await timeRecordsStore.updateTimeRecord(updatedRecord);
    await timeRecordsStore.getTimeRecords(true);
    router.push(`/record/${recordId.value}`);
  } catch (error: any) {
    console.error('Failed to save record:', error.response?.data);

    if (error.response?.status === 401) {
      auth.logout();
    }
  }
}

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      await recordAttributesStore.getRecordAttributes();
      await timeRecordsStore.getTimeRecords();
    } catch (error: any) {
      if (error.response?.status === 401) {
        auth.logout();
      }
    } finally {
      loading.value = false;
    }
  } else {
    loading.value = false;
  }
})
</script>
<template>
  <Card>
    <template #content>
      <template v-if="loading">
        Loading...
      </template>
      <template v-else>
        <TimecardForm
        :timeRecord="record ? record : defaultTimeRecord"
        :recordAttributes="recordAttributes"
        @save-record="handleSaveRecord"/>
      </template>
    </template>
  </Card>
</template>
