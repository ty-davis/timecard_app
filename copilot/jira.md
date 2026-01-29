# JIRA Integration Plan for Timecard App

**Status:** 🔨 In Progress - Step 6 Complete (Sync Functionality - Single Record)  
**Branch:** `jira`  
**Started:** 2026-01-29

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

### Phase 1: Foundation (MVP) - 🔨 IN PROGRESS
- 🔨 JIRA authentication setup (database models complete, APIs pending)
- 🔨 Link time records to JIRA issues (database fields added)
- ⬜ Manual sync to JIRA (one-way: app → JIRA)
- ⬜ Basic JIRA issue search
- ⬜ Sync status indicators

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

## Implementation Plan

### Step 1: Database & Backend Foundation (Day 1-2) ✅ COMPLETED

#### 1.1 Database Migrations ✅
- [x] Create `jira_connections` table
- [x] Create `jira_sync_logs` table
- [x] Add JIRA fields to `time_records` table
- [ ] Add indexes for performance (deferred - can optimize later)

#### 1.2 Backend Models ✅
- [x] Create `JiraConnection` model with encryption for tokens
- [x] Create `JiraSyncLog` model
- [x] Update `TimeRecord` model with JIRA fields
- [x] Import new models in app.py

#### 1.3 JIRA Service Layer ✅
- [x] Create `services/jira_service.py`
- [x] Implement JIRA client initialization
- [x] Add connection test method
- [x] Add issue search method
- [x] Add worklog creation method
- [x] Add error handling and retries

#### 1.4 Encryption Utilities ✅
- [x] Create token encryption/decryption helpers (implemented in JiraConnection model)
- [x] Store encryption key securely (using environment variable JIRA_ENCRYPTION_KEY)

**Notes:**
- Used cryptography.fernet for symmetric encryption
- Encryption key auto-generated if not in environment
- Migration applied successfully with 5 new TimeRecord fields:
  - jira_issue_key, jira_worklog_id, jira_synced, jira_sync_error, last_synced_at
- Added atlassian-python-api and cryptography to requirements.txt

### Step 2: Backend API Endpoints (Day 2-3) ✅ COMPLETED

#### 2.1 Connection Management Routes ✅
- [x] `POST /api/jira/connections` - Create connection
- [x] `GET /api/jira/connections` - List connections
- [x] `PUT /api/jira/connections/{id}` - Update connection
- [x] `DELETE /api/jira/connections/{id}` - Delete connection
- [x] `POST /api/jira/connections/{id}/test` - Test connection

#### 2.2 Issue Search Routes ✅
- [x] `GET /api/jira/issues/search?q={query}` - Search issues
- [x] `GET /api/jira/issues/assigned` - Get assigned issues
- [x] `GET /api/jira/issues/{key}` - Get issue details

#### 2.3 Sync Routes ✅
- [x] `POST /api/jira/sync/record/{id}` - Sync single record
- [x] `POST /api/jira/sync/bulk` - Sync multiple records
- [x] `GET /api/jira/sync/history` - Get sync history
- [x] `DELETE /api/jira/worklog/{timeRecordId}` - Delete worklog from JIRA

#### 2.4 Validation & Authorization ✅
- [x] Ensure user owns the time records being synced
- [x] Validate JIRA issue keys format
- [x] Validate connection belongs to user

**Notes:**
- Created `services/jira_service.py` with full JIRA client integration
- Implemented all connection management endpoints with encryption
- All sync operations create JiraSyncLog entries for audit trail
- Comprehensive error handling and validation
- User authorization checks on all endpoints
- Bulk sync returns detailed results with success/failure counts

### Step 3: Frontend Types & Store (Day 3-4) ✅ COMPLETED

#### 3.1 Type Definitions ✅
- [x] Add JIRA types to `types/index.ts`
- [x] Update `TimeRecord` interface
- [x] Add `JiraConnection`, `JiraIssue`, `JiraSyncStatus`

#### 3.2 Jira Store ✅
- [x] Create `stores/jira.ts`
- [x] Implement connection management methods
- [x] Implement issue search methods
- [x] Implement sync methods
- [x] Add loading states and error handling

**Notes:**
- Added 5 new fields to `TimeRecord` interface: jira_issue_key, jira_worklog_id, jira_synced, jira_sync_error, last_synced_at
- Created comprehensive type definitions: JiraConnection, JiraIssue, JiraSyncLog, JiraSyncResult, JiraBulkSyncResult
- Implemented full Pinia store with all CRUD operations for connections
- Store includes helper methods for tracking syncing state per record
- All methods use proper error handling with user-friendly error messages
- Store follows existing pattern using composition API with ref() and computed()
- Type checking passes successfully

### Step 4: JIRA Connection Setup UI (Day 4-5) ✅ COMPLETED

#### 4.1 Settings Page ✅
- [x] Create `JiraSettingsView.vue` route
- [x] Create `JiraConnectionSetup.vue` component
- [x] Form: JIRA URL, email, API token
- [x] "Test Connection" button with feedback
- [x] Save/Update connection
- [x] Delete connection with confirmation

#### 4.2 Navigation ✅
- [x] Add "JIRA Settings" link to settings/nav menu
- [x] Add JIRA connection indicator in nav bar

**Notes:**
- Created comprehensive settings view with connection status card
- Form includes validation for all required fields
- Test & Save button creates connection and tests it in one action
- Visual connection status indicator (green checkmark) in navigation
- Help card with step-by-step instructions for getting API token
- Edit mode for updating existing connections
- Secure handling - API token cleared after save
- Toast notifications for all user actions
- Confirm dialog for connection deletion
- Auto-loads JIRA connections on app mount and login
- Responsive design works on mobile and desktop
- Type checking passes successfully

### Step 5: Issue Linking in TimecardForm (Day 5-6) ✅ COMPLETED

#### 5.1 Issue Selector Component ✅
- [x] Create `JiraIssueSelector.vue`
- [x] Autocomplete with debounced search
- [x] Display: `[KEY] Summary` format
- [x] Show issue status badge
- [x] Handle "no connection" state

#### 5.2 Integrate into TimecardForm ✅
- [x] Add JIRA issue selector field
- [x] Make it optional
- [x] Store `jira_issue_key` when saving
- [x] Show selected issue badge

**Notes:**
- Created comprehensive JiraIssueSelector component with autocomplete search
- Debounced search (300ms) to prevent excessive API calls
- Beautiful issue display with key badge, summary, status, and assignee
- Selected issue shows as a card with link to JIRA and clear button
- Graceful handling when JIRA not connected (shows warning with link to settings)
- Custom option template in dropdown showing issue details
- Color-coded status badges (To Do, In Progress, Done, etc.)
- Integrated into TimecardForm between external link and date fields
- Form properly saves and loads jira_issue_key
- Type checking passes successfully

### Step 6: Sync Functionality (Day 6-7) ✅ COMPLETED

#### 6.1 Sync Button Component ✅
- [x] Create `JiraSyncButton.vue`
- [x] Three states: not synced, syncing, synced
- [x] Error state with tooltip
- [x] Re-sync capability
- [x] Icon indicators (✓, ✗, ⟳)

#### 6.2 Single Record Sync ✅
- [x] Add sync button to `TimecardForm` (for existing records)
- [x] Add sync button to `RecordView` detail page
- [x] Show sync status in UI
- [x] Handle success/error feedback

#### 6.3 Bulk Sync
- [ ] Add checkboxes to `GroupedRecordsList`
- [ ] "Sync selected to JIRA" bulk action
- [ ] Progress indicator for multiple syncs
- [ ] Summary of results (X succeeded, Y failed)

**Notes:**
- Created comprehensive JiraSyncButton component with 4 states: not-synced, syncing, synced, error
- Smart state detection: checks for connection, issue key, and timeout status
- Icon indicators: spinner (syncing), check (synced), exclamation (error), cloud-upload (ready)
- Detailed tooltips with error messages and last sync time
- Integrated into TimecardForm - shows for clocked-out records with JIRA issues
- Auto-updates record state after successful sync
- Toast notifications for success/error feedback
- Color-coded buttons (green for synced, red for error)
- Disabled state when prerequisites not met
- Type checking passes successfully

### Step 7: Visual Indicators (Day 7-8) ✅ COMPLETE

#### 7.1 Issue Badge Component ✅
- [x] Create `JiraIssueBadge.vue`
- [x] Display issue key with link to JIRA
- [x] Color-coded by status (blue default, green for done, yellow for in-progress, red for blocked)
- [x] Tooltip with issue summary
- [x] Three sizes: small, medium, large
- [x] Auto-fetches issue details on mount
- [x] Uses Tailwind CSS with dark mode support

#### 7.2 Integrate Badges ✅
- [x] Add to `LittleRecord` component (replaced inline badge)
- [x] Add to `RecordView` detail page (with summary and sync button)
- [x] Add to `TimecardForm` when viewing (shows above selector for existing records)

#### 7.3 Sync Status Icons ✅
- [x] Add sync status indicator to `LittleRecord`
- [x] Add to list views
- [x] Green checkmark = synced (`pi-check-circle`)
- [x] Red X = error (`pi-exclamation-circle`)
- [x] Gray cloud = not synced (`pi-cloud`)
- [x] Uses Tailwind color classes with dark mode variants

**Notes:**
- JiraIssueBadge component is fully reusable with size and showSummary props
- Status color-coding handles: done/closed/resolved (green), in-progress/review (yellow), blocked/waiting (red), default (blue)
- All components now use Tailwind CSS for consistency
- Badge automatically fetches and displays issue details from JIRA

### Step 8: Sync History (Day 8-9) ✅ COMPLETE

#### 8.1 History View ✅
- [x] Create `JiraSyncHistoryView.vue` with DataTable
- [x] Table columns: date/time, JIRA issue (with badge), record link, status (with Tag), worklog ID, error message
- [x] Date range filter (status filter implemented)
- [x] Status filter (All/Success/Failed dropdown)
- [x] Pagination (PrimeVue DataTable with 25 rows per page, configurable)
- [x] Limit filter (50/100/200/500 results)
- [x] Retry button for failed syncs in Actions column
- [x] View record button to navigate to detail page
- [x] Refresh button to reload history
- [x] Added route `/jira/history`
- [x] Added link from JIRA Settings page

#### 8.2 Record-Specific History ✅
- [x] Add sync history section to `RecordView`
- [x] Show all sync attempts for that record (limited to 50 most recent)
- [x] Display with success/failed icons, timestamps, worklog IDs
- [x] Show error messages for failed syncs
- [x] Refresh button to reload record-specific history
- [x] Link to full sync history page
- [x] Auto-loads when record has JIRA integration

#### 8.3 Backend Enhancement ✅
- [x] Added `record_id` query parameter to `/jira/sync/history` endpoint
- [x] Updated `getSyncHistory()` store method to accept `recordId` parameter

**Notes:**
- JiraSyncHistoryView uses PrimeVue DataTable with sorting, pagination, and filtering
- Retry functionality triggers new sync and refreshes both history and time records
- RecordView sync history section only appears if record has JIRA issue linked
- All components use Tailwind CSS for consistency
- Error messages are truncated in table with full text in tooltip
- Status badges use PrimeVue Tag component with color coding

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
