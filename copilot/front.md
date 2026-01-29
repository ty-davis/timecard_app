# Timecard Frontend Analysis

## Overview
The timecard_front project is a Vue 3 + TypeScript time tracking application built with Vite. It allows users to log work sessions with hierarchical categorization (Domain → Category → Title) and provides reporting/visualization features.

## Tech Stack
- **Framework**: Vue 3.5.18 with Composition API
- **Build Tool**: Vite 7.0.6
- **Language**: TypeScript 5.8
- **State Management**: Pinia 3.0.3
- **Routing**: Vue Router 4.5.1
- **UI Library**: PrimeVue 4.3.7 with custom theme
- **Styling**: Tailwind CSS 4.1.12
- **HTTP Client**: Axios 1.11.0

## Project Structure

### Core Files
- `src/main.ts` - App initialization, PrimeVue setup, component registration
- `src/App.vue` - Root component with navigation and routing, popup mode detection
- `src/styles.css` - Global styles
- `src/tailwind-theme.css` - Generated Tailwind theme file

### Key Directories
- `src/router/` - Route definitions and view components
- `src/components/` - Reusable UI components
- `src/stores/` - Pinia state management stores
- `src/api/` - Axios configuration with auth interceptors
- `src/types/` - TypeScript type definitions
- `src/utils/` - Utility functions (time utilities)
- `src/presets/` - PrimeVue theme customization
- `src/config/` - Configuration files

## State Management (Pinia Stores)

### Auth Store (`stores/auth.ts`)
- Manages authentication state (access/refresh tokens)
- Stores tokens in localStorage
- Provides `isLoggedIn` computed property
- Handles logout functionality
- Integrates with Vue Router for redirects

### Time Records Store (`stores/timerecords.ts`)
- Manages time record data (CRUD operations)
- Implements smart data fetching (only requests new data when needed)
- Default date range: 2 weeks ago to 1 week from now
- Provides filtered records by date range
- API endpoints:
  - GET `/timerecords` (with date range params)
  - POST `/timerecords`
  - PUT `/timerecords/:id`
  - DELETE `/timerecords/:id`

### Record Attributes Store (`stores/recordattributes.ts`)
- Manages hierarchical categories (domains, categories, titles)
- Fetches all record attributes
- Updates individual attributes
- API endpoints:
  - GET `/recordattributes`
  - PUT `/recordattributes/:id`

## API Integration

### Configuration (`api/axios.ts`)
- Base URL: `/api` (proxied via Vite)
- Vite proxy target: `VITE_API_TARGET` env var or `http://127.0.0.1:5000`
- **Request Interceptor**: Adds Bearer token to all requests
- **Response Interceptor**: Handles 401 errors with automatic token refresh
  - Attempts to refresh token on 401
  - Retries original request with new token
  - Logs out user if refresh fails

## Data Models

### TimeRecord
```typescript
{
  id?: number
  domain_id: number | string
  category_id: number | string
  title_id: number | string
  timein: string | Date
  timeout: string | Date | null
  external_link: string | null  // e.g., obsidian:// links
  notes: string | null
}
```

### RecordAttribute
```typescript
{
  id?: number
  name: string
  parent_id: number | null
  user_id: number
  level_num: number  // 1=Domain, 2=Category, 3=Title
  color: string | null
}
```

### SummaryData & CategoryRecord
Used for report aggregation by domain/category with time totals.

## Routes & Views

1. **HomeView** (`/`) - Main dashboard
   - New record form (collapsible panel)
   - Open timecards panel (shows unclosed records)
   - History panel with tabs:
     - List view (LittleRecord components)
     - Calendar view
   - Requires login

2. **LoginView** (`/login`) - User authentication

3. **RegisterView** (`/register`) - New user registration

4. **ReportView** (`/report`) - Time tracking reports
   - Aggregates time by domain and category
   - Shows summary cards with time totals
   - Filterable by date range
   - Sorted by total time (descending)

5. **ClockView** (`/clock`) - Live timer display
   - Query params: `domain`, `category`, `timein`
   - Shows elapsed time since timein
   - Displays domain/category names with color coding
   - Popup mode support (window.opener detection)
   - Mobile responsive

6. **RecordView** (`/record/:id`) - View single record details

7. **RecordEditView** (`/record/edit/:id`) - Edit existing record

8. **RecordAttributeView** (`/info/:id`) - View/edit record attributes

9. **AboutView** (`/about`) - About page

## Components

### TimecardForm
- Main form for creating/editing time records
- Three-level hierarchical selection (Domain → Category → Title)
- Uses TextSelect component for autocomplete
- Fields: domain, category, title, external link, timein, timeout, notes
- Clock view integration button for open records
- Delete functionality for existing records

### TextSelect
- Autocomplete component for hierarchical record attributes
- Supports creating new attributes on-the-fly
- Level-aware (1=Domain, 2=Category, 3=Title)
- Parent-child relationship filtering

### Calendar
- Monthly calendar view of time records
- Shows records grouped by day
- Month navigation
- Visual indication of records per day

### LittleRecord
- Compact record display for list views
- Shows domain/category/title with colors
- Time display
- Delete functionality

### SummaryCard
- Report visualization component
- Shows domain/category time summaries
- Visual time bars (relative to max time)

### Nav
- Main navigation component
- Conditional rendering (hidden on `/clock` route)

## Features & Functionality

### Time Tracking
- Create new time records with hierarchical categorization
- "Open timecards" - records without timeout (still running)
- Automatic refresh after record creation/update
- Delete confirmation dialog
- External link support (Obsidian, etc.)

### Hierarchical Organization
- 3-level hierarchy: Domain → Category → Title
- Color coding for visual identification
- Dynamic creation of new categories via autocomplete
- Parent-child relationships

### Reporting
- Aggregate time by domain and category
- Date range filtering (default: 2 weeks ago to 1 week from now)
- Visual time comparison with bars
- Sorted by total time

### Clock View
- Live elapsed time display
- Popup window support for "floating" clock
- Mobile optimized
- Color-coded domain display
- Can be opened from active timecards

### UI/UX
- Responsive design (max-width: 768px for main content)
- Dark mode support via Tailwind
- Collapsible panels
- Tab navigation (List/Calendar views)
- Confirmation dialogs for destructive actions
- Popup mode detection for embedded views

## Authentication Flow
1. User logs in → tokens stored in localStorage
2. All API requests include Bearer token
3. On 401 error → automatic token refresh attempt
4. If refresh succeeds → retry original request
5. If refresh fails → logout and redirect to home

## Development Features
- TypeScript strict mode
- Vue DevTools plugin
- Hot module replacement (HMR)
- Pre-build script generates Tailwind theme
- Vite proxy for API calls (no CORS issues in dev)

## PrimeVue Components Used
- AutoComplete
- Button
- Card
- Checkbox
- ColorPicker
- ConfirmDialog
- DatePicker
- InputText
- Message
- Panel
- Tabs/TabList/Tab/TabPanels/TabPanel

## Potential Enhancement Areas
1. **Offline Support** - No PWA/service worker currently
2. **Data Export** - No export functionality for reports
3. **Bulk Operations** - No multi-select for records
4. **Advanced Filtering** - Limited filtering options in history view
5. **Time Edit** - No easy way to adjust times for past records
6. **Statistics** - Limited analytics/insights beyond basic reports
7. **Notifications** - No reminders for open timecards
8. **Search** - No search functionality for historical records
9. **Keyboard Shortcuts** - No keyboard navigation support
10. **Data Visualization** - Limited charts/graphs (mostly text-based)
