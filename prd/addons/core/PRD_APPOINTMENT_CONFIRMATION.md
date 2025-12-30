# PRD: Appointment Confirmation & Rebooking System

**Addon Extension:** `property_fielder_field_service`  
**Version:** 1.1.0  
**Status:** 🔧 In Development  
**Layer:** Core (Layer 2)  
**Effort:** 8 days  

---

## 1. Overview

### 1.1 Purpose
Enable property owners and inspectors to confirm, decline, or reschedule appointments via secure links in emails, with automatic re-optimization triggers when schedules change.

### 1.2 Target Users
- Property Owners (confirm/reschedule appointments)
- Inspectors (acknowledge route assignments)
- Dispatchers (view confirmation status, handle change requests)

### 1.3 Business Value
- Reduce no-shows by getting confirmations in advance
- Enable self-service rebooking without phone calls
- Automatic re-optimization when appointments change
- Track confirmation rates for reporting

---

## 2. Data Model Extensions

### 2.1 `property_fielder.job` Extensions

| Field | Type | Description |
|-------|------|-------------|
| `confirmation_token` | Char | Secure random token for URL (32 chars) |
| `confirmation_token_expiry` | Datetime | Token expiration (72 hours after send) |
| `confirmation_state` | Selection | pending/confirmed/declined/rescheduled |
| `confirmation_date` | Datetime | When confirmed/declined |
| `confirmation_method` | Selection | email_link/phone/portal/auto |
| `proposed_reschedule_date` | Date | Date proposed by owner |
| `proposed_reschedule_time` | Char | Time window proposed |
| `reschedule_reason` | Text | Reason for reschedule request |
| `owner_notified` | Boolean | Appointment notification sent |
| `owner_notified_date` | Datetime | When notification sent |
| `reminder_sent` | Boolean | 24h reminder sent |
| `reminder_sent_date` | Datetime | When reminder sent |

### 2.2 `property_fielder.route` Extensions

| Field | Type | Description |
|-------|------|-------------|
| `needs_reoptimization` | Boolean | Route needs re-optimization |
| `reoptimization_reason` | Char | Why re-optimization needed |
| `inspector_acknowledged` | Boolean | Inspector confirmed receipt |
| `inspector_acknowledged_date` | Datetime | When acknowledged |

---

## 3. Controller Endpoints

### 3.1 Public Confirmation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/appointment/confirm/<token>` | GET | Confirm appointment page |
| `/appointment/confirm/<token>/submit` | POST | Submit confirmation |
| `/appointment/decline/<token>` | GET | Decline form page |
| `/appointment/decline/<token>/submit` | POST | Submit decline with reason |
| `/appointment/reschedule/<token>` | GET | Reschedule form page |
| `/appointment/reschedule/<token>/submit` | POST | Submit reschedule request |
| `/inspector/acknowledge/<token>` | GET | Inspector route acknowledgement |

---

## 4. Email Templates

### 4.1 Owner Appointment Email (Updated)
- **Subject:** Inspection Scheduled at [Address] - [Date]
- **Body:** Property details, date/time, inspector name
- **Buttons:**
  - ✅ Confirm Appointment (green)
  - 📅 Request Reschedule (orange)
  - ❌ Cannot Accommodate (red)

### 4.2 Inspector Schedule Email (Updated)
- **Subject:** Your Route Schedule for [Date]
- **Body:** Route summary, job list with addresses
- **Button:** ✅ Acknowledge Schedule

### 4.3 Reschedule Request Notification
- **To:** Dispatcher
- **Subject:** Reschedule Request: [Job] - [Property]
- **Body:** Current date, proposed date, reason

### 4.4 24-Hour Reminder
- **Subject:** Reminder: Inspection Tomorrow at [Address]
- **Body:** Appointment details, confirmation status

---

## 5. Workflows

### 5.1 Confirmation Flow
```
Email Sent → Owner clicks Confirm → confirmation_state = 'confirmed'
                                  → confirmation_date = now
                                  → Log in chatter
```

### 5.2 Decline Flow
```
Owner clicks Decline → Shows reason form → confirmation_state = 'declined'
                                         → reschedule_reason = [reason]
                                         → Create change.request
                                         → Notify dispatcher
```

### 5.3 Reschedule Flow
```
Owner clicks Reschedule → Shows date picker → proposed_reschedule_date = [date]
                                            → confirmation_state = 'rescheduled'
                                            → Create change.request (pending)
                                            → Notify dispatcher
Dispatcher Approves → job.scheduled_date = proposed_date
                    → route.needs_reoptimization = True
                    → Trigger re-optimization (optional)
```

### 5.4 Re-optimization Trigger
```
Job rescheduled/cancelled → Remove from route
                          → route.needs_reoptimization = True
                          → Show warning in UI
                          → Option: "Re-optimize Route" button
```

---

## 6. Security

- Tokens are 32-character random strings (uuid4 + secrets)
- Tokens expire after 72 hours
- One-time use for confirmations (token cleared after use)
- Rate limiting on endpoints (10 requests/minute/IP)
- No authentication required (public links)

---

## 7. Cron Jobs

### 7.1 Send 24-Hour Reminders
- **Schedule:** Daily at 8 AM
- **Logic:** Find jobs scheduled for tomorrow with owner_notified=True, reminder_sent=False
- **Action:** Send reminder email, set reminder_sent=True

### 7.2 Expire Old Tokens
- **Schedule:** Daily at midnight
- **Logic:** Clear tokens where expiry < now
- **Action:** Set confirmation_token = False, confirmation_token_expiry = False

