<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useRecordAttributesStore } from '@/stores/recordattributes';
import { useTimeRecordsStore } from '@/stores/timerecords';
import { useRoute } from 'vue-router';
import { useConfirm } from 'primevue/useconfirm';
import type { TimeRecord, RecordAttribute } from '@/types';
import DateRangeSelector from '@/components/DateRangeSelector.vue';
import GroupedRecordsList from '@/components/GroupedRecordsList.vue';

const auth = useAuthStore();
const confirm = useConfirm();

const recordAttributesStore = useRecordAttributesStore();
const { recordAttributes } = storeToRefs(recordAttributesStore);

const timeRecordsStore = useTimeRecordsStore();
const { timeRecords } = storeToRefs(timeRecordsStore);

const recentRecords = ref<TimeRecord[]>([]);


const route = useRoute();
const recordId = computed(() => parseInt(route.params.id as string, 10));


const mainRA = computed(() => {
  return recordAttributes.value.find(ra => ra.id === recordId.value);
})

const filteredTimeRecords = computed(() => {
  return timeRecords.value.filter(record => record.domain_id === recordId.value)
    .sort((a, b) => new Date(b.timein).getTime() - new Date(a.timein).getTime());
});

const colorSelect = computed({
  get() {
    return mainRA.value?.color;
  },
  set(newColor) {
    if (mainRA.value) {
      recordAttributesStore.updateRecordAttribute({ ...mainRA.value, color: `#${newColor}` });
    }
  }
});

const deleteConfirm = (record: TimeRecord) => {
  confirm.require({
    message: 'Do you want to delete this record?',
    header: 'Delete Confirmation',
    icon: 'pi pi-info-circle',
    acceptClass: 'p-button-danger',
    accept: () => {
      try {
        timeRecordsStore.deleteTimeRecord(record);
      } catch (error: any) {
        if (error.response?.status === 401) {
          auth.logout();
        }
      }
    }
  })
}


onMounted(async () => {
  if (auth.isLoggedIn) {
    if (!recordAttributes.value?.length) {
      try {
        await recordAttributesStore.getRecordAttributes();

      } catch (error: any) {
        if (error.response?.status === 401) {
          auth.logout();
        }
      }
    }
    
    if (!timeRecords.value?.length) {
      try {
        await timeRecordsStore.getTimeRecords();
      } catch (error: any) {
        if (error.response?.status === 401) {
          auth.logout();
        }
      }
    }
  }
})
</script>

<template>
  <Card>
    <template #title>
      <div class="flex">
        <div class="text-2xl font-bold">
          {{ mainRA?.name }}
        </div>
        <div class="ml-auto">
          {{ mainRA?.color }}
          <ColorPicker v-model="colorSelect"/>
        </div>
      </div>
    </template>
    <template #content>
    </template>
  </Card>

  <Panel class="mt-6">
    <template #header>
      <div class="flex items-center justify-between w-full">
        <span>Time Records</span>
        <DateRangeSelector />
      </div>
    </template>
    
    <GroupedRecordsList 
      :records="filteredTimeRecords" 
      :recordAttributes="recordAttributes" 
      @delete-record="deleteConfirm"
    />
  </Panel>
</template>
