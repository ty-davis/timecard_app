<script setup lang="ts">
import { ref, computed, watch } from 'vue';
import { useJiraStore } from '@/stores/jira';
import type { JiraIssue } from '@/types';

const jiraStore = useJiraStore();

const props = defineProps<{
  modelValue: string | null;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | null): void;
}>();

const selectedIssue = ref<JiraIssue | null>(null);
const searchQuery = ref('');
const issues = ref<JiraIssue[]>([]);
const isSearching = ref(false);
const searchTimeout = ref<number | null>(null);

// Check if JIRA is connected
const isConnected = computed(() => jiraStore.hasActiveConnection);

// Format issue for display
const formatIssue = (issue: JiraIssue) => {
  return `[${issue.key}] ${issue.summary}`;
};

// Search issues with debounce
const searchIssues = async (query: string) => {
  if (!query || query.length < 2) {
    issues.value = [];
    return;
  }

  isSearching.value = true;
  
  try {
    const results = await jiraStore.searchIssues(query);
    issues.value = results;
  } catch (error) {
    console.error('Error searching JIRA issues:', error);
    issues.value = [];
  } finally {
    isSearching.value = false;
  }
};

// Debounced search handler
const onSearch = (event: any) => {
  const query = event.query || event;
  
  // Clear existing timeout
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }

  // Set new timeout
  searchTimeout.value = window.setTimeout(() => {
    searchIssues(query);
  }, 300);
};

// When an issue is selected
const onIssueSelect = (event: any) => {
  const issue = event.value as JiraIssue;
  if (issue) {
    selectedIssue.value = issue;
    emit('update:modelValue', issue.key);
  }
};

// Clear selection
const clearSelection = () => {
  selectedIssue.value = null;
  searchQuery.value = '';
  emit('update:modelValue', null);
};

// Load issue details if we have a key but no selected issue
watch(() => props.modelValue, async (newKey) => {
  if (newKey && !selectedIssue.value) {
    try {
      const issue = await jiraStore.getIssue(newKey);
      if (issue) {
        selectedIssue.value = issue;
      }
    } catch (error) {
      console.error('Error loading JIRA issue:', error);
    }
  } else if (!newKey) {
    selectedIssue.value = null;
  }
}, { immediate: true });
</script>

<template>
  <div class="my-2">
    <!-- Not connected warning -->
    <div v-if="!isConnected" class="mb-3">
      <Message severity="warn" :closable="false">
        <div class="flex items-center gap-2">
          <span>JIRA not connected.</span>
          <RouterLink to="/settings/jira">
            <Button label="Connect JIRA" size="small" outlined />
          </RouterLink>
        </div>
      </Message>
    </div>

    <!-- Issue selector (when connected) -->
    <div v-else>
      <!-- Display selected issue -->
      <div v-if="selectedIssue && props.modelValue" class="mb-3">
        <Card>
          <template #content>
            <div class="flex justify-between items-start gap-3">
              <div class="flex-1 flex gap-3 items-start">
                <div class="flex-shrink-0">
                  <a 
                    :href="`${jiraStore.activeConnection?.jira_url}/browse/${selectedIssue.key}`" 
                    target="_blank" 
                    rel="noopener"
                    class="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-600 dark:bg-blue-500 text-white rounded-md no-underline font-semibold text-sm hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
                  >
                    {{ selectedIssue.key }}
                    <i class="pi pi-external-link text-xs"></i>
                  </a>
                </div>
                <div class="flex-1 flex flex-col gap-1.5">
                  <div class="font-medium text-gray-900 dark:text-gray-100 leading-tight">
                    {{ selectedIssue.summary }}
                  </div>
                  <div class="flex gap-3 items-center flex-wrap">
                    <span 
                      class="inline-block px-2 py-0.5 rounded text-xs font-semibold uppercase"
                      :class="{
                        'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300': ['to do', 'open'].includes(selectedIssue.status.toLowerCase()),
                        'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300': selectedIssue.status.toLowerCase() === 'in progress',
                        'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300': ['done', 'closed', 'resolved'].includes(selectedIssue.status.toLowerCase()),
                        'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300': !['to do', 'open', 'in progress', 'done', 'closed', 'resolved'].includes(selectedIssue.status.toLowerCase())
                      }"
                    >
                      {{ selectedIssue.status }}
                    </span>
                    <span v-if="selectedIssue.assignee" class="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                      <i class="pi pi-user text-xs"></i> {{ selectedIssue.assignee }}
                    </span>
                  </div>
                </div>
              </div>
              <Button 
                icon="pi pi-times" 
                @click="clearSelection" 
                text 
                rounded 
                severity="secondary"
                :disabled="props.disabled"
              />
            </div>
          </template>
        </Card>
      </div>

      <!-- Search input (when no issue selected) -->
      <div v-else class="mb-3">
        <label class="block mb-1.5 font-medium text-gray-900 dark:text-gray-100">
          JIRA Issue (Optional)
        </label>
        <AutoComplete
          v-model="searchQuery"
          :suggestions="issues"
          @complete="onSearch"
          @item-select="onIssueSelect"
          :disabled="props.disabled || !isConnected"
          placeholder="Search for JIRA issue (e.g., PROJ-123)"
          :optionLabel="formatIssue"
          :loading="isSearching"
          fluid
        >
          <template #option="slotProps">
            <div class="py-2 flex flex-col gap-1">
              <div class="font-semibold text-blue-600 dark:text-blue-400 text-sm">
                {{ slotProps.option.key }}
              </div>
              <div class="text-gray-900 dark:text-gray-100 text-sm">
                {{ slotProps.option.summary }}
              </div>
              <div class="mt-0.5">
                <span 
                  class="inline-block px-2 py-0.5 rounded text-xs font-semibold uppercase"
                  :class="{
                    'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300': ['to do', 'open'].includes(slotProps.option.status.toLowerCase()),
                    'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300': slotProps.option.status.toLowerCase() === 'in progress',
                    'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300': ['done', 'closed', 'resolved'].includes(slotProps.option.status.toLowerCase()),
                    'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300': !['to do', 'open', 'in progress', 'done', 'closed', 'resolved'].includes(slotProps.option.status.toLowerCase())
                  }"
                >
                  {{ slotProps.option.status }}
                </span>
              </div>
            </div>
          </template>
        </AutoComplete>
        <small class="block mt-1 text-sm text-gray-600 dark:text-gray-400">
          Link this time record to a JIRA issue for worklog sync
        </small>
      </div>
    </div>
  </div>
</template>
