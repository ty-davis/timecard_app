<template>
  <div class="">
    <div v-if="timeRecord.id && !timeRecord.timeout" class="flex justify-end mb-3">
      <Button
        icon="pi pi-clock"
        class="p-button-rounded p-button-text"
        @click="goToClock"
        v-tooltip.left="'View Clock'"
      />
    </div>
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

      <div>
        <InputText type="text" id="externalLink" v-model="externalLink" placeholder="obsidian://..." style="width: 100%;"/>
      </div>

      <!-- JIRA Issue Section -->
      <div class="flex flex-col gap-2">
        <!-- Show badge if already linked (viewing mode) -->
        <div v-if="timeRecord.id && jiraIssueKey" class="flex items-center gap-2">
          <JiraIssueBadge 
            :issue-key="jiraIssueKey"
            :show-summary="true"
            size="medium"
          />
        </div>
        <!-- Issue Selector (editing mode) -->
        <JiraIssueSelector v-model="jiraIssueKey" />
      </div>

      <div class="flex space-x-4">
        <div class="p-field flex-1 flex flex-col gap-2">
          <label for="timein">In:</label>
          <DatePicker id="datepicker-12h" v-model="localTimein" showTime hourFormat="12" fluid/>
        </div>
      </div>

      <div v-if="timeRecord.id && !timeRecord.timeout">
        <div class="flex space-x-4">
          <Checkbox v-model="showTimeout" binary />
          <span>
            Choose clock out time
          </span>
        </div>
      </div>

      <div v-if="showTimeout || timeRecord.timeout" class="p-field flex-1 flex flex-col gap-2">
        <label for="timeout">Out:</label>
        <DatePicker v-model="localTimeout" showTime hourFormat="12" fluid/>
      </div>

      <!-- JIRA Sync Button (for existing records with JIRA issue) -->
      <div v-if="timeRecord.id && timeRecord.timeout && timeRecord.jira_issue_key" class="flex justify-end">
        <JiraSyncButton :record="record" :show-label="true" size="large" />
      </div>

      <div class="flex gap-2 flex-wrap">
        <template v-if="!timeRecord.timeout">
          <Button 
            type="submit" 
            :label="`Clock ${record.id ? 'Out' : 'In'}`" 
            icon="pi pi-check"
            :disabled="!readyToSubmit"
            class="p-button-success p-button-lg grow-3"
          />
        </template>
      </div>
      <div class="flex gap-2 flex-wrap">
        <Button
          v-if="timeRecord.id && record.timeout"
          label="Cancel"
          class="p-button-lg p-button-secondary grow"
          @click="router.push(`/record/${record.id}`)"
        />
        <Button
          v-if="timeRecord.id"
          label="Save Changes"
          :disabled="!readyToSubmit"
          class="p-button-lg grow"
          @click="saveChanges"
        />
        <Button
          v-if="timeRecord.id"
          label="Delete record"
          icon="pi pi-trash"
          class="p-button-danger p-button-lg grow"
          @click="deleteConfirm()"
        />
      </div>

    </form>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, reactive, toRefs, computed, nextTick } from 'vue';
import type { RecordAttribute, TimeRecord } from '@/types';
import { toLocalDateTimeString } from '@/utils/timeUtils';
import TextSelect from '@/components/TextSelect.vue';
import JiraIssueSelector from '@/components/JiraIssueSelector.vue';
import JiraSyncButton from '@/components/JiraSyncButton.vue';
import JiraIssueBadge from '@/components/JiraIssueBadge.vue';
import { useConfirm } from 'primevue/useconfirm';
import { useRouter } from 'vue-router';

const confirm = useConfirm();
const router = useRouter();

const props = defineProps<{
  timeRecord: TimeRecord;
  recordAttributes: RecordAttribute[];
}>();

const localTimein = ref<Date | null>(new Date());
const localTimeout = ref<Date | null>(null);
const showTimeout = ref<boolean>(false);
const jiraIssueKey = ref<string | null>(null);

const emit = defineEmits(['save-record', 'delete-record']);

// --- Reactive State ---
const record = reactive({ ...props.timeRecord });

const selectedDomain = ref<RecordAttribute | string>('');
const selectedCategory = ref<RecordAttribute | string>('');
const selectedTitle = ref<RecordAttribute | string>('');

const externalLink = ref<string>('');

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
    localTimein.value = new Date();
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

    localTimein.value = new Date(props.timeRecord.timein);
    if (props.timeRecord.timeout) {
      localTimeout.value = new Date(props.timeRecord.timeout);
    }

    externalLink.value = props.timeRecord.external_link || '';
    jiraIssueKey.value = props.timeRecord.jira_issue_key || null;

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

const prepTimeRecord = (clockOut: boolean) => {
  if (!localTimein.value) {
    throw new Error('time in is missing.');
  }
  const utcDateTimeIn = localTimein.value.toISOString();

  let utcDateTimeOut = null;
  if ((showTimeout.value || record.timeout) && localTimeout.value && clockOut) {
    utcDateTimeOut = localTimeout.value.toISOString();
  } else if (clockOut) {
    utcDateTimeOut = new Date().toISOString();
  }

  if (!selectedDomain.value || !selectedCategory.value || !selectedTitle.value) {
    throw new Error('A record attribute is missing');
  }

  if (typeof selectedDomain.value === 'object' && selectedDomain.value.id)
    record.domain_id = selectedDomain.value.id;
  else if (typeof selectedDomain.value === 'string')
    record.domain_id = selectedDomain.value;
  
  if (typeof selectedCategory.value === 'object' && selectedCategory.value.id)
    record.category_id = selectedCategory.value.id;
  else if (typeof selectedCategory.value === 'string')
    record.category_id = selectedCategory.value;
    
  if (typeof selectedTitle.value === 'object' && selectedTitle.value.id)
    record.title_id = selectedTitle.value.id 
  else if (typeof selectedTitle.value === 'string')
    record.title_id = selectedTitle.value;

  record.timein = utcDateTimeIn;
  record.timeout = utcDateTimeOut;

  record.external_link = externalLink.value;
  record.jira_issue_key = jiraIssueKey.value;

}

const saveChanges = () => {
  prepTimeRecord(false || !!record.timeout);
  emit('save-record', record);
}

const submitTimeRecord = () => {
  prepTimeRecord(true);
  emit('save-record', record);
};

const deleteTimeRecord = () => {
  prepTimeRecord(false);
  emit('delete-record', record);
}



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

const goToClock = () => {
  const domainId = typeof selectedDomain.value === 'object' ? selectedDomain.value.id : null;
  const categoryId = typeof selectedCategory.value === 'object' ? selectedCategory.value.id : null;
  
  const clockUrl = router.resolve({
    path: '/clock',
    query: {
      domain: domainId,
      category: categoryId,
      timein: props.timeRecord.timein?.toString()
    }
  }).href;
  
  const width = 500;
  const height = 300;
  const left = (screen.width - width) / 2;
  const top = (screen.height - height) / 2;
  
  window.open(
    clockUrl,
    'clockWindow',
    `width=${width},height=${height},left=${left},top=${top},menubar=no,toolbar=no,location=no,status=no,scrollbars=no,resizable=yes`
  );
};


</script>
