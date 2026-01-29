<template>
  <div v-if="issueKey" class="inline-flex items-center gap-2">
    <!-- Issue Badge with Link -->
    <a 
      :href="issueUrl" 
      target="_blank" 
      rel="noopener"
      :class="badgeClasses"
      v-tooltip.top="tooltipContent"
    >
      <i class="pi pi-external-link text-xs mr-1"></i>
      {{ issueKey }}
    </a>
    
    <!-- Issue Summary (optional) -->
    <span v-if="showSummary && issue" class="text-sm text-gray-700 dark:text-gray-300">
      {{ issue.summary }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useJiraStore } from '@/stores/jira';
import type { JiraIssue } from '@/types';

const props = withDefaults(defineProps<{
  issueKey: string | null | undefined;
  showSummary?: boolean;
  size?: 'small' | 'medium' | 'large';
}>(), {
  showSummary: false,
  size: 'medium'
});

const jiraStore = useJiraStore();
const issue = ref<JiraIssue | null>(null);
const loading = ref(false);

// Fetch issue details if we don't have them
onMounted(async () => {
  if (props.issueKey && jiraStore.hasActiveConnection) {
    try {
      loading.value = true;
      issue.value = await jiraStore.getIssue(props.issueKey);
    } catch (error) {
      console.error('Failed to fetch JIRA issue:', error);
    } finally {
      loading.value = false;
    }
  }
});

const issueUrl = computed(() => {
  if (!props.issueKey || !jiraStore.activeConnection) return '#';
  return `${jiraStore.activeConnection.jira_url}/browse/${props.issueKey}`;
});

// Color-code badge by status
const badgeClasses = computed(() => {
  const baseClasses = 'inline-flex items-center rounded no-underline font-semibold transition-colors';
  
  // Size classes
  const sizeClasses = {
    small: 'px-1.5 py-0.5 text-xs',
    medium: 'px-2 py-1 text-sm',
    large: 'px-3 py-1.5 text-base'
  };
  
  // Status-based colors
  let colorClasses = 'bg-blue-600 dark:bg-blue-500 text-white hover:bg-blue-700 dark:hover:bg-blue-600';
  
  if (issue.value?.status) {
    const status = issue.value.status.toLowerCase();
    
    if (status.includes('done') || status.includes('closed') || status.includes('resolved')) {
      colorClasses = 'bg-green-600 dark:bg-green-500 text-white hover:bg-green-700 dark:hover:bg-green-600';
    } else if (status.includes('progress') || status.includes('review')) {
      colorClasses = 'bg-yellow-600 dark:bg-yellow-500 text-white hover:bg-yellow-700 dark:hover:bg-yellow-600';
    } else if (status.includes('blocked') || status.includes('waiting')) {
      colorClasses = 'bg-red-600 dark:bg-red-500 text-white hover:bg-red-700 dark:hover:bg-red-600';
    }
  }
  
  return `${baseClasses} ${sizeClasses[props.size]} ${colorClasses}`;
});

const tooltipContent = computed(() => {
  if (!issue.value) return 'View in JIRA';
  
  let tooltip = `${issue.value.summary}\n\nStatus: ${issue.value.status}`;
  if (issue.value.assignee) {
    tooltip += `\nAssignee: ${issue.value.assignee}`;
  }
  tooltip += '\n\nClick to view in JIRA';
  return tooltip;
});
</script>
