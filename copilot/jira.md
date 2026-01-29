# JIRA Integration Plan for Timecard App

## Overview
This document outlines the complete plan for integrating JIRA with the timecard application, enabling users to sync their time tracking data with JIRA worklogs and link time records to JIRA issues.

## Goals

### Primary Goals
1. Allow users to link time records to JIRA issues
2. Sync time records to JIRA as worklogs
3. Auto-suggest JIRA issues when creating time records
4. Provide visual feedback on sync status

### Secondary Goals
1. Pull JIRA issue details for better context
2. Support multiple JIRA instances per user
3. Bulk sync operations
4. Historical sync for existing records

## Scope

### Phase 1: Foundation (MVP)
- ✅ JIRA authentication setup
- ✅ Link time records to JIRA issues
- ✅ Manual sync to JIRA (one-way: app → JIRA)
- ✅ Basic JIRA issue search
- ✅ Sync status indicators

### Phase 2: Enhanced Experience
- ✅ Auto-suggest JIRA issues in TimecardForm
- ✅ Fetch and display JIRA issue details
- ✅ Bulk sync operations
- ✅ Sync history/audit log

### Phase 3: Advanced (Future)
- ⬜ Two-way sync (JIRA → app)
- ⬜ Automatic sync on save
- ⬜ Multiple JIRA instance support
- ⬜ Conflict resolution
- ⬜ Offline queue for syncs

## Technical Architecture

### Backend Changes

#### New Database Models

**JiraConnection** (User's JIRA credentials)
```python
class JiraConnection(db.Model):
    id: int
    user_id: int  # FK to User
    jira_url: str  # e.g., "https://company.atlassian.net"
    auth_type: str  # "api_token" or "oauth"
    api_token: str  # Encrypted
    email: str  # JIRA email for API token auth
    oauth_access_token: str  # Encrypted, for OAuth
    oauth_refresh_token: str  # Encrypted, for OAuth
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

**JiraSyncLog** (Track sync history)
```python
class JiraSyncLog(db.Model):
    id: int
    time_record_id: int  # FK to TimeRecord
    jira_issue_key: str
    jira_worklog_id: str  # JIRA's worklog ID
    sync_status: str  # "pending", "success", "failed"
    sync_error: str  # Error message if failed
    synced_at: datetime
    synced_by_user_id: int
```

#### TimeRecord Model Updates
```python
# Add new fields to existing TimeRecord model
jira_issue_key: str | None  # e.g., "PROJ-123"
jira_worklog_id: str | None  # JIRA's worklog ID after sync
jira_synced: bool  # Default False
jira_sync_error: str | None  # Last sync error
last_synced_at: datetime | None
```

#### New API Endpoints

**JIRA Connection Management**
```
POST   /api/jira/connections                    # Create JIRA connection
GET    /api/jira/connections                    # List user's connections
PUT    /api/jira/connections/{id}               # Update connection
DELETE /api/jira/connections/{id}               # Delete connection
POST   /api/jira/connections/{id}/test          # Test connection
```

**JIRA Issue Operations**
```
GET    /api/jira/issues/search                  # Search JIRA issues (JQL)
GET    /api/jira/issues/{issueKey}              # Get issue details
GET    /api/jira/issues/assigned                # Get assigned issues
```

**Worklog Sync Operations**
```
POST   /api/jira/sync/record/{id}               # Sync single time record
POST   /api/jira/sync/bulk                      # Sync multiple records
GET    /api/jira/sync/status/{id}               # Get sync status
GET    /api/jira/sync/history                   # Get sync history
DELETE /api/jira/worklog/{timeRecordId}         # Delete worklog from JIRA
```

#### Backend Dependencies
```
pip install atlassian-python-api  # JIRA Python client
pip install cryptography           # For encrypting tokens
```

### Frontend Changes

#### Type Definitions (`types/index.ts`)
```typescript
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
  project: string
  issueType: string
}

export interface JiraSyncStatus {
  synced: boolean
  sync_error: string | null
  last_synced_at: string | null
  jira_worklog_id: string | null
}

// Update TimeRecord interface
export interface TimeRecord {
  // ... existing fields
  jira_issue_key?: string | null
  jira_worklog_id?: string | null
  jira_synced?: boolean
  jira_sync_error?: string | null
  last_synced_at?: string | null
}
```

#### New Components

**1. JiraConnectionSetup.vue** (Settings page)
- Form to configure JIRA connection
- Fields: JIRA URL, email, API token
- "Test Connection" button
- Display connection status

**2. JiraIssueSelector.vue** (For TimecardForm)
- Autocomplete search for JIRA issues
- Display: `[PROJ-123] Issue summary`
- Shows issue status badge
- Optional: Recent issues quick select

**3. JiraSyncButton.vue** (Reusable sync button)
- Shows sync status (synced, pending, error)
- Click to sync/re-sync
- Loading state during sync
- Error tooltip

**4. JiraSyncHistory.vue** (View sync logs)
- Table of sync attempts
- Filters: date range, status
- Retry failed syncs

**5. JiraIssueBadge.vue** (Display issue info)
- Shows JIRA issue key with link
- Color-coded by status
- Tooltip with issue details

#### Modified Components

**TimecardForm.vue**
- Add JIRA issue selector field
- Show sync button for saved records
- Display sync status indicator

**LittleRecord.vue**
- Add JIRA issue badge if linked
- Show sync status icon
- Quick sync button in expanded view

**GroupedRecordsList.vue**
- Bulk sync checkbox selection
- "Sync selected to JIRA" action button

**RecordView.vue** (Detail page)
- Full JIRA issue details section
- Sync history for this record
- Manual sync controls

#### New Pinia Store

**jira.ts**
```typescript
export const useJiraStore = defineStore('jira', () => {
  const connections = ref<JiraConnection[]>([])
  const activeConnection = computed(() => 
    connections.value.find(c => c.is_active)
  )
  
  // Methods
  const getConnections = async () => { /* ... */ }
  const createConnection = async (data) => { /* ... */ }
  const testConnection = async (id) => { /* ... */ }
  const searchIssues = async (query) => { /* ... */ }
  const syncRecord = async (recordId) => { /* ... */ }
  const bulkSync = async (recordIds) => { /* ... */ }
  
  return {
    connections,
    activeConnection,
    getConnections,
    createConnection,
    testConnection,
    searchIssues,
    syncRecord,
    bulkSync,
  }
})
```

#### New Routes
```typescript
{ path: '/settings/jira', component: JiraSettingsView }
{ path: '/settings/jira/sync-history', component: JiraSyncHistoryView }
```

## Implementation Plan

### Step 1: Database & Backend Foundation (Day 1-2)

#### 1.1 Database Migrations
- [ ] Create `jira_connections` table
- [ ] Create `jira_sync_logs` table
- [ ] Add JIRA fields to `time_records` table
- [ ] Add indexes for performance

#### 1.2 Backend Models
- [ ] Create `JiraConnection` model with encryption for tokens
- [ ] Create `JiraSyncLog` model
- [ ] Update `TimeRecord` model with JIRA fields

#### 1.3 JIRA Service Layer
- [ ] Create `services/jira_service.py`
- [ ] Implement JIRA client initialization
- [ ] Add connection test method
- [ ] Add issue search method
- [ ] Add worklog creation method
- [ ] Add error handling and retries

#### 1.4 Encryption Utilities
- [ ] Create token encryption/decryption helpers
- [ ] Store encryption key securely (environment variable)

### Step 2: Backend API Endpoints (Day 2-3)

#### 2.1 Connection Management Routes
- [ ] `POST /api/jira/connections` - Create connection
- [ ] `GET /api/jira/connections` - List connections
- [ ] `PUT /api/jira/connections/{id}` - Update connection
- [ ] `DELETE /api/jira/connections/{id}` - Delete connection
- [ ] `POST /api/jira/connections/{id}/test` - Test connection

#### 2.2 Issue Search Routes
- [ ] `GET /api/jira/issues/search?q={query}` - Search issues
- [ ] `GET /api/jira/issues/assigned` - Get assigned issues
- [ ] `GET /api/jira/issues/{key}` - Get issue details

#### 2.3 Sync Routes
- [ ] `POST /api/jira/sync/record/{id}` - Sync single record
- [ ] `POST /api/jira/sync/bulk` - Sync multiple records
- [ ] `GET /api/jira/sync/history` - Get sync history

#### 2.4 Validation & Authorization
- [ ] Ensure user owns the time records being synced
- [ ] Validate JIRA issue keys format
- [ ] Validate connection belongs to user

### Step 3: Frontend Types & Store (Day 3-4)

#### 3.1 Type Definitions
- [ ] Add JIRA types to `types/index.ts`
- [ ] Update `TimeRecord` interface
- [ ] Add `JiraConnection`, `JiraIssue`, `JiraSyncStatus`

#### 3.2 Jira Store
- [ ] Create `stores/jira.ts`
- [ ] Implement connection management methods
- [ ] Implement issue search methods
- [ ] Implement sync methods
- [ ] Add loading states and error handling

### Step 4: JIRA Connection Setup UI (Day 4-5)

#### 4.1 Settings Page
- [ ] Create `JiraSettingsView.vue` route
- [ ] Create `JiraConnectionSetup.vue` component
- [ ] Form: JIRA URL, email, API token
- [ ] "Test Connection" button with feedback
- [ ] Save/Update connection
- [ ] Delete connection with confirmation

#### 4.2 Navigation
- [ ] Add "JIRA Settings" link to settings/nav menu
- [ ] Add JIRA connection indicator in nav bar

### Step 5: Issue Linking in TimecardForm (Day 5-6)

#### 5.1 Issue Selector Component
- [ ] Create `JiraIssueSelector.vue`
- [ ] Autocomplete with debounced search
- [ ] Display: `[KEY] Summary` format
- [ ] Show issue status badge
- [ ] Handle "no connection" state

#### 5.2 Integrate into TimecardForm
- [ ] Add JIRA issue selector field
- [ ] Make it optional
- [ ] Store `jira_issue_key` when saving
- [ ] Show selected issue badge

### Step 6: Sync Functionality (Day 6-7)

#### 6.1 Sync Button Component
- [ ] Create `JiraSyncButton.vue`
- [ ] Three states: not synced, syncing, synced
- [ ] Error state with tooltip
- [ ] Re-sync capability
- [ ] Icon indicators (✓, ✗, ⟳)

#### 6.2 Single Record Sync
- [ ] Add sync button to `TimecardForm` (for existing records)
- [ ] Add sync button to `RecordView` detail page
- [ ] Show sync status in UI
- [ ] Handle success/error feedback

#### 6.3 Bulk Sync
- [ ] Add checkboxes to `GroupedRecordsList`
- [ ] "Sync selected to JIRA" bulk action
- [ ] Progress indicator for multiple syncs
- [ ] Summary of results (X succeeded, Y failed)

### Step 7: Visual Indicators (Day 7-8)

#### 7.1 Issue Badge Component
- [ ] Create `JiraIssueBadge.vue`
- [ ] Display issue key with link to JIRA
- [ ] Color-coded by status
- [ ] Tooltip with issue summary

#### 7.2 Integrate Badges
- [ ] Add to `LittleRecord` component
- [ ] Add to `RecordView` detail page
- [ ] Add to `TimecardForm` when viewing

#### 7.3 Sync Status Icons
- [ ] Add sync status indicator to `LittleRecord`
- [ ] Add to list views
- [ ] Green checkmark = synced
- [ ] Red X = error
- [ ] Gray = not synced

### Step 8: Sync History (Day 8-9)

#### 8.1 History View
- [ ] Create `JiraSyncHistoryView.vue`
- [ ] Table with: date, record, issue, status, error
- [ ] Date range filter
- [ ] Status filter (success/failed)
- [ ] Pagination

#### 8.2 Record-Specific History
- [ ] Add sync history section to `RecordView`
- [ ] Show all sync attempts for that record
- [ ] Retry button for failed syncs

### Step 9: Error Handling & Edge Cases (Day 9-10)

#### 9.1 Connection Errors
- [ ] Handle invalid credentials
- [ ] Handle network errors
- [ ] Handle JIRA API rate limits
- [ ] User-friendly error messages

#### 9.2 Sync Errors
- [ ] Handle invalid issue keys
- [ ] Handle permission errors (can't log time)
- [ ] Handle duplicate worklog detection
- [ ] Retry logic with exponential backoff

#### 9.3 Data Validation
- [ ] Validate time record has required fields
- [ ] Validate JIRA issue exists
- [ ] Validate user has permissions

### Step 10: Testing & Polish (Day 10-11)

#### 10.1 Backend Testing
- [ ] Test connection creation/deletion
- [ ] Test issue search
- [ ] Test worklog creation
- [ ] Test error scenarios

#### 10.2 Frontend Testing
- [ ] Test connection setup flow
- [ ] Test issue search/selection
- [ ] Test single sync
- [ ] Test bulk sync
- [ ] Test error display

#### 10.3 UI/UX Polish
- [ ] Loading states
- [ ] Success/error toasts
- [ ] Confirmation dialogs
- [ ] Help text/tooltips

### Step 11: Documentation (Day 11)

#### 11.1 User Documentation
- [ ] How to get JIRA API token
- [ ] How to connect JIRA
- [ ] How to link issues
- [ ] How to sync time records
- [ ] Troubleshooting guide

#### 11.2 Developer Documentation
- [ ] API endpoint documentation
- [ ] JIRA service layer documentation
- [ ] Component usage examples

## Data Flow Diagrams

### Connection Setup Flow
```
User → JiraSettingsView → Input credentials → Test connection
  → Success: Save encrypted tokens to DB
  → Failure: Show error, don't save

DB: JiraConnection (user_id, url, email, encrypted_token)
```

### Issue Search Flow
```
User types in JiraIssueSelector
  → Debounced search (300ms)
  → Frontend: jiraStore.searchIssues(query)
  → Backend: GET /api/jira/issues/search?q={query}
  → JIRA API: GET /rest/api/3/search (JQL)
  → Return: [{key, summary, status}, ...]
  → Display in dropdown
```

### Single Record Sync Flow
```
User clicks "Sync to JIRA" button
  → Frontend: jiraStore.syncRecord(recordId)
  → Backend: POST /api/jira/sync/record/{id}
  → Validate: record belongs to user, has jira_issue_key
  → Calculate: time difference (timeout - timein)
  → JIRA API: POST /rest/api/3/issue/{key}/worklog
    Body: {
      timeSpentSeconds: calculated_seconds,
      started: timein (ISO format),
      comment: notes or default message
    }
  → Success:
    - Update TimeRecord: jira_synced=true, jira_worklog_id={id}
    - Create JiraSyncLog: status=success
    - Return success to frontend
  → Failure:
    - Update TimeRecord: jira_sync_error={error}
    - Create JiraSyncLog: status=failed, error={error}
    - Return error to frontend
```

### Bulk Sync Flow
```
User selects multiple records → Clicks "Sync selected"
  → Frontend: jiraStore.bulkSync([id1, id2, id3])
  → Backend: POST /api/jira/sync/bulk
    Body: { record_ids: [id1, id2, id3] }
  → For each record:
    - Attempt sync (same as single record)
    - Track success/failure
  → Return: {
      total: 3,
      succeeded: 2,
      failed: 1,
      errors: [{record_id: id3, error: "..."}]
    }
  → Frontend: Show summary toast
```

## Security Considerations

### Token Storage
- **Backend**: Encrypt API tokens using Fernet (cryptography library)
- **Frontend**: Never expose tokens (only backend has access)
- **Environment**: Encryption key in environment variable (not in code)

### API Security
- **Authentication**: All JIRA endpoints require valid user session
- **Authorization**: Verify user owns the time records
- **Rate Limiting**: Implement rate limiting on JIRA endpoints
- **Input Validation**: Sanitize all user inputs

### JIRA API Token
- **Storage**: Users get token from JIRA settings
- **Permissions**: Token needs worklog edit permissions
- **Scope**: Recommend creating token with minimal permissions

## Testing Strategy

### Unit Tests
- JIRA service methods (mock JIRA API responses)
- Encryption/decryption helpers
- TimeRecord JIRA field validations

### Integration Tests
- Connection creation flow (with mock JIRA)
- Issue search (with mock JIRA)
- Worklog sync (with mock JIRA)

### Manual Testing Checklist
- [ ] Connect to real JIRA instance
- [ ] Search for real issues
- [ ] Sync time record to real issue
- [ ] Verify worklog appears in JIRA
- [ ] Test error scenarios (invalid token, wrong issue key)
- [ ] Test with closed/resolved issues
- [ ] Test with issues user can't access

## Future Enhancements (Post-Phase 1)

### Two-Way Sync
- Pull JIRA worklogs into app
- Detect changes in JIRA
- Conflict resolution UI

### Multiple JIRA Instances
- Support multiple connections per user
- Select connection per domain/project
- Connection-specific sync

### Advanced Sync Options
- Automatic sync on save (opt-in)
- Sync queue for offline mode
- Scheduled background sync
- Webhook listener for JIRA changes

### Reporting
- Time logged to JIRA vs not logged
- Sync success rate
- Most-used JIRA projects/issues

### Team Features
- Shared JIRA connections (for teams)
- Admin-managed JIRA config
- Team sync reports

## Migration Plan for Existing Data

### Backfilling JIRA Issue Keys
For users with existing time records that need JIRA linking:

1. **Option 1: Manual UI**
   - Provide bulk edit interface
   - User selects records and assigns JIRA issues
   - Sync in bulk

2. **Option 2: External Link Parsing**
   - If `external_link` contains JIRA URLs
   - Parse issue key from URL
   - Auto-populate `jira_issue_key`
   - Prompt user to verify

3. **Option 3: Notes Parsing**
   - Search `notes` field for issue key patterns (e.g., "PROJ-123")
   - Suggest matches to user
   - User confirms before linking

## Success Metrics

### Phase 1 Success Criteria
- [ ] 80% of users can successfully connect JIRA
- [ ] Avg time to first successful sync < 5 minutes
- [ ] Sync success rate > 95%
- [ ] Sync latency < 3 seconds per record

### User Feedback
- [ ] Post-setup survey: ease of use
- [ ] Track: connection errors
- [ ] Track: sync failures
- [ ] Collect: feature requests

## Timeline Estimate

- **Phase 1 (MVP)**: ~11 days (2 weeks)
- **Phase 2 (Enhanced)**: ~5-7 days
- **Phase 3 (Advanced)**: ~10-14 days

**Total for Phase 1**: Approximately 2 weeks of focused development

## Dependencies & Prerequisites

### Required Before Starting
- [ ] JIRA instance for testing (Cloud or Server)
- [ ] Test JIRA account with worklog permissions
- [ ] Test JIRA project with issues
- [ ] API token generated

### Backend Dependencies
```bash
pip install atlassian-python-api
pip install cryptography
```

### Frontend Dependencies
```bash
# No new dependencies needed
# Uses existing: axios, pinia, primevue
```

## Questions to Answer Before Implementation

1. **JIRA Type**: Cloud, Server, or Data Center? (Affects API endpoints)
2. **Authentication**: Start with API tokens only, or support OAuth too?
3. **Multi-tenant**: Support multiple JIRA instances per user?
4. **Worklog Comments**: What should default comment be? User notes, or custom message?
5. **Time Rounding**: JIRA uses minutes, should we round seconds?
6. **Conflict Handling**: What if worklog already exists for this time period?
7. **Delete Sync**: Should deleting a time record also delete JIRA worklog?
8. **Required Fields**: Should JIRA issue be required when sync is enabled?

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| JIRA API changes | High | Version API calls, monitor JIRA changelog |
| Rate limiting | Medium | Implement backoff, queue syncs |
| Token expiration | Medium | Handle 401 errors, prompt re-auth |
| User permissions | Medium | Clear error messages, permission checks |
| Network failures | Medium | Retry logic, sync queue |
| Large bulk syncs | Low | Batch processing, progress indicators |

## Conclusion

This plan provides a comprehensive roadmap for integrating JIRA with the timecard application. Phase 1 delivers core value (linking issues and syncing time) with reasonable complexity. Future phases can build on this foundation based on user feedback and needs.

**Next Steps:**
1. Review and approve this plan
2. Answer outstanding questions
3. Set up JIRA test environment
4. Begin implementation with Step 1
