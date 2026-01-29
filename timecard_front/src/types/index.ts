
export interface RecordAttribute {
  id?: number
  name: string
  parent_id: number | null
  user_id: number
  level_num: number
  color: string | null
}

export interface TimeRecord {
  id?: number
  domain_id: number | string
  category_id: number | string
  title_id: number | string
  timein: string | Date
  timeout: string | Date | null
  external_link: string | null
  notes: string | null
  jira_issue_key?: string | null
  jira_worklog_id?: string | null
  jira_synced?: boolean
  jira_sync_error?: string | null
  last_synced_at?: string | null
}

export type CategoryRecord = {
  timeDiff: number;
  category_id: number | string;
}

export type SummaryData = {
  domainId: number | string;
  totalTime: number;
  categoryRecords: CategoryRecord[];
}

// JIRA-related types
export interface JiraConnection {
  id: number
  jira_url: string
  auth_type: 'api_token' | 'oauth'
  email?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface JiraIssue {
  key: string
  summary: string
  status: string
  assignee: string | null
  issueType: string
  project: string
  description?: string
  created?: string
  updated?: string
}

export interface JiraSyncLog {
  id: number
  time_record_id: number
  jira_issue_key: string
  jira_worklog_id: string | null
  sync_status: 'pending' | 'success' | 'failed'
  sync_error: string | null
  synced_at: string
  synced_by_user_id: number
}

export interface JiraSyncResult {
  success: boolean
  message?: string
  error?: string
  worklog_id?: string
}

export interface JiraBulkSyncResult {
  total: number
  succeeded: number
  failed: number
  errors: Array<{
    record_id: number
    error: string
  }>
}

