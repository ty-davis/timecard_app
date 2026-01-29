import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/axios';
import type { 
  JiraConnection, 
  JiraIssue, 
  JiraSyncLog, 
  JiraSyncResult,
  JiraBulkSyncResult 
} from '@/types';

export const useJiraStore = defineStore('jira', () => {
  // State
  const connections = ref<JiraConnection[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);
  const syncingRecords = ref<Set<number>>(new Set());

  // Computed
  const activeConnection = computed(() => 
    connections.value.find(c => c.is_active) || null
  );

  const hasActiveConnection = computed(() => 
    !!activeConnection.value
  );

  // Connection Management Methods
  const getConnections = async (): Promise<void> => {
    isLoading.value = true;
    error.value = null;
    
    try {
      const response = await api.get('/jira/connections');
      connections.value = response.data.connections;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to fetch JIRA connections';
      console.error('Error fetching JIRA connections:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const createConnection = async (data: {
    jira_url: string;
    email: string;
    api_token: string;
  }): Promise<JiraConnection> => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post('/jira/connections', data);
      connections.value.push(response.data.connection);
      return response.data.connection;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to create JIRA connection';
      console.error('Error creating JIRA connection:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const updateConnection = async (
    connectionId: number, 
    data: Partial<{
      jira_url: string;
      email: string;
      api_token: string;
      is_active: boolean;
    }>
  ): Promise<JiraConnection> => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.put(`/jira/connections/${connectionId}`, data);
      const updatedConnection = response.data.connection;
      
      // Update in local state
      const index = connections.value.findIndex(c => c.id === connectionId);
      if (index !== -1) {
        connections.value[index] = updatedConnection;
      }
      
      return updatedConnection;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update JIRA connection';
      console.error('Error updating JIRA connection:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const deleteConnection = async (connectionId: number): Promise<void> => {
    isLoading.value = true;
    error.value = null;

    try {
      await api.delete(`/jira/connections/${connectionId}`);
      
      // Remove from local state
      connections.value = connections.value.filter(c => c.id !== connectionId);
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to delete JIRA connection';
      console.error('Error deleting JIRA connection:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const testConnection = async (connectionId: number): Promise<{
    success: boolean;
    error?: string;
    server_info?: any;
  }> => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post(`/jira/connections/${connectionId}/test`);
      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Connection test failed';
      error.value = errorMsg;
      return {
        success: false,
        error: errorMsg
      };
    } finally {
      isLoading.value = false;
    }
  };

  // Issue Operations Methods
  const searchIssues = async (query: string): Promise<JiraIssue[]> => {
    if (!query.trim()) {
      return [];
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/jira/issues/search', {
        params: { q: query }
      });
      return response.data.issues;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to search JIRA issues';
      console.error('Error searching JIRA issues:', err);
      return [];
    } finally {
      isLoading.value = false;
    }
  };

  const getIssue = async (issueKey: string): Promise<JiraIssue | null> => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get(`/jira/issues/${issueKey}`);
      return response.data.issue;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to get JIRA issue';
      console.error('Error getting JIRA issue:', err);
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const getAssignedIssues = async (): Promise<JiraIssue[]> => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/jira/issues/assigned');
      return response.data.issues;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to get assigned issues';
      console.error('Error getting assigned issues:', err);
      return [];
    } finally {
      isLoading.value = false;
    }
  };

  // Sync Operations Methods
  const syncRecord = async (recordId: number): Promise<JiraSyncResult> => {
    syncingRecords.value.add(recordId);
    error.value = null;

    try {
      const response = await api.post(`/jira/sync/record/${recordId}`);
      return {
        success: true,
        message: response.data.message,
        worklog_id: response.data.worklog_id
      };
    } catch (err: any) {
      const errorMsg = err.response?.data?.error || 'Failed to sync record';
      error.value = errorMsg;
      return {
        success: false,
        error: errorMsg
      };
    } finally {
      syncingRecords.value.delete(recordId);
    }
  };

  const bulkSync = async (recordIds: number[]): Promise<JiraBulkSyncResult> => {
    recordIds.forEach(id => syncingRecords.value.add(id));
    error.value = null;

    try {
      const response = await api.post('/jira/sync/bulk', { record_ids: recordIds });
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to bulk sync records';
      console.error('Error bulk syncing records:', err);
      throw err;
    } finally {
      recordIds.forEach(id => syncingRecords.value.delete(id));
    }
  };

  const getSyncHistory = async (
    status?: 'success' | 'failed' | null,
    limit?: number,
    recordId?: number
  ): Promise<JiraSyncLog[]> => {
    isLoading.value = true;
    error.value = null;

    try {
      const params: any = {};
      if (status) params.status = status;
      if (limit) params.limit = limit;
      if (recordId) params.record_id = recordId;

      console.log('getSyncHistory API call with params:', params);
      const response = await api.get('/jira/sync/history', { params });
      console.log('getSyncHistory API response:', response.data);
      return response.data.history;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to get sync history';
      console.error('Error getting sync history:', err);
      console.error('Error response:', err.response);
      return [];
    } finally {
      isLoading.value = false;
    }
  };

  const deleteWorklog = async (timeRecordId: number): Promise<boolean> => {
    syncingRecords.value.add(timeRecordId);
    error.value = null;

    try {
      await api.delete(`/jira/worklog/${timeRecordId}`);
      return true;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to delete worklog';
      console.error('Error deleting worklog:', err);
      return false;
    } finally {
      syncingRecords.value.delete(timeRecordId);
    }
  };

  // Helper Methods
  const isRecordSyncing = (recordId: number): boolean => {
    return syncingRecords.value.has(recordId);
  };

  const clearError = () => {
    error.value = null;
  };

  return {
    // State
    connections,
    isLoading,
    error,
    syncingRecords,

    // Computed
    activeConnection,
    hasActiveConnection,

    // Connection Management
    getConnections,
    createConnection,
    updateConnection,
    deleteConnection,
    testConnection,

    // Issue Operations
    searchIssues,
    getIssue,
    getAssignedIssues,

    // Sync Operations
    syncRecord,
    bulkSync,
    getSyncHistory,
    deleteWorklog,

    // Helpers
    isRecordSyncing,
    clearError
  };
});
