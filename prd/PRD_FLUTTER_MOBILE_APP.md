# PRD: Property Fielder Inspector - Flutter Mobile App

**Document Version:** 1.0.0
**Last Updated:** December 31, 2024
**Status:** In Development
**Platform:** iOS & Android (Flutter)

---

## 1. Executive Summary

### 1.1 Purpose

The Property Fielder Inspector mobile app enables field inspectors to efficiently manage their daily inspection jobs, capture evidence, and sync data with the Property Fielder backend. The app is designed for offline-first operation in areas with poor connectivity.

### 1.2 Target Users

- **Primary:** Field Inspectors (Gas Safe, EICR, Asbestos, Fire Safety, etc.)
- **Secondary:** Housing Officers, Surveyors

### 1.3 Key Objectives

1. Enable inspectors to view and manage assigned jobs
2. Provide GPS-verified check-in/check-out functionality
3. Capture photo evidence with GPS tagging and timestamps
4. Collect digital signatures for proof of service
5. Support offline operation with automatic sync
6. Implement lone worker safety features (panic button, safety timer)
7. Integrate with inspection templates for structured data capture

---

## 2. Technical Architecture

### 2.1 Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | Flutter 3.x |
| Language | Dart |
| State Management | Provider + GetIt |
| HTTP Client | Dio + Retrofit |
| Local Storage | Hive (NoSQL) |
| Background Tasks | WorkManager |
| Maps | Google Maps Flutter |
| Camera | camera + image_picker |
| Location | geolocator |
| Signatures | signature package |

### 2.2 Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                      Presentation Layer                      │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ Screens │ │ Widgets │ │Providers│ │  Theme  │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
├─────────────────────────────────────────────────────────────┤
│                       Domain Layer                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │   Models    │ │ Repositories│ │  Use Cases  │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│                        Data Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ API Client  │ │ Local DB    │ │ Sync Engine │           │
│  │  (Retrofit) │ │   (Hive)    │ │(WorkManager)│           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Backend Integration

**Base URL:** Configured per environment (dev/staging/prod)
**Authentication:** Session-based with Odoo (migrating to JWT)
**Protocol:** JSON-RPC over HTTPS

---

## 3. Functional Requirements

### 3.1 Authentication (FR-AUTH)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-AUTH-1 | Login with username/password | HIGH |
| FR-AUTH-2 | Persist session securely (encrypted storage) | HIGH |
| FR-AUTH-3 | Auto-logout after 24 hours inactivity | MEDIUM |
| FR-AUTH-4 | Biometric authentication (fingerprint/face) | LOW |
| FR-AUTH-5 | Remember last logged-in inspector | MEDIUM |

### 3.2 Job Management (FR-JOB)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-JOB-1 | View list of assigned jobs for today | HIGH |
| FR-JOB-2 | Filter jobs by status (pending/in-progress/completed) | HIGH |
| FR-JOB-3 | View job details (property, schedule, type, notes) | HIGH |
| FR-JOB-4 | View job location on map | HIGH |
| FR-JOB-5 | Navigate to job location (open in Google/Apple Maps) | HIGH |
| FR-JOB-6 | View historical jobs (past 7 days) | MEDIUM |
| FR-JOB-7 | Search jobs by address or customer name | MEDIUM |

### 3.3 Route Management (FR-ROUTE)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-ROUTE-1 | View assigned route for the day | HIGH |
| FR-ROUTE-2 | See all jobs on route map with driving directions | HIGH |
| FR-ROUTE-3 | View optimized job sequence | HIGH |
| FR-ROUTE-4 | See estimated travel times between jobs | MEDIUM |
| FR-ROUTE-5 | Re-sequence jobs manually if needed | LOW |

### 3.4 Check-In/Check-Out (FR-CHECKIN)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-CHECKIN-1 | Check in to job with GPS location capture | HIGH |
| FR-CHECKIN-2 | Validate check-in within geofence (configurable radius) | HIGH |
| FR-CHECKIN-3 | Allow geofence override with reason | HIGH |
| FR-CHECKIN-4 | Check out from job with GPS location | HIGH |
| FR-CHECKIN-5 | Track time spent on job | HIGH |
| FR-CHECKIN-6 | Enforce Section 11 compliance (24-hour tenant notice) | HIGH |
| FR-CHECKIN-7 | Allow emergency access override with documented reason | HIGH |

### 3.5 Photo Capture (FR-PHOTO)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-PHOTO-1 | Capture photos using device camera | HIGH |
| FR-PHOTO-2 | Auto-tag photos with GPS coordinates | HIGH |
| FR-PHOTO-3 | Auto-tag photos with timestamp | HIGH |
| FR-PHOTO-4 | Burn timestamp/GPS watermark into image pixels | HIGH |
| FR-PHOTO-5 | Categorize photos (before/during/after/defect) | HIGH |
| FR-PHOTO-6 | Add caption/notes to photos | MEDIUM |
| FR-PHOTO-7 | View photo gallery for job | HIGH |
| FR-PHOTO-8 | Delete unsynced photos | MEDIUM |
| FR-PHOTO-9 | Compress photos for sync (configurable quality) | MEDIUM |
| FR-PHOTO-10 | Link photos to specific inspection checklist items | MEDIUM |

### 3.6 Digital Signatures (FR-SIG)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SIG-1 | Capture signature using touch interface | HIGH |
| FR-SIG-2 | Record signer name and role | HIGH |
| FR-SIG-3 | Capture GPS location at signing | HIGH |
| FR-SIG-4 | Store device/IP info for audit trail | HIGH |
| FR-SIG-5 | Generate SHA-256 hash for signature integrity | HIGH |
| FR-SIG-6 | Allow signature clear and retry | HIGH |
| FR-SIG-7 | Support multiple signatures per job | MEDIUM |

### 3.7 Notes & Voice (FR-NOTES)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-NOTES-1 | Add text notes to job | HIGH |
| FR-NOTES-2 | Categorize notes (general/issue/follow-up/safety) | MEDIUM |
| FR-NOTES-3 | Set note priority (low/normal/high/urgent) | MEDIUM |
| FR-NOTES-4 | Record voice notes | LOW |
| FR-NOTES-5 | Transcribe voice notes to text | LOW |

### 3.8 Inspection Templates (FR-TEMPLATE)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-TEMPLATE-1 | Download inspection templates from backend | HIGH |
| FR-TEMPLATE-2 | Display template sections and items in sequence | HIGH |
| FR-TEMPLATE-3 | Support response types: yes/no, severity, numeric, text | HIGH |
| FR-TEMPLATE-4 | Show conditional follow-up questions | HIGH |
| FR-TEMPLATE-5 | Auto-create defects based on trigger conditions | HIGH |
| FR-TEMPLATE-6 | Require photos for specific items/conditions | HIGH |
| FR-TEMPLATE-7 | Show completion progress bar | MEDIUM |
| FR-TEMPLATE-8 | Support offline template execution | HIGH |
| FR-TEMPLATE-9 | Calculate pass/fail/conditional result | HIGH |

### 3.9 Safety & Lone Worker (FR-SAFETY)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SAFETY-1 | Start safety timer with configurable duration | HIGH |
| FR-SAFETY-2 | Extend safety timer | HIGH |
| FR-SAFETY-3 | Cancel/complete safety timer | HIGH |
| FR-SAFETY-4 | PANIC button with immediate alert | HIGH |
| FR-SAFETY-5 | Send GPS location with panic alert | HIGH |
| FR-SAFETY-6 | Visual countdown timer on screen | HIGH |
| FR-SAFETY-7 | Vibration/sound alert before timer expires | MEDIUM |
| FR-SAFETY-8 | Auto-start timer on check-in (configurable) | MEDIUM |

### 3.10 Offline & Sync (FR-SYNC)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-SYNC-1 | Store all data locally in Hive database | HIGH |
| FR-SYNC-2 | Queue photos/signatures for upload when offline | HIGH |
| FR-SYNC-3 | Background sync every 15 minutes when online | HIGH |
| FR-SYNC-4 | Manual sync trigger button | HIGH |
| FR-SYNC-5 | Show sync status indicator (pending items count) | HIGH |
| FR-SYNC-6 | Retry failed uploads automatically | HIGH |
| FR-SYNC-7 | Handle sync conflicts (server wins strategy) | MEDIUM |
| FR-SYNC-8 | Show last sync timestamp | MEDIUM |

---

## 4. Screen Specifications

### 4.1 Screen Flow Diagram

```
┌─────────┐    ┌─────────┐    ┌───────────┐
│ Splash  │───▶│  Login  │───▶│ Dashboard │
└─────────┘    └─────────┘    └─────┬─────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              ┌──────────┐   ┌──────────┐   ┌──────────┐
              │ Job List │   │Route Map │   │ Settings │
              └────┬─────┘   └──────────┘   └──────────┘
                   │
                   ▼
              ┌──────────┐
              │Job Detail│
              └────┬─────┘
                   │
     ┌─────────┬───┼───┬─────────┐
     ▼         ▼       ▼         ▼
┌────────┐┌────────┐┌────────┐┌────────┐
│ Photos ││Signature││ Notes ││Template│
└────────┘└────────┘└────────┘└────────┘
```

### 4.2 Screen List

| Screen | Purpose | Priority |
|--------|---------|----------|
| Splash | App loading, auto-login check | HIGH |
| Login | User authentication | HIGH |
| Dashboard | Today's overview, quick stats | HIGH |
| Job List | List of assigned jobs | HIGH |
| Job Detail | Full job information | HIGH |
| Job Map | Single job on map | HIGH |
| Route Map | All route jobs on map | HIGH |
| Route List | Route jobs in sequence | HIGH |
| Photo Gallery | View/capture photos for job | HIGH |
| Photo Capture | Camera interface | HIGH |
| Signature Capture | Signature pad | HIGH |
| Note List | View/add notes | HIGH |
| Note Add | Add new note | HIGH |
| Template Execution | Fill inspection template | HIGH |
| Safety Timer | Timer display and controls | HIGH |
| Sync Status | Sync queue and status | MEDIUM |
| Settings | App configuration | MEDIUM |
| Profile | Inspector profile | LOW |

---

## 5. API Endpoints

### 5.1 Authentication

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/mobile/api/auth/login` | POST | `{username, password}` | `{success, user_id, inspector_id, session_id}` |

### 5.2 Jobs

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mobile/api/jobs/my` | GET | Get assigned jobs (query: date, status) |
| `/mobile/api/jobs/{id}` | GET | Get job detail |
| `/mobile/api/jobs/{id}/checkin` | POST | Check in to job |
| `/mobile/api/jobs/{id}/checkout` | POST | Check out from job |
| `/mobile/api/jobs/{id}/photos` | POST | Upload photo |
| `/mobile/api/jobs/{id}/signature` | POST | Capture signature |
| `/mobile/api/jobs/{id}/notes` | POST | Add note |

### 5.3 Routes

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mobile/api/routes/my` | GET | Get assigned routes (query: date) |

### 5.4 Inspection Templates

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mobile/api/templates` | GET | Get available templates |
| `/mobile/api/templates/{id}` | GET | Get template detail with sections/items |
| `/mobile/api/inspections/{id}/responses` | POST | Submit template responses |

### 5.5 Safety

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mobile/api/safety/timer/start` | POST | Start safety timer |
| `/mobile/api/safety/timer/extend` | POST | Extend timer |
| `/mobile/api/safety/timer/cancel` | POST | Cancel/complete timer |
| `/mobile/api/safety/panic` | POST | Trigger panic button |
| `/mobile/api/safety/status` | GET | Get active timer status |

### 5.6 Sync

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mobile/api/sync` | POST | Bulk sync data |
| `/mobile/api/device/register` | POST | Register mobile device |

---

## 6. Data Models (Local)

### 6.1 Hive Boxes

| Box Name | Model | Purpose |
|----------|-------|---------|
| `auth_box` | AuthState | Session, tokens, user info |
| `jobs_box` | Job | Cached jobs |
| `routes_box` | Route | Cached routes |
| `photos_box` | Photo | Pending/synced photos |
| `signatures_box` | Signature | Pending/synced signatures |
| `checkins_box` | CheckIn | Check-in/out records |
| `notes_box` | Note | Job notes |
| `templates_box` | Template | Inspection templates |
| `responses_box` | Response | Template responses |
| `sync_queue_box` | SyncItem | Pending sync items |

### 6.2 Key Models

```dart
@HiveType(typeId: 0)
class Job extends HiveObject {
  @HiveField(0) int id;
  @HiveField(1) String jobNumber;
  @HiveField(2) String name;
  @HiveField(3) String status;
  @HiveField(4) String? scheduledDate;
  @HiveField(5) String? scheduledTime;
  @HiveField(6) String? address;
  @HiveField(7) double? latitude;
  @HiveField(8) double? longitude;
  @HiveField(9) String jobType;
  @HiveField(10) int? templateId;
  @HiveField(11) bool synced;
}

@HiveType(typeId: 1)
class Photo extends HiveObject {
  @HiveField(0) String localId;  // UUID for local reference
  @HiveField(1) int? serverId;   // null until synced
  @HiveField(2) int jobId;
  @HiveField(3) String localPath;
  @HiveField(4) String category;
  @HiveField(5) String? caption;
  @HiveField(6) double? latitude;
  @HiveField(7) double? longitude;
  @HiveField(8) DateTime capturedAt;
  @HiveField(9) bool synced;
  @HiveField(10) int retryCount;
}
```

---

## 7. Non-Functional Requirements

### 7.1 Performance

| NFR | Target | Priority |
|-----|--------|----------|
| App launch time | < 3 seconds | HIGH |
| Screen transition | < 300ms | HIGH |
| Photo capture to preview | < 1 second | HIGH |
| Sync completion (10 photos) | < 30 seconds on 4G | MEDIUM |
| Offline storage capacity | 5000 photos, 1000 jobs | HIGH |

### 7.2 Reliability

| NFR | Target | Priority |
|-----|--------|----------|
| Crash-free sessions | > 99.5% | HIGH |
| Sync success rate | > 99% (with retry) | HIGH |
| GPS accuracy | < 10 meters | HIGH |
| Data loss prevention | Zero data loss offline | HIGH |

### 7.3 Security

| NFR | Requirement | Priority |
|-----|-------------|----------|
| Storage encryption | All local data encrypted | HIGH |
| Session management | Auto-expire after 24 hours | HIGH |
| Certificate pinning | Pin SSL certificates | MEDIUM |
| Root/jailbreak detection | Warn on compromised devices | LOW |

### 7.4 Usability

| NFR | Requirement | Priority |
|-----|-------------|----------|
| Offline indicator | Clear visual when offline | HIGH |
| Loading states | Skeleton screens, not spinners | MEDIUM |
| Error messages | User-friendly, actionable | HIGH |
| Accessibility | WCAG 2.1 AA compliance | MEDIUM |

---

## 8. Implementation Phases

### Phase 1: Core Foundation (Weeks 1-2)
- [ ] Project structure and architecture setup
- [ ] Authentication flow (login/logout)
- [ ] Base API client with error handling
- [ ] Hive database setup and models
- [ ] Basic navigation and routing

### Phase 2: Job Management (Weeks 3-4)
- [ ] Job list screen with filtering
- [ ] Job detail screen
- [ ] Check-in/check-out functionality
- [ ] GPS location service
- [ ] Navigation to job location

### Phase 3: Evidence Capture (Weeks 5-6)
- [ ] Photo capture with camera
- [ ] Photo gallery and viewer
- [ ] GPS tagging and timestamp watermark
- [ ] Signature capture pad
- [ ] Notes creation

### Phase 4: Routes & Maps (Week 7)
- [ ] Route list and detail
- [ ] Map view with all jobs
- [ ] Turn-by-turn navigation launch

### Phase 5: Offline & Sync (Week 8)
- [ ] Sync queue management
- [ ] Background sync with WorkManager
- [ ] Conflict resolution
- [ ] Sync status UI

### Phase 6: Safety Features (Week 9)
- [ ] Safety timer UI and logic
- [ ] Panic button
- [ ] Emergency alert integration

### Phase 7: Inspection Templates (Weeks 10-11)
- [ ] Template download and caching
- [ ] Template execution UI
- [ ] Response capture
- [ ] Defect auto-creation

### Phase 8: Polish & Release (Week 12)
- [ ] UI/UX refinement
- [ ] Performance optimization
- [ ] Testing and bug fixes
- [ ] App store preparation

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Model serialization/deserialization
- Repository methods
- Provider state management
- Utility functions

### 9.2 Widget Tests
- Screen rendering
- User interactions
- Form validation

### 9.3 Integration Tests
- API client with mock server
- Database operations
- Sync flow

### 9.4 E2E Tests (Playwright/Appium)
- Complete user flows
- Offline scenarios
- Error recovery

---

## 10. Success Metrics

| Metric | Target |
|--------|--------|
| App Store rating | > 4.5 stars |
| Daily active users | > 80% of inspectors |
| Sync failure rate | < 1% |
| Average check-in time | < 30 seconds |
| Photo upload success rate | > 99% |
| Crash-free sessions | > 99.5% |

---

## 11. Appendix

### 11.1 Glossary

| Term | Definition |
|------|------------|
| Job | A scheduled inspection task at a property |
| Route | An optimized sequence of jobs for a day |
| Check-in | GPS-verified arrival at job location |
| Geofence | Configurable radius around job location |
| Safety Timer | Lone worker protection countdown |
| Template | Structured inspection checklist |
| Defect | Issue found during inspection |

### 11.2 Related Documents

- PRD_FIELD_SERVICE_MOBILE.md (Backend PRD)
- PRD_INSPECTION_TEMPLATES.md
- PRD_LONE_WORKER.md
- FLUTTER_APP_SUMMARY.md (Current implementation status)

