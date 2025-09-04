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

</script>
<template>
  Record edit view
</template>
