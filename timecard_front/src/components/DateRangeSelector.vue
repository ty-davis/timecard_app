<template>
  <div class="flex items-center gap-2">
    <Button
      :label="dateRangeLabel"
      icon="pi pi-calendar"
      @click="visible = true"
      text
      size="small"
    />
    
    <Dialog
      v-model:visible="visible"
      header="Select Date Range"
      :modal="true"
      :style="{ width: '25rem' }"
    >
      <div class="flex flex-col gap-4">
        <div class="flex flex-wrap gap-2">
          <Button 
            label="Last 2 weeks" 
            size="small" 
            outlined 
            @click="setLastTwoWeeks"
          />
          <Button 
            label="This month" 
            size="small" 
            outlined 
            @click="setThisMonth"
          />
        </div>
        
        <div class="flex flex-col gap-2">
          <label for="startDate">Start Date</label>
          <DatePicker
            id="startDate"
            v-model="tempStart"
            dateFormat="yy-mm-dd"
            showIcon
            :maxDate="tempEnd"
          />
        </div>
        
        <div class="flex flex-col gap-2">
          <label for="endDate">End Date</label>
          <DatePicker
            id="endDate"
            v-model="tempEnd"
            dateFormat="yy-mm-dd"
            showIcon
            :minDate="tempStart"
          />
        </div>
        
        <div class="flex gap-2 justify-end mt-2">
          <Button label="Cancel" text @click="visible = false" />
          <Button label="Apply" @click="applyDateRange" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { storeToRefs } from 'pinia';
import { useTimeRecordsStore } from '@/stores/timerecords';

const timeRecordsStore = useTimeRecordsStore();
const { start, end } = storeToRefs(timeRecordsStore);

const visible = ref(false);
const tempStart = ref<Date>(new Date(start.value));
const tempEnd = ref<Date>(new Date(end.value));

const dateRangeLabel = computed(() => {
  const startDate = start.value;
  const endDate = end.value;
  const today = new Date();
  
  // Normalize dates to midnight for comparison
  const normalizeDate = (date: Date) => {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    return d;
  };
  
  const normalizedStart = normalizeDate(startDate);
  const normalizedEnd = normalizeDate(endDate);
  const normalizedToday = normalizeDate(today);
  
  // Check if it's "Last 2 weeks" (14 days ago to today)
  const fourteenDaysAgo = new Date(normalizedToday);
  fourteenDaysAgo.setDate(normalizedToday.getDate() - 14);
  
  if (normalizedStart.getTime() === fourteenDaysAgo.getTime() && 
      normalizedEnd.getTime() === normalizedToday.getTime()) {
    return 'Last 2 weeks';
  }
  
  // Check if it's a full month or current month up to today
  const isFirstOfMonth = normalizedStart.getDate() === 1;
  const isLastOfMonth = normalizedEnd.getDate() === new Date(normalizedEnd.getFullYear(), normalizedEnd.getMonth() + 1, 0).getDate();
  const isSameMonth = normalizedStart.getMonth() === normalizedEnd.getMonth() && 
                      normalizedStart.getFullYear() === normalizedEnd.getFullYear();
  const isCurrentMonth = normalizedStart.getMonth() === today.getMonth() && 
                         normalizedStart.getFullYear() === today.getFullYear();
  const endIsToday = normalizedEnd.getTime() === normalizedToday.getTime();
  
  if (isFirstOfMonth && isSameMonth && (isLastOfMonth || (isCurrentMonth && endIsToday))) {
    return normalizedStart.toLocaleDateString('en-US', { 
      month: 'long', 
      year: 'numeric'
    });
  }
  
  // Default: show date range
  const formatDate = (date: Date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: date.getFullYear() !== new Date().getFullYear() ? 'numeric' : undefined
    });
  };
  
  return `${formatDate(startDate)} - ${formatDate(endDate)}`;
});

const applyDateRange = async () => {
  // Set start date to beginning of day
  const startDate = new Date(tempStart.value);
  startDate.setHours(0, 0, 0, 0);
  
  // Set end date to end of day (23:59:59.999)
  const endDate = new Date(tempEnd.value);
  endDate.setHours(23, 59, 59, 999);
  
  await timeRecordsStore.updateDateRange(startDate, endDate);
  visible.value = false;
};

const setLastTwoWeeks = () => {
  const today = new Date();
  
  const twoWeeksAgo = new Date(today);
  twoWeeksAgo.setDate(today.getDate() - 14);
  twoWeeksAgo.setHours(0, 0, 0, 0);
  
  today.setHours(23, 59, 59, 999);
  
  tempStart.value = twoWeeksAgo;
  tempEnd.value = today;
};

const setThisMonth = () => {
  const today = new Date();
  const firstOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
  firstOfMonth.setHours(0, 0, 0, 0);
  
  const endOfRange = new Date(today);
  endOfRange.setHours(23, 59, 59, 999);
  
  tempStart.value = firstOfMonth;
  tempEnd.value = endOfRange;
};

// Reset temp values when dialog opens
const openDialog = () => {
  tempStart.value = new Date(start.value);
  tempEnd.value = new Date(end.value);
  visible.value = true;
};
</script>
