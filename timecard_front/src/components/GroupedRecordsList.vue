<template>
  <div>
    <div v-if="groupedRecords.length === 0" class="text-center text-gray-500 py-4">
      No records found in the selected date range.
    </div>
    
    <div v-for="group in groupedRecords" :key="group.dateKey" class="mb-6">
      <h3 class="text-lg font-semibold mb-2 text-gray-700 dark:text-gray-300">
        {{ group.label }}
      </h3>
      <div>
        <template v-for="record in group.records" :key="record.id">
          <LittleRecord 
            :record="record" 
            :recordAttributes="recordAttributes" 
            @delete-record="emit('delete-record', record)"
          />
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { TimeRecord, RecordAttribute } from '@/types';
import LittleRecord from '@/components/LittleRecord.vue';

const props = defineProps<{
  records: TimeRecord[];
  recordAttributes: RecordAttribute[];
}>();

const emit = defineEmits<{
  (e: 'delete-record', record: TimeRecord): void
}>();

type GroupedRecord = {
  dateKey: string;
  label: string;
  date: Date;
  records: TimeRecord[];
};

const groupedRecords = computed(() => {
  // Group records by date
  const groups: Record<string, GroupedRecord> = {};
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  
  // Sort records by timein (newest first)
  const sortedRecords = [...props.records].sort((a, b) => 
    new Date(b.timein).getTime() - new Date(a.timein).getTime()
  );
  
  for (const record of sortedRecords) {
    const recordDate = new Date(record.timein);
    recordDate.setHours(0, 0, 0, 0);
    
    const dateKey = recordDate.toISOString().split('T')[0]; // YYYY-MM-DD
    
    if (!groups[dateKey]) {
      let label: string;
      
      if (recordDate.getTime() === today.getTime()) {
        label = 'Today';
      } else if (recordDate.getTime() === yesterday.getTime()) {
        label = 'Yesterday';
      } else {
        label = recordDate.toLocaleDateString('en-US', { 
          weekday: 'long',
          month: 'long', 
          day: 'numeric',
          year: recordDate.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
        });
      }
      
      groups[dateKey] = {
        dateKey,
        label,
        date: recordDate,
        records: []
      };
    }
    
    groups[dateKey].records.push(record);
  }
  
  // Convert to array and sort by date (newest first)
  return Object.values(groups).sort((a, b) => 
    b.date.getTime() - a.date.getTime()
  );
});
</script>
