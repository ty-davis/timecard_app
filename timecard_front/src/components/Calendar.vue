<script setup lang="ts">
import { ref, computed } from 'vue';
import type { TimeRecord, RecordAttribute } from '@/types';

type DayTimeRecords = {
  day: Date;
  timeRecords: TimeRecord[];
};

const props = defineProps<{
  recordAttributes: RecordAttribute[];
  records: TimeRecord[];
}>();

const selMonthObject = ref<Date>(new Date());
const selectedMonth = computed(() => { return selMonthObject.value.getMonth()})
const selectedYear = computed(() => { return selMonthObject.value.getFullYear()})
const weeks = computed(() => {
  const d = new Date(selectedYear.value, selectedMonth.value, 1);
  const dayOfWeek = d.getDay();

  d.setDate(d.getDate() - dayOfWeek);

  const weeks: DayTimeRecords[][] = [];
  while (d.getMonth() <= selectedMonth.value && d.getFullYear() === selectedYear.value) {
    const days: DayTimeRecords[] = [];
    for (let i = 0; i < 7; i++) {
      const dtr: DayTimeRecords = {
        day: new Date(d.getTime()),
        timeRecords: props.records.filter(r => sameDay(new Date(r.timein), d)),
      };
      days.push(dtr);
      d.setDate(d.getDate() + 1);
    }
    weeks.push(days);
  }
  return weeks;
})

const inMonth: boolean = (d: Date) => {
  return d.getMonth() === selectedMonth.value && d.getFullYear() === selectedYear.value;
}

const sameDay: boolean = (d1: Date, d2: Date) => {
  return d1.getDate() === d2.getDate() && d1.getMonth() === d2.getMonth() && d1.getFullYear() === d2.getFullYear();
}

const decrementMonth = () => {
  selMonthObject.value = new Date(selMonthObject.value.getFullYear(), selMonthObject.value.getMonth() - 1, 1);
}

const incrementMonth = () => {
  selMonthObject.value = new Date(selMonthObject.value.getFullYear(), selMonthObject.value.getMonth() + 1, 1);
}
</script>


<template>
  <div class="text-center mb-3">
    <Button link icon="pi pi-chevron-left" @click="decrementMonth"/>
    <DatePicker view="month" v-model="selMonthObject" dateFormat="MM yy"/>
    <Button link icon="pi pi-chevron-right" @click="incrementMonth"/>
  </div>
  <div class="">
    <div class="grid grid-cols-7">
      <span class="text-center font-semibold" v-for="day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']">{{ day }}</span>
    </div>
    <template v-for="week in weeks">
      <div class="grid grid-cols-7">
        <template v-for="dtr in week">
          <span class="px-1 min-h-16 border dark:border-gray-800 m-[1px]" :class="{ 'text-gray-400': !inMonth(dtr.day) }">
            <div> {{ dtr.day.getDate() }} </div>
            <div v-for="record in dtr.timeRecords" class="w-full h-1 mb-1" :style="{ backgroundColor: props.recordAttributes.find(ra => ra.id === record.domain_id).color || '#333' }"> </div>
          </span>
        </template>
      </div>
    </template>
  </div>

</template>
