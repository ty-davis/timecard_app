<template>
  <div class="flex flex-col items-center justify-center" :class="heightClass">
    <div class="text-[50px] leading-none font-bold">
      {{ elapsedTime }}
    </div>
    <div class="text-xl text-gray-600 dark:text-gray-400 flex gap-3 items-center">
      <Button
        v-if="!isPopup"
        icon="pi pi-home"
        class="p-button-rounded p-button-text"
        @click="router.push('/')"
      />
      <div v-if="domainName" class="underline decoration-4" :style="{ textDecorationColor: domainColor }">{{ domainName }}</div>
      <div v-if="domainName && categoryName">-</div>
      <div v-if="categoryName">{{ categoryName }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useRecordAttributesStore } from '@/stores/recordattributes';
import { storeToRefs } from 'pinia';

const isMobile = computed(() => /iPhone|iPad|iPod|Android/i.test(navigator.userAgent));
const heightClass = computed(() => {
  if (!isPopup.value) return 'min-h-[70vh]';
  return isMobile.value ? 'min-h-screen' : 'min-h-[95vh]';
});

const route = useRoute();
const router = useRouter();
const recordAttributesStore = useRecordAttributesStore();
const { recordAttributes } = storeToRefs(recordAttributesStore);

const elapsedTime = ref('00:00');
let intervalId: number | null = null;

const domainId = computed(() => route.query.domain ? Number(route.query.domain) : null);
const categoryId = computed(() => route.query.category ? Number(route.query.category) : null);
const clockInTime = computed(() => route.query.timein ? new Date(route.query.timein as string) : null);
const isPopup = computed(() => window.opener !== null);

const domainName = computed(() => {
  if (!domainId.value) return '';
  const domain = recordAttributes.value.find(attr => attr.id === domainId.value);
  return domain?.name || '';
});

const domainColor = computed(() => {
  if (!domainId.value) return '';
  const domain = recordAttributes.value.find(attr => attr.id === domainId.value);
  return domain?.color || '';
});

const categoryName = computed(() => {
  if (!categoryId.value) return '';
  const category = recordAttributes.value.find(attr => attr.id === categoryId.value);
  return category?.name || '';
});

const updateTime = () => {
  if (!clockInTime.value) {
    elapsedTime.value = '00:00';
    return;
  }
  
  const now = new Date();
  const diffMs = now.getTime() - clockInTime.value.getTime();
  
  const totalSeconds = Math.floor(diffMs / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const hrs = `${hours ? hours.toString().padStart(2, '0') + ':' : ''}`;
  elapsedTime.value = `${hrs}${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
};

onMounted(async () => {
  await recordAttributesStore.getRecordAttributes();
  updateTime();
  intervalId = window.setInterval(updateTime, 1000);
});

onUnmounted(() => {
  if (intervalId !== null) {
    clearInterval(intervalId);
  }
});
</script>
