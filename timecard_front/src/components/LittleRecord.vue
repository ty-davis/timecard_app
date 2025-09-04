<template>
  <div :class="{ border: showDetails, 'my-2': showDetails }" class="dark:border-mygray-700 border-mygray-200 rounded px-2">
    <div class="flex gap-2 items-baseline">
      <RouterLink :to="`/info/${record.domain_id}`">
        <span v-if="domainAttribute" :style="{borderColor: domainAttribute.color || 'transparent', backgroundColor: domainAttribute.color ? secondaryColor(domainAttribute.color) : 'transparent' }" class="border-2 rounded px-2 px-1" >
          {{ domainAttribute.name }}
        </span>
      </RouterLink>
      <span v-if="categoryAttribute" :style="{borderColor: categoryAttribute.color || 'transparent' }" class="border-b-2">{{ categoryAttribute.name }}</span>
      <span class="ml-auto">{{ timeDifference(props.record) }}</span>
      <span class=""><Button link :icon="`pi ${showDetails ? 'pi-chevron-up' : 'pi-chevron-down'}`" class="p-0 m-0 p-button-sm" @click="showDetails = !showDetails"></Button></span>
    </div>
    <div v-if="showDetails">
      <div class="flex items-baseline gap-2">
        <span><RouterLink :to="`/record/${record.id}`" class="underline"> {{ titleAttribute?.name}} </RouterLink></span>
        <span> {{ displayDate }}</span>
        <RouterLink :to="`/record/edit/${record.id}`" class="ml-auto"><Button link icon="pi pi-pen-to-square" class="p-0"/></RouterLink>
        <Button link icon="pi pi-trash" class="p-0" @click="deleteRecord"/>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import type { TimeRecord, RecordAttribute } from '@/types';
import { showTimeDifference } from '@/utils/timeUtils';
import { secondaryColor } from '@/utils/colorUtils';

const props = defineProps<{
  record: TimeRecord;
  recordAttributes: RecordAttribute[];
}>();

const emit = defineEmits<{
  (e: 'delete-record', record: TimeRecord): void
}>();
const domainAttribute = computed(() => { return props.recordAttributes.find(ra => ra.id === props.record.domain_id); })
const categoryAttribute = computed(() => { return props.recordAttributes.find(ra => ra.id === props.record.category_id); })
const titleAttribute = computed(() => { return props.recordAttributes.find(ra => ra.id === props.record.title_id); })


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
