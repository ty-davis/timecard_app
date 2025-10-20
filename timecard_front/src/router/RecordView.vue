<script setup lang="ts">
import { ref, onMounted, computed, type CSSProperties } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useRecordAttributesStore } from '@/stores/recordattributes';
import { useTimeRecordsStore } from '@/stores/timerecords';
import { showTime, timeDiff } from '@/utils/timeUtils';
import { useRoute } from 'vue-router';
import { secondaryColor } from '@/utils/colorUtils';
import type { TimeRecord, RecordAttribute } from '@/types';

const auth = useAuthStore();
const route = useRoute();

const recordId = computed(() => parseInt(route.params.id as string, 10));

const recordAttributesStore = useRecordAttributesStore();
const timeRecordsStore = useTimeRecordsStore();
const { recordAttributes } = storeToRefs(recordAttributesStore);
const {
  timeRecords,
  filteredRecords,
} = storeToRefs(timeRecordsStore);

const record = computed(() => {
  return timeRecords.value.find((r: TimeRecord) => r.id === recordId.value);
})

const timein = computed(() => {
  if (record.value?.timein) {
    return new Date(record.value?.timein);
  }
  return new Date();
});
const timeout = computed(() => {
  return record.value?.timeout ? new Date(record.value?.timeout) : null;
});

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      await recordAttributesStore.getRecordAttributes();
      await timeRecordsStore.getTimeRecords();
    } catch (error: any) {
      if (error.response?.status === 401) {
        auth.logout();
      }
    }
  }
})

const domainRA = computed(() => {
  return recordAttributes.value.find((ra: RecordAttribute) => ra.id === record.value?.domain_id);
});
const domainStyle = computed(() => {
  const style: CSSProperties = {};
  if (domainRA.value) {
    console.log(domainRA);
    style.borderColor = domainRA.value?.color || '#333333';
    style.backgroundColor = secondaryColor(domainRA.value?.color || '#333333');
  }
  return style;
});

const categoryRA = computed(() => {
  return recordAttributes.value.find((ra: RecordAttribute) => ra.id === record.value?.category_id);
})
const categoryStyle = computed(() => {
  return {};
})

const titleRA = computed(() => {
  return recordAttributes.value.find((ra: RecordAttribute) => ra.id === record.value?.title_id);
})
const titleStyle = computed(() => {
  return {};
})

</script>
<template>
  <Card>
    <template #content>
      <div class="mb-4">
        <div class="mb-2">
          <span :style="domainStyle" class="border p-1 text-2xl rounded-md font-bold"> {{ domainRA?.name }} </span>
        </div>
        <div>
          <span :style="categoryStyle" class="border-b p-1 text-lg inline-block mb-2"> {{ categoryRA?.name }} </span>
        </div>
        <span :style="titleStyle" class="p-1"> {{ titleRA?.name }}</span>
      </div>

      <a :href="`${ record?.external_link }`" class="text-blue-500 hover:underline">External Link</a>

      <div>
        <div>
          {{ timein.toLocaleDateString() }}
        </div>
        <div>
          {{ timein.toLocaleTimeString() }}
          <template v-if="timeout">
            &ndash; {{ timeout.toLocaleTimeString() }}
          </template>
        </div>
      </div>
    </template>
  </Card>
</template>
