<script setup lang="ts">
import { computed } from 'vue';
import { useJiraStore } from '@/stores/jira';
import { useToast } from 'primevue/usetoast';
import type { TimeRecord } from '@/types';

const jiraStore = useJiraStore();
const toast = useToast();

const props = defineProps<{
  record: TimeRecord;
  size?: 'small' | 'normal' | 'large';
  showLabel?: boolean;
}>();

const emit = defineEmits<{
  (e: 'synced'): void;
}>();

// Computed states
const canSync = computed(() => {
  return props.record.id && 
         props.record.jira_issue_key && 
         props.record.timeout && // Must be clocked out
         jiraStore.hasActiveConnection;
});

const isSyncing = computed(() => {
  return props.record.id ? jiraStore.isRecordSyncing(props.record.id) : false;
});

const isSynced = computed(() => {
  return props.record.jira_synced && props.record.jira_worklog_id;
});

const hasError = computed(() => {
  return props.record.jira_sync_error !== null && props.record.jira_sync_error !== undefined;
});

const syncStatus = computed(() => {
  if (isSyncing.value) return 'syncing';
  if (isSynced.value) return 'synced';
  if (hasError.value) return 'error';
  return 'not-synced';
});

const buttonIcon = computed(() => {
  switch (syncStatus.value) {
    case 'syncing': return 'pi pi-spin pi-spinner';
    case 'synced': return 'pi pi-check-circle';
    case 'error': return 'pi pi-exclamation-circle';
    default: return 'pi pi-cloud-upload';
  }
});

const buttonLabel = computed(() => {
  if (!props.showLabel) return '';
  
  switch (syncStatus.value) {
    case 'syncing': return 'Syncing...';
    case 'synced': return 'Synced';
    case 'error': return 'Sync Failed';
    default: return 'Sync to JIRA';
  }
});

const buttonSeverity = computed(() => {
  switch (syncStatus.value) {
    case 'synced': return 'success';
    case 'error': return 'danger';
    default: return 'secondary';
  }
});

const tooltipText = computed(() => {
  if (!canSync.value) {
    if (!props.record.jira_issue_key) return 'No JIRA issue linked';
    if (!props.record.timeout) return 'Clock out before syncing';
    if (!jiraStore.hasActiveConnection) return 'JIRA not connected';
    return 'Cannot sync';
  }
  
  switch (syncStatus.value) {
    case 'syncing': return 'Syncing to JIRA...';
    case 'synced': 
      return `Synced to ${props.record.jira_issue_key}\nLast synced: ${formatDate(props.record.last_synced_at)}`;
    case 'error': 
      return `Sync failed: ${props.record.jira_sync_error}`;
    default: 
      return `Sync to ${props.record.jira_issue_key}`;
  }
});

// Methods
const formatDate = (dateStr: string | null | undefined) => {
  if (!dateStr) return 'Unknown';
  try {
    return new Date(dateStr).toLocaleString();
  } catch {
    return 'Unknown';
  }
};

const syncToJira = async () => {
  if (!canSync.value || !props.record.id) return;

  try {
    const result = await jiraStore.syncRecord(props.record.id);
    
    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: `Time logged to ${props.record.jira_issue_key}`,
        life: 3000
      });
      
      // Update the record with sync info
      props.record.jira_synced = true;
      props.record.jira_worklog_id = result.worklog_id || null;
      props.record.jira_sync_error = null;
      props.record.last_synced_at = new Date().toISOString();
      
      emit('synced');
    } else {
      toast.add({
        severity: 'error',
        summary: 'Sync Failed',
        detail: result.error || 'Failed to sync to JIRA',
        life: 5000
      });
      
      // Update error state
      props.record.jira_synced = false;
      props.record.jira_sync_error = result.error || 'Unknown error';
      props.record.last_synced_at = new Date().toISOString();
    }
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.message || 'Failed to sync to JIRA',
      life: 5000
    });
  }
};
</script>

<template>
  <Button
    :icon="buttonIcon"
    :label="buttonLabel"
    :severity="buttonSeverity"
    :size="size"
    :disabled="!canSync || isSyncing"
    :loading="isSyncing"
    @click="syncToJira"
    v-tooltip.top="tooltipText"
    :class="['jira-sync-button', `sync-status-${syncStatus}`]"
  />
</template>

<style scoped>
.jira-sync-button.sync-status-synced {
  color: var(--green-600);
}

.jira-sync-button.sync-status-error {
  color: var(--red-600);
}

.jira-sync-button.sync-status-syncing {
  color: var(--blue-600);
}
</style>
