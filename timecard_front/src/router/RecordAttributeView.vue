<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import api from '@/api/axios';
import { useAuthStore } from '@/stores/auth';
import { useRecordAttributesStore } from '@/stores/recordattributes';
import { useRoute } from 'vue-router';
import type { TimeRecord, RecordAttribute } from '@/types';

const auth = useAuthStore();

const recordAttributesStore = useRecordAttributesStore();
const { recordAttributes } = storeToRefs(recordAttributesStore);
const recentRecords = ref<TimeRecord[]>([]);


const route = useRoute();
const recordId = computed(() => parseInt(route.params.id as string, 10));


const mainRA = computed(() => {
  return recordAttributes.value.find(ra => ra.id === recordId.value);
})

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


const getTimeRecords = async () => {
  try {
    const response = await api.get('/timerecords');
    recentRecords.value = response.data;
  } catch (error: any) {
    console.error('Request failed:', error.response?.data);

    if (error.response?.status === 401) {
      auth.logout();
    }
  }
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
</template>
