<template>
  <div class="">
    <form @submit.prevent="submitTimeRecord" class="flex flex-col gap-4">
      <div class="my-2">
        <AutoComplete
          v-model="selectedDomain"
          :suggestions="domainSuggestions"
          @complete="search($event, 1)"
          optionLabel="name"
          dropdown
          placeholder="Select a domain or type a new one..."
        />
      </div>

      <div class="p-field flex flex-col gap-2">
        <AutoComplete
          v-model="selectedCategory"
          :suggestions="categorySuggestions"
          @complete="search($event, 2)"
          :disabled="!selectedDomain && typeof selectedDomain === 'object'"
          optionLabel="name"
          dropdown
          placeholder="Select a category or type a new one..."
          class="w-full"
        />
      </div>

      <div class="p-field flex flex-col gap-2">
        <AutoComplete
          v-model="selectedTitle"
          :suggestions="titleSuggestions"
          @complete="search($event, 3)"
          :disabled="!selectedCategory && typeof selectedCategory === 'object'"
          optionLabel="name"
          dropdown
          placeholder="Select a title or type a new one..."
          class="w-full"
        />
      </div>

      <div class="flex space-x-4">
        <div class="p-field flex-1 flex flex-col gap-2">
          <label for="timein">In:</label>
          <InputText id="timein" type="datetime-local" v-model="record.timein" class="rounded-lg p-3" />
        </div>
      </div>
      
      <Button 
        type="submit" 
        :label="`Clock ${record.id ? 'Out' : 'In'}`" 
        icon="pi pi-check"
        class="p-button-success p-button-lg"
      />

      <Button
        label="Choose Clockout Time"
        class="p-button-danger p-button-lg"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive, toRefs } from 'vue';
import type { RecordAttribute, TimeRecord } from '@/types';

// --- Props & Emits ---
const props = defineProps<{
  timeRecord: TimeRecord;
  recordAttributes: RecordAttribute[];
}>();

const emit = defineEmits(['save-record']);

// --- Reactive State ---
// Local copy of the time record to avoid mutating props directly
const record = reactive({ ...props.timeRecord });

// Selected items from the AutoComplete dropdowns.
const selectedDomain = ref<RecordAttribute | string | null>(null);
const selectedCategory = ref<RecordAttribute | string | null>(null);
const selectedTitle = ref<RecordAttribute | string | null>(null);

// Suggestions for each AutoComplete
const domainSuggestions = ref<RecordAttribute[]>([]);
const categorySuggestions = ref<RecordAttribute[]>([]);
const titleSuggestions = ref<RecordAttribute[]>([]);

// --- Pre-populate Form from Props ---
/**
 * Watcher to pre-populate the AutoComplete components when the timeRecord prop changes.
 */
watch(() => props.timeRecord, (newRecord) => {
  // Update the reactive record object with the new prop values.
  Object.assign(record, newRecord);

  // If a domain_id exists, find the corresponding object and set the selected value
  if (newRecord.domain_id !== null) {
    selectedDomain.value = props.recordAttributes.find(attr => attr.id === newRecord.domain_id) || null;
  }
  // If a category_id exists, find the corresponding object and set the selected value
  if (newRecord.category_id !== null) {
    selectedCategory.value = props.recordAttributes.find(attr => attr.id === newRecord.category_id) || null;
  }
  // If a title_id exists, find the corresponding object and set the selected value
  if (newRecord.title_id !== null) {
    selectedTitle.value = props.recordAttributes.find(attr => attr.id === newRecord.title_id) || null;
  }
}, { immediate: true, deep: true });

// --- AutoComplete Logic ---
/**
 * Filters the provided record attributes based on the query and level number.
 * Populates the correct suggestions list.
 */
const search = (event: { query: string }, level: number) => {
  const query = event.query.toLowerCase();

  // Determine the parent_id to filter by based on the level.
  let parentId: number | null = null;
  if (level === 2 && typeof selectedDomain.value === 'object' && selectedDomain.value) {
    parentId = selectedDomain.value.id || null;
  }
  if (level === 3 && typeof selectedCategory.value === 'object' && selectedCategory.value) {
    parentId = selectedCategory.value.id || null;
  }
  
  // Filter the provided database
  const filtered = props.recordAttributes.filter(attr => 
    attr.level_num === level &&
    (parentId === null || attr.parent_id === parentId) &&
    attr.name.toLowerCase().includes(query)
  );

  // Set the suggestions for the correct level
  if (level === 1) {
    domainSuggestions.value = filtered;
  } else if (level === 2) {
    categorySuggestions.value = filtered;
  } else if (level === 3) {
    titleSuggestions.value = filtered;
  }
};

// --- Dynamic Dependencies ---
// Watchers to clear downstream selections when a parent changes.
// This ensures the form's state is consistent.
watch(selectedDomain, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    selectedCategory.value = null;
    selectedTitle.value = null;
  }
});

watch(selectedCategory, (newValue, oldValue) => {
  if (newValue !== oldValue) {
    selectedTitle.value = null;
  }
});

// --- Form Submission Logic ---
/**
 * Handles form submission. Maps the selected RecordAttribute objects
 * or new string values to the TimeRecord's ID fields and emits the record.
 */
const submitTimeRecord = () => {

  const localDateTimeIn = new Date(record.timein);
  const utcDateTimeIn = localDateTimeIn.toISOString().slice(0, 19);

  // Update the record's ID fields based on the selections.
  record.domain_id = typeof selectedDomain.value === 'object' 
    ? (selectedDomain.value?.id || null) 
    : null;
  
  record.category_id = typeof selectedCategory.value === 'object'
    ? (selectedCategory.value?.id || null)
    : null;
    
  record.title_id = typeof selectedTitle.value === 'object'
    ? (selectedTitle.value?.id || null)
    : null;

  record.timein = utcDateTimeIn;
  record.timeout = new Date().toISOString().slice(0, 19);

  // Emit the updated record to the parent component.
  emit('save-record', record);
};
</script>
