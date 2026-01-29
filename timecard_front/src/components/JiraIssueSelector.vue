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
  <div class="jira-issue-selector">
    <!-- Not connected warning -->
    <div v-if="!isConnected" class="no-connection-warning">
      <Message severity="warn" :closable="false">
        <div class="flex items-center gap-2">
          <span>JIRA not connected.</span>
          <RouterLink to="/settings/jira" class="jira-link">
            <Button label="Connect JIRA" size="small" outlined />
          </RouterLink>
        </div>
      </Message>
    </div>

    <!-- Issue selector (when connected) -->
    <div v-else>
      <!-- Display selected issue -->
      <div v-if="selectedIssue && props.modelValue" class="selected-issue">
        <Card>
          <template #content>
            <div class="issue-content">
              <div class="issue-info">
                <div class="issue-key-badge">
                  <a 
                    :href="`${jiraStore.activeConnection?.jira_url}/browse/${selectedIssue.key}`" 
                    target="_blank" 
                    rel="noopener"
                    class="issue-link"
                  >
                    {{ selectedIssue.key }}
                    <i class="pi pi-external-link"></i>
                  </a>
                </div>
                <div class="issue-details">
                  <div class="issue-summary">{{ selectedIssue.summary }}</div>
                  <div class="issue-meta">
                    <span class="status-badge" :class="`status-${selectedIssue.status.toLowerCase().replace(/\s/g, '-')}`">
                      {{ selectedIssue.status }}
                    </span>
                    <span v-if="selectedIssue.assignee" class="assignee">
                      <i class="pi pi-user"></i> {{ selectedIssue.assignee }}
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
      <div v-else class="search-input">
        <label class="input-label">JIRA Issue (Optional)</label>
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
            <div class="issue-option">
              <div class="issue-option-key">{{ slotProps.option.key }}</div>
              <div class="issue-option-summary">{{ slotProps.option.summary }}</div>
              <div class="issue-option-meta">
                <span class="status-badge" :class="`status-${slotProps.option.status.toLowerCase().replace(/\s/g, '-')}`">
                  {{ slotProps.option.status }}
                </span>
              </div>
            </div>
          </template>
        </AutoComplete>
        <small class="help-text">Link this time record to a JIRA issue for worklog sync</small>
      </div>
    </div>
  </div>
</template>

<style scoped>
.jira-issue-selector {
  margin: 8px 0;
}

.no-connection-warning {
  margin-bottom: 12px;
}

.jira-link {
  text-decoration: none;
}

.input-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--text-color);
}

.help-text {
  display: block;
  margin-top: 4px;
  color: var(--text-color-secondary);
  font-size: 0.85rem;
}

.selected-issue {
  margin-bottom: 12px;
}

.issue-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.issue-info {
  flex: 1;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.issue-key-badge {
  flex-shrink: 0;
}

.issue-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  background: var(--primary-color);
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.issue-link:hover {
  background: var(--primary-600);
}

.issue-link i {
  font-size: 0.75rem;
}

.issue-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.issue-summary {
  font-weight: 500;
  color: var(--text-color);
  line-height: 1.4;
}

.issue-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  background: var(--surface-200);
  color: var(--text-color);
}

.status-badge.status-to-do,
.status-badge.status-open {
  background: var(--blue-100);
  color: var(--blue-700);
}

.status-badge.status-in-progress {
  background: var(--yellow-100);
  color: var(--yellow-700);
}

.status-badge.status-done,
.status-badge.status-closed,
.status-badge.status-resolved {
  background: var(--green-100);
  color: var(--green-700);
}

.assignee {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: var(--text-color-secondary);
}

.assignee i {
  font-size: 0.75rem;
}

.search-input {
  margin-bottom: 12px;
}

.issue-option {
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.issue-option-key {
  font-weight: 600;
  color: var(--primary-color);
  font-size: 0.9rem;
}

.issue-option-summary {
  color: var(--text-color);
  font-size: 0.9rem;
}

.issue-option-meta {
  margin-top: 2px;
}
</style>
