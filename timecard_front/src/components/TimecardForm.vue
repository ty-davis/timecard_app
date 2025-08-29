<template>
  <div class="">
    <form @submit.prevent="submitTimeRecord" class="flex flex-col gap-4">
      <div>
        <TextSelect
          v-model="selectedDomain"
          :recordAttributes="props.recordAttributes"
          :parentRecordAttribute="null"
          :levelNum="1"
          placeholder="Select a domain or type a new one..."
        />
      </div>

      <div>
        <TextSelect
          v-model="selectedCategory"
          :recordAttributes="props.recordAttributes"
          :parentRecordAttribute="selectedDomain"
          :levelNum="2"
          :disabled="selectedDomain === null || selectedDomain === ''"
          placeholder="Select a category or type a new one..."
        />
      </div>

      <div>
        <TextSelect
          v-model="selectedTitle"
          :recordAttributes="props.recordAttributes"
          :parentRecordAttribute="selectedCategory"
          :levelNum="3"
          :disabled="selectedCategory === null || selectedCategory === ''"
          placeholder="Select a title or type a new one..."
        />
      </div>

      <div class="flex space-x-4">
        <div class="p-field flex-1 flex flex-col gap-2">
          <label for="timein">In:</label>
          <InputText id="timein" type="datetime-local" v-model="localTimein" class="rounded-lg p-3" />
        </div>
      </div>
      
      <div class="flex gap-2">
        <Button 
          type="submit" 
          :label="`Clock ${record.id ? 'Out' : 'In'}`" 
          icon="pi pi-check"
          :disabled="!readyToSubmit"
          class="p-button-success p-button-lg flex-grow"
        />
        <Button
          v-if="timeRecord.id"
          label="Delete record"
          icon="pi pi-trash"
          @click="deleteConfirm()"
        />
      </div>

      <Button
        v-if="timeRecord.id"
        label="Choose Clockout Time"
        class="p-button-danger p-button-lg"
      />
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive, toRefs, computed, nextTick } from 'vue';
import type { RecordAttribute, TimeRecord } from '@/types';
import { toLocalDateTimeString } from '@/utils/timeUtils';
import TextSelect from '@/components/TextSelect.vue';
import { useConfirm } from 'primevue/useconfirm';


const props = defineProps<{
  timeRecord: TimeRecord;
  recordAttributes: RecordAttribute[];
}>();

const localTimein = ref<string>(toLocalDateTimeString(new Date()));

const emit = defineEmits(['save-record', 'delete-record']);

// --- Reactive State ---
const record = reactive({ ...props.timeRecord });

const selectedDomain = ref<RecordAttribute | string>('');
const selectedCategory = ref<RecordAttribute | string>('');
const selectedTitle = ref<RecordAttribute | string>('');

const isPopulating = ref(true);

const readyToSubmit = computed(() => {
  if (selectedDomain.value === '' || selectedDomain.value === null) {
    return false;
  }
  if (selectedCategory.value === '' || selectedCategory.value === null) {
    return false;
  }
  if (selectedTitle.value === '' || selectedTitle.value === null) {
    return false;
  }
  return true;
})

// Suggestions for each AutoComplete
const domainSuggestions = ref<RecordAttribute[]>([]);
const categorySuggestions = ref<RecordAttribute[]>([]);
const titleSuggestions = ref<RecordAttribute[]>([]);


// --- Pre-populate Form from Props ---
/**
 * Watcher to pre-populate the AutoComplete components when the timeRecord prop changes.
 */
watch(() => props.timeRecord, async (newRecord) => {
  Object.assign(record, newRecord);

  if (newRecord.domain_id === null && newRecord.category_id === null && newRecord.title_id === null) {
    selectedDomain.value = '';
    selectedCategory.value = '';
    selectedTitle.value = '';
    localTimein.value = toLocalDateTimeString(new Date());
    return;
  }

  const hasDataToPopulate = newRecord && newRecord.domain_id !== null;
  if (hasDataToPopulate) {
    if (newRecord.domain_id !== null) {
      selectedDomain.value = props.recordAttributes.find(attr => attr.id === newRecord.domain_id) || selectedDomain.value;
    }
    if (newRecord.category_id !== null) {
      selectedCategory.value = props.recordAttributes.find(attr => attr.id === newRecord.category_id) || selectedCategory.value;
    }
    if (newRecord.title_id !== null) {
      selectedTitle.value = props.recordAttributes.find(attr => attr.id === newRecord.title_id) || selectedTitle.value;
    }

    localTimein.value = toLocalDateTimeString(new Date(props.timeRecord.timein));

    await nextTick();
    isPopulating.value = false;
  }



}, { immediate: true, deep: true });


watch(selectedDomain, (newValue, oldValue) => {
  if (isPopulating.value) return;

  if (newValue !== oldValue) {
    selectedCategory.value = '';
    selectedTitle.value = '';
  }
});

watch(selectedCategory, (newValue, oldValue) => {
  if (isPopulating.value) return;

  if (newValue !== oldValue) {
    selectedTitle.value = '';
  }
});

const prepTimeRecord = () => {
  const localDateTimeIn = new Date(localTimein.value);
  const utcDateTimeIn = localDateTimeIn.toISOString();

  record.domain_id = typeof selectedDomain.value === 'object' 
    ? (selectedDomain.value?.id || null) 
    : selectedDomain.value;
  
  record.category_id = typeof selectedCategory.value === 'object'
    ? (selectedCategory.value?.id || null)
    : selectedCategory.value;
    
  record.title_id = typeof selectedTitle.value === 'object'
    ? (selectedTitle.value?.id || null)
    : selectedTitle.value;

  record.timein = utcDateTimeIn;
  record.timeout = new Date().toISOString();

}

const submitTimeRecord = () => {
  prepTimeRecord();
  emit('save-record', record);
};

const deleteTimeRecord = () => {
  prepTimeRecord();
  emit('delete-record', record);
}


const confirm = useConfirm();

const deleteConfirm = () => {
  confirm.require({
    message: 'Are you sure you want to delete this record?',
    header: 'Delete record?',
    icon: 'pi pi-info-circle',
    rejectLabel: 'Cancel',
    accept: () => {
      deleteTimeRecord();      
    }
  });
};


</script>
