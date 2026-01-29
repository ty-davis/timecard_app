<script setup lang="ts">
import { ref, onMounted, computed, type CSSProperties } from 'vue';
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';
import { useRecordAttributesStore } from '@/stores/recordattributes';
import { useTimeRecordsStore } from '@/stores/timerecords';
import { useJiraStore } from '@/stores/jira';
import { showTime, timeDiff } from '@/utils/timeUtils';
import { useRoute } from 'vue-router';
import { secondaryColor } from '@/utils/colorUtils';
import type { TimeRecord, RecordAttribute, JiraSyncLog } from '@/types';
import JiraIssueBadge from '@/components/JiraIssueBadge.vue';
import JiraSyncButton from '@/components/JiraSyncButton.vue';

const auth = useAuthStore();
const route = useRoute();
const jiraStore = useJiraStore();

const recordId = computed(() => parseInt(route.params.id as string, 10));

const recordAttributesStore = useRecordAttributesStore();
const timeRecordsStore = useTimeRecordsStore();
const { recordAttributes } = storeToRefs(recordAttributesStore);
const {
  timeRecords,
  filteredRecords,
} = storeToRefs(timeRecordsStore);

const record = computed(() => {
  return timeRecords.value.find((r: TimeRecord) => r.id === recordId.value);
})

const timein = computed(() => {
  if (record.value?.timein) {
    return new Date(record.value?.timein);
  }
  return new Date();
});
const timeout = computed(() => {
  return record.value?.timeout ? new Date(record.value?.timeout) : null;
});

onMounted(async () => {
  if (auth.isLoggedIn) {
    try {
      await recordAttributesStore.getRecordAttributes();
      await timeRecordsStore.getTimeRecords();
      await jiraStore.getConnections();
      
      // Load sync history if record has JIRA integration
      if (record.value?.jira_issue_key) {
        await loadSyncHistory();
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        auth.logout();
      }
    }
  }
})

const domainRA = computed(() => {
  return recordAttributes.value.find((ra: RecordAttribute) => ra.id === record.value?.domain_id);
});
const domainStyle = computed(() => {
  const style: CSSProperties = {};
  if (domainRA.value) {
    console.log(domainRA);
    style.borderColor = domainRA.value?.color || '#333333';
    style.backgroundColor = secondaryColor(domainRA.value?.color || '#333333');
  }
  return style;
});

const categoryRA = computed(() => {
  return recordAttributes.value.find((ra: RecordAttribute) => ra.id === record.value?.category_id);
})
const categoryStyle = computed(() => {
  return {};
})

const titleRA = computed(() => {
  return recordAttributes.value.find((ra: RecordAttribute) => ra.id === record.value?.title_id);
})
const titleStyle = computed(() => {
  return {};
})

// Sync history for this record
const syncHistory = ref<JiraSyncLog[]>([]);
const loadingSyncHistory = ref(false);

const loadSyncHistory = async () => {
  if (!record.value?.id) return;
  
  loadingSyncHistory.value = true;
  try {
    syncHistory.value = await jiraStore.getSyncHistory(undefined, 50, record.value.id);
  } catch (error) {
    console.error('Error loading sync history:', error);
  } finally {
    loadingSyncHistory.value = false;
  }
};

const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
};

const getSeverityClass = (status: string): string => {
  if (status === 'success') return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20';
  if (status === 'failed') return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20';
  return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20';
};


</script>
<template>
  <Card>
    <template #content>
      <div class="mb-4">
        <div class="mb-2">
          <span :style="domainStyle" class="border p-1 text-2xl rounded-md font-bold"> {{ domainRA?.name }} </span>
        </div>
        <div>
          <span :style="categoryStyle" class="border-b p-1 text-lg inline-block mb-2"> {{ categoryRA?.name }} </span>
        </div>
        <span :style="titleStyle" class="p-1"> {{ titleRA?.name }}</span>
      </div>

      <!-- JIRA Integration Section -->
      <div v-if="record?.jira_issue_key" class="mb-4 flex items-center gap-3">
        <JiraIssueBadge 
          :issue-key="record.jira_issue_key"
          :show-summary="true"
          size="medium"
        />
        <JiraSyncButton 
          v-if="record.timeout"
          :record="record"
          size="small"
        />
      </div>

      <a :href="`${ record?.external_link }`" class="text-blue-500 hover:underline">External Link</a>

      <div>
        <div>
          {{ timein.toLocaleDateString() }}
        </div>
        <div>
          {{ timein.toLocaleTimeString() }}
          <template v-if="timeout">
            &ndash; {{ timeout.toLocaleTimeString() }}
          </template>
        </div>
      </div>

      <!-- JIRA Sync History Section -->
      <div v-if="record?.jira_issue_key" class="mt-6">
        <Divider />
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-lg font-semibold">JIRA Sync History</h3>
          <Button 
            icon="pi pi-refresh" 
            size="small"
            text
            @click="loadSyncHistory"
            :loading="loadingSyncHistory"
            v-tooltip.top="'Refresh history'"
          />
        </div>
        
        <div v-if="loadingSyncHistory && syncHistory.length === 0" class="text-center py-4 text-gray-500">
          <i class="pi pi-spin pi-spinner text-2xl"></i>
          <p class="mt-2">Loading sync history...</p>
        </div>
        
        <div v-else-if="syncHistory.length === 0" class="text-center py-4 text-gray-500">
          <i class="pi pi-info-circle text-2xl"></i>
          <p class="mt-2">No sync history for this record</p>
        </div>
        
        <div v-else class="space-y-2">
          <div 
            v-for="log in syncHistory" 
            :key="log.id"
            class="flex items-start gap-3 p-3 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div class="flex-shrink-0 mt-1">
              <i 
                :class="log.sync_status === 'success' ? 'pi pi-check-circle text-green-500' : 'pi pi-times-circle text-red-500'"
                class="text-xl"
              ></i>
            </div>
            
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <span :class="getSeverityClass(log.sync_status)" class="px-2 py-0.5 rounded text-xs font-semibold uppercase">
                  {{ log.sync_status }}
                </span>
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDateTime(log.synced_at) }}
                </span>
              </div>
              
              <div v-if="log.jira_worklog_id" class="text-xs text-gray-500 dark:text-gray-400 font-mono">
                Worklog ID: {{ log.jira_worklog_id }}
              </div>
              
              <div v-if="log.sync_error" class="mt-2 text-sm text-red-600 dark:text-red-400">
                <strong>Error:</strong> {{ log.sync_error }}
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="syncHistory.length > 0" class="mt-3 text-center">
          <RouterLink to="/jira/history" class="text-sm text-blue-600 dark:text-blue-400 hover:underline">
            View all sync history →
          </RouterLink>
        </div>
      </div>
    </template>
  </Card>
</template>
