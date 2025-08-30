<template>
  <div :class="{ border: showDetails, 'my-2': showDetails }" class="dark:border-gray-700 rounded">
    <div class="flex gap-2 items-baseline">
      <span>{{ recordAttributes.find(ra => ra.id === props.record.domain_id)?.name }}</span>
      <span>{{ recordAttributes.find(ra => ra.id === props.record.category_id)?.name }}</span>
      <span class="ml-auto">{{ timeDifference(props.record) }}</span>
      <span class=""><Button link :icon="`pi ${showDetails ? 'pi-chevron-up' : 'pi-chevron-down'}`" class="p-0 m-0 p-button-sm" @click="showDetails = !showDetails"></Button></span>
    </div>
    <div v-if="showDetails">
      <div class="flex items-baseline gap-2">
        <span> {{ recordAttributes.find(ra => ra.id === props.record.title_id)?.name}} </span>
        <span> {{ displayDate }}</span>
        <Button link icon="pi pi-trash" class="p-0 ml-auto" @click="deleteRecord"/>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { TimeRecord, RecordAttribute } from '@/types';
import { showTimeDifference } from '@/utils/timeUtils';

const props = defineProps<{
  record: TimeRecord;
  recordAttributes: RecordAttribute[];
}>();

const emit = defineEmits<{
  (e: 'delete-record', record: TimeRecord): void
}>();


const showDetails = ref<boolean>(false);
const displayDate = computed(() => {
  const d = new Date(props.record.timein);
  return d.toDateString();
})

const timeDifference = (record: TimeRecord) => {
  if (!(record.timein && record.timeout)) {
    return '';
  }
  return showTimeDifference(new Date(record.timein), new Date(record.timeout));
}

const deleteRecord = () => {
  emit('delete-record', props.record);
}

</script>
