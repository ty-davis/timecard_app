<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useJiraStore } from '@/stores/jira';
import { useConfirm } from 'primevue/useconfirm';
import { useToast } from 'primevue/usetoast';

const jiraStore = useJiraStore();
const confirm = useConfirm();
const toast = useToast();

// Form fields
const jiraUrl = ref('');
const email = ref('');
const apiToken = ref('');
const isEditing = ref(false);
const isTesting = ref(false);
const isSaving = ref(false);

// Computed
const hasConnection = computed(() => jiraStore.activeConnection !== null);
const connection = computed(() => jiraStore.activeConnection);

// Load connection on mount
onMounted(async () => {
  try {
    await jiraStore.getConnections();
    if (connection.value) {
      jiraUrl.value = connection.value.jira_url;
      email.value = connection.value.email || '';
      isEditing.value = false;
    }
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to load JIRA connection',
      life: 3000
    });
  }
});

// Methods
const startEdit = () => {
  isEditing.value = true;
};

const cancelEdit = () => {
  if (connection.value) {
    jiraUrl.value = connection.value.jira_url;
    email.value = connection.value.email || '';
    apiToken.value = '';
  } else {
    jiraUrl.value = '';
    email.value = '';
    apiToken.value = '';
  }
  isEditing.value = false;
};

const validateForm = () => {
  if (!jiraUrl.value.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'JIRA URL is required',
      life: 3000
    });
    return false;
  }

  if (!email.value.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Email is required',
      life: 3000
    });
    return false;
  }

  if (!hasConnection.value && !apiToken.value.trim()) {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'API Token is required',
      life: 3000
    });
    return false;
  }

  // Validate URL format
  try {
    new URL(jiraUrl.value);
  } catch {
    toast.add({
      severity: 'warn',
      summary: 'Validation Error',
      detail: 'Invalid JIRA URL format',
      life: 3000
    });
    return false;
  }

  return true;
};

const testConnection = async () => {
  if (!validateForm()) return;

  isTesting.value = true;

  try {
    // If we have a connection, test it
    if (connection.value) {
      const result = await jiraStore.testConnection(connection.value.id);
      
      if (result.success) {
        toast.add({
          severity: 'success',
          summary: 'Connection Successful',
          detail: `Connected to JIRA ${result.server_info?.version || ''}`,
          life: 5000
        });
      } else {
        toast.add({
          severity: 'error',
          summary: 'Connection Failed',
          detail: result.error || 'Unable to connect to JIRA',
          life: 5000
        });
      }
    } else {
      // Create a temporary connection to test
      const tempConnection = await jiraStore.createConnection({
        jira_url: jiraUrl.value.trim(),
        email: email.value.trim(),
        api_token: apiToken.value.trim()
      });

      const result = await jiraStore.testConnection(tempConnection.id);
      
      if (result.success) {
        toast.add({
          severity: 'success',
          summary: 'Connection Successful',
          detail: 'JIRA connection has been saved',
          life: 5000
        });
        isEditing.value = false;
        apiToken.value = ''; // Clear token after save
      } else {
        // Delete the failed connection
        await jiraStore.deleteConnection(tempConnection.id);
        toast.add({
          severity: 'error',
          summary: 'Connection Failed',
          detail: result.error || 'Unable to connect to JIRA',
          life: 5000
        });
      }
    }
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.message || 'Failed to test connection',
      life: 5000
    });
  } finally {
    isTesting.value = false;
  }
};

const saveConnection = async () => {
  if (!validateForm()) return;

  isSaving.value = true;

  try {
    if (connection.value) {
      // Update existing connection
      const updateData: any = {
        jira_url: jiraUrl.value.trim(),
        email: email.value.trim()
      };

      // Only include token if provided
      if (apiToken.value.trim()) {
        updateData.api_token = apiToken.value.trim();
      }

      await jiraStore.updateConnection(connection.value.id, updateData);
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'JIRA connection updated',
        life: 3000
      });
    } else {
      // Create new connection
      await jiraStore.createConnection({
        jira_url: jiraUrl.value.trim(),
        email: email.value.trim(),
        api_token: apiToken.value.trim()
      });
      
      toast.add({
        severity: 'success',
        summary: 'Success',
        detail: 'JIRA connection created',
        life: 3000
      });
    }

    isEditing.value = false;
    apiToken.value = ''; // Clear token after save
  } catch (error: any) {
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: error.message || 'Failed to save connection',
      life: 5000
    });
  } finally {
    isSaving.value = false;
  }
};

const deleteConnection = () => {
  if (!connection.value) return;

  confirm.require({
    message: 'Are you sure you want to delete this JIRA connection? This action cannot be undone.',
    header: 'Delete Connection',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: 'Cancel',
    acceptLabel: 'Delete',
    accept: async () => {
      try {
        await jiraStore.deleteConnection(connection.value!.id);
        
        // Reset form
        jiraUrl.value = '';
        email.value = '';
        apiToken.value = '';
        isEditing.value = false;

        toast.add({
          severity: 'success',
          summary: 'Success',
          detail: 'JIRA connection deleted',
          life: 3000
        });
      } catch (error: any) {
        toast.add({
          severity: 'error',
          summary: 'Error',
          detail: error.message || 'Failed to delete connection',
          life: 5000
        });
      }
    }
  });
};
</script>

<template>
  <div class="jira-connection-setup">
    <ConfirmDialog />
    
    <!-- Connection Status Card -->
    <Card v-if="hasConnection && !isEditing" class="status-card">
      <template #content>
        <div class="connection-info">
          <div class="status-header">
            <i class="pi pi-check-circle" style="color: var(--green-500); font-size: 1.5rem;"></i>
            <div>
              <h3>Connected to JIRA</h3>
              <p class="url">{{ connection?.jira_url }}</p>
            </div>
          </div>
          
          <div class="connection-details">
            <div class="detail-row">
              <span class="label">Email:</span>
              <span class="value">{{ connection?.email }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Connection Type:</span>
              <span class="value">API Token</span>
            </div>
          </div>

          <div class="actions">
            <Button label="Test Connection" icon="pi pi-wifi" @click="testConnection" :loading="isTesting" outlined />
            <Button label="Edit" icon="pi pi-pencil" @click="startEdit" />
            <Button label="Delete" icon="pi pi-trash" @click="deleteConnection" severity="danger" outlined />
          </div>
        </div>
      </template>
    </Card>

    <!-- Connection Form -->
    <Card v-else class="form-card">
      <template #content>
        <form @submit.prevent="saveConnection">
          <div class="form-group">
            <label for="jira-url">JIRA URL *</label>
            <InputText 
              id="jira-url" 
              v-model="jiraUrl" 
              placeholder="https://your-domain.atlassian.net"
              :disabled="isSaving || isTesting"
              style="width: 100%;"
            />
            <small class="help-text">Your JIRA Cloud or Server URL</small>
          </div>

          <div class="form-group">
            <label for="email">Email *</label>
            <InputText 
              id="email" 
              v-model="email" 
              type="email"
              placeholder="you@example.com"
              :disabled="isSaving || isTesting"
              style="width: 100%;"
            />
            <small class="help-text">The email associated with your JIRA account</small>
          </div>

          <div class="form-group">
            <label for="api-token">API Token {{ hasConnection ? '' : '*' }}</label>
            <Password 
              id="api-token" 
              v-model="apiToken" 
              :placeholder="hasConnection ? 'Leave blank to keep current token' : 'Your JIRA API token'"
              :disabled="isSaving || isTesting"
              :feedback="false"
              toggleMask
              style="width: 100%;"
              :inputStyle="{ width: '100%' }"
            />
            <small class="help-text">
              <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank" rel="noopener">
                Generate an API token
              </a> from your Atlassian account settings
            </small>
          </div>

          <Divider />

          <div class="form-actions">
            <Button 
              v-if="hasConnection" 
              label="Cancel" 
              icon="pi pi-times" 
              @click="cancelEdit" 
              outlined
              type="button"
            />
            <Button 
              label="Test & Save" 
              icon="pi pi-check" 
              @click="testConnection"
              :loading="isTesting"
              type="button"
            />
            <Button 
              label="Save" 
              icon="pi pi-save" 
              type="submit"
              :loading="isSaving"
              severity="secondary"
            />
          </div>
        </form>
      </template>
    </Card>

    <!-- Help Card -->
    <Card class="help-card">
      <template #header>
        <div class="card-header">
          <i class="pi pi-info-circle"></i>
          <span>How to get your API Token</span>
        </div>
      </template>
      <template #content>
        <ol class="help-steps">
          <li>Go to <a href="https://id.atlassian.com/manage-profile/security/api-tokens" target="_blank" rel="noopener">Atlassian Account Settings</a></li>
          <li>Click "Create API token"</li>
          <li>Give it a label (e.g., "Timecard App")</li>
          <li>Copy the token and paste it above</li>
        </ol>
        <Message severity="info" :closable="false">
          Your API token is encrypted and stored securely. It's only used to sync time records to JIRA.
        </Message>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.jira-connection-setup {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-card {
  border: 1px solid var(--green-200);
  background: var(--green-50);
}

.connection-info {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.status-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-header h3 {
  margin: 0 0 4px 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.status-header .url {
  margin: 0;
  color: var(--text-color-secondary);
  font-size: 0.9rem;
}

.connection-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--surface-ground);
  border-radius: 6px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-row .label {
  font-weight: 500;
  color: var(--text-color-secondary);
}

.detail-row .value {
  color: var(--text-color);
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
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

.help-text a {
  color: var(--primary-color);
  text-decoration: none;
}

.help-text a:hover {
  text-decoration: underline;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.help-card .card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  font-weight: 600;
  font-size: 1.1rem;
}

.help-steps {
  margin: 0 0 16px 0;
  padding-left: 20px;
}

.help-steps li {
  margin-bottom: 8px;
  line-height: 1.5;
}

.help-steps a {
  color: var(--primary-color);
  text-decoration: none;
}

.help-steps a:hover {
  text-decoration: underline;
}
</style>
