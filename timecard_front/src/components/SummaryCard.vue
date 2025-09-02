<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, type CSSProperties } from 'vue';
import type { TimeRecord, RecordAttribute, SummaryData, CategoryRecord } from '@/types';
import { secondaryColor } from '@/utils/colorUtils';
import { showTime, timeDiff } from '@/utils/timeUtils';

const containerDiv = ref<HTMLDivElement | null>(null);
const containerWidth = ref(0);

const props = defineProps<{
  summaryData: SummaryData;
  recordAttributes: RecordAttribute[];
  maxTime: number;
}>();

const domainRA = computed(() => {
  return props.recordAttributes.find(ra => ra.id === props.summaryData.domainId);
})

const categoryRAs = computed(() => {
  const res = [];
  for (let cr of props.summaryData.categoryRecords) {
    const obj = {
      width: `${Math.floor(cr.timeDiff / props.maxTime * containerWidth.value) - 5}px`,
      ra: props.recordAttributes.find(ra => ra.id === cr.category_id)
    };
    res.push(obj);
  }
  return res;
})

const backgroundColor = computed(() => {
  return secondaryColor(domainRA.value?.color || '#333333');
})

const dynamicStyle = computed(() => {
  const style: CSSProperties = {};
  style.backgroundColor = backgroundColor.value;
  return style;
})

const resizeObserver = new ResizeObserver(entries => {
  containerWidth.value = entries[0].contentRect.width;
});

onMounted(() => {
  if (containerDiv.value) {
    resizeObserver.observe(containerDiv.value);
  }
});

onUnmounted(() => {
  resizeObserver.disconnect();
});
</script>

<template>
  <div ref="containerDiv" :style="dynamicStyle" class="p-1 rounded">
    <div class="flex">
      <div class="font-semibold"><RouterLink :to="`/info/${ summaryData.domainId }`">{{ domainRA?.name }}</RouterLink></div>
      <div class="ml-auto">{{ showTime(summaryData.totalTime) }}</div>
    </div>
    <div>
      <template v-for="cr in categoryRAs">
        <span class="h-[6px] inline-block rounded mr-1" :style="{ width: cr.width, backgroundColor: cr.ra?.color || '#333333' }"></span>
      </template>
    </div>
  </div>
</template>
