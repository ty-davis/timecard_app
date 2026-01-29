<template>
  <div class="p-4 max-w-7xl mx-auto">
    <Card>
      <template #title>
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold">JIRA Sync History</h1>
          <Button 
            icon="pi pi-refresh" 
            label="Refresh"
            @click="loadHistory"
            :loading="loading"
            size="small"
          />
        </div>
      </template>
      
      <template #content>
        <!-- Filters -->
        <div class="flex flex-wrap gap-4 mb-4">
          <div class="flex flex-col gap-2">
            <label for="statusFilter" class="text-sm font-medium">Status</label>
            <Select 
              id="statusFilter"
              v-model="statusFilter" 
              :options="statusOptions"
              optionLabel="label"
              optionValue="value"
              placeholder="All Statuses"
              class="w-48"
              @change="loadHistory"
            />
          </div>
          
          <div class="flex flex-col gap-2">
            <label for="limitFilter" class="text-sm font-medium">Results</label>
            <Select 
              id="limitFilter"
              v-model="limitFilter" 
              :options="limitOptions"
              placeholder="100"
              class="w-32"
              @change="loadHistory"
            />
          </div>
        </div>

        <!-- Error Display -->
        <Message v-if="jiraStore.error" severity="error" :closable="true" @close="jiraStore.clearError">
          {{ jiraStore.error }}
        </Message>

        <!-- History Table -->
        <DataTable 
          :value="syncHistory" 
          :loading="loading"
          paginator 
          :rows="25"
          :rowsPerPageOptions="[10, 25, 50, 100]"
          stripedRows
          responsiveLayout="scroll"
          class="text-sm"
          :emptyMessage="loading ? 'Loading...' : 'No sync history found'"
        >
          <Column field="synced_at" header="Date/Time" sortable>
            <template #body="slotProps">
              <div class="flex flex-col">
                <span class="font-medium">{{ formatDate(slotProps.data.synced_at) }}</span>
                <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatTime(slotProps.data.synced_at) }}</span>
              </div>
            </template>
          </Column>
          
          <Column field="jira_issue_key" header="JIRA Issue" sortable>
            <template #body="slotProps">
              <JiraIssueBadge 
                :issue-key="slotProps.data.jira_issue_key"
                size="small"
              />
            </template>
          </Column>
          
          <Column field="time_record_id" header="Record" sortable>
            <template #body="slotProps">
              <RouterLink 
                :to="`/record/${slotProps.data.time_record_id}`"
                class="text-blue-600 dark:text-blue-400 hover:underline"
              >
                #{{ slotProps.data.time_record_id }}
              </RouterLink>
            </template>
          </Column>
          
          <Column field="sync_status" header="Status" sortable>
            <template #body="slotProps">
              <Tag 
                :value="slotProps.data.sync_status" 
                :severity="getSeverity(slotProps.data.sync_status)"
                :icon="getStatusIcon(slotProps.data.sync_status)"
              />
            </template>
          </Column>
          
          <Column field="jira_worklog_id" header="Worklog ID" sortable>
            <template #body="slotProps">
              <span v-if="slotProps.data.jira_worklog_id" class="font-mono text-xs text-gray-600 dark:text-gray-400">
                {{ slotProps.data.jira_worklog_id }}
              </span>
              <span v-else class="text-gray-400">—</span>
            </template>
          </Column>
          
          <Column field="sync_error" header="Error" :style="{ minWidth: '200px' }">
            <template #body="slotProps">
              <div v-if="slotProps.data.sync_error" class="text-xs text-red-600 dark:text-red-400 max-w-xs truncate" :title="slotProps.data.sync_error">
                {{ slotProps.data.sync_error }}
              </div>
              <span v-else class="text-gray-400">—</span>
            </template>
          </Column>
          
          <Column header="Actions" :style="{ width: '100px' }">
            <template #body="slotProps">
              <div class="flex gap-2">
                <Button 
                  v-if="slotProps.data.sync_status === 'failed'"
                  icon="pi pi-refresh" 
                  size="small"
                  severity="secondary"
                  text
                  v-tooltip.top="'Retry sync'"
                  @click="retrySync(slotProps.data.time_record_id)"
                  :loading="jiraStore.syncingRecords.has(slotProps.data.time_record_id)"
                />
                <RouterLink :to="`/record/${slotProps.data.time_record_id}`">
                  <Button 
                    icon="pi pi-eye" 
                    size="small"
                    severity="secondary"
                    text
                    v-tooltip.top="'View record'"
                  />
                </RouterLink>
              </div>
            </template>
          </Column>
        </DataTable>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useJiraStore } from '@/stores/jira';
import { useTimeRecordsStore } from '@/stores/timerecords';
import { useToast } from 'primevue/usetoast';
import type { JiraSyncLog } from '@/types';
import JiraIssueBadge from '@/components/JiraIssueBadge.vue';

const jiraStore = useJiraStore();
const timeRecordsStore = useTimeRecordsStore();
const toast = useToast();

const syncHistory = ref<JiraSyncLog[]>([]);
const loading = ref(false);
const statusFilter = ref<string | null>(null);
const limitFilter = ref<number>(100);

const statusOptions = [
  { label: 'All Statuses', value: null },
  { label: 'Success', value: 'success' },
  { label: 'Failed', value: 'failed' }
];

const limitOptions = [50, 100, 200, 500];

onMounted(() => {
  loadHistory();
});

const loadHistory = async () => {
  loading.value = true;
  try {
    console.log('Loading sync history with filters:', {
      status: statusFilter.value,
      limit: limitFilter.value
    });
    
    const result = await jiraStore.getSyncHistory(
      statusFilter.value as 'success' | 'failed' | undefined,
      limitFilter.value
    );
    
    console.log('Sync history result:', result);
    syncHistory.value = result;
    
    console.log('syncHistory.value now:', syncHistory.value);
  } catch (error) {
    console.error('Error loading sync history:', error);
  } finally {
    loading.value = false;
  }
};

const retrySync = async (recordId: number) => {
  try {
    const result = await jiraStore.syncRecord(recordId);
    
    if (result.success) {
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'Record synced successfully',
        life: 3000
      });
      loadHistory(); // Refresh the history
      
      // Also refresh the time records to update sync status
      await timeRecordsStore.getTimeRecords();
    } else {
      toast.add({
        severity: 'error',
        summary: 'Sync Failed',
        detail: result.error || 'Unknown error',
        life: 5000
      });
    }
  } catch (error) {
    console.error('Error retrying sync:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to retry sync',
      life: 3000
    });
  }
};

const getSeverity = (status: string): 'success' | 'danger' | 'info' => {
  if (status === 'success') return 'success';
  if (status === 'failed') return 'danger';
  return 'info';
};

const getStatusIcon = (status: string): string => {
  if (status === 'success') return 'pi pi-check';
  if (status === 'failed') return 'pi pi-times';
  return 'pi pi-clock';
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString();
};

const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString();
};
</script>
