<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useRecordAttributesStore } from '@/stores/recordattributes';
import { useTimeRecordsStore } from '@/stores/timerecords';
import { showTime, timeDiff } from '@/utils/timeUtils';
import SummaryCard from '@/components/SummaryCard.vue';
import DateRangeSelector from '@/components/DateRangeSelector.vue';

import type { TimeRecord, RecordAttribute, SummaryData } from '@/types';

const auth = useAuthStore();
const isFirstLoading = ref(true);
const recordAttributesStore = useRecordAttributesStore();
const timeRecordsStore = useTimeRecordsStore();
const { timeRecords, filteredRecords } = storeToRefs(timeRecordsStore);
const openRecords = computed(() => {
  return filteredRecords.value.filter((r: TimeRecord) => r.timeout === null);
})
const { recordAttributes } = storeToRefs(recordAttributesStore);
const today = computed(() => {
  const d = new Date();
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
})

const mainData = computed(() => {
  const d: Record<string | number, SummaryData> = {};
  for (let record of filteredRecords.value) {
    if (!d[record.domain_id]) {
      d[record.domain_id] = {
        domainId: record.domain_id,
        totalTime: 0,
        categoryRecords: [],
      };
    }
    const timeout = record.timeout ? new Date(record.timeout) : new Date();
    const timeDifference = timeDiff(new Date(record.timein), timeout);
    d[record.domain_id].totalTime += timeDifference;
    d[record.domain_id].categoryRecords.push({
      timeDiff: timeDifference,
      category_id: record.category_id
    });
  }
  const sortedDomains = Object.values(d).sort((a, b) => {
    return b.totalTime - a.totalTime; 
  });

  return sortedDomains;
})

const maxTime = computed(() => {
  if (!mainData.value || mainData.value.length === 0) {
    return 0;
  }
  return mainData.value[0].totalTime;
})

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      await recordAttributesStore.getRecordAttributes();
      await timeRecordsStore.getTimeRecords();
      isFirstLoading.value = false;
    } catch (error: any) {
      if (error.response?.status === 401) {
        auth.logout();
      }
    }
  }
})

</script>

<template>
  <Card>
    <template #content>
      <div class="mb-4 flex items-center gap-2">
        <DateRangeSelector />
      </div>
      <div class="flex flex-col gap-2">
        <div v-for="d in mainData">
          <SummaryCard :summaryData="d" :recordAttributes="recordAttributes" :maxTime="maxTime"/>
        </div>
      </div>
    </template>
  </Card>
</template>
