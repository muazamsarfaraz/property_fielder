# Property Fielder - Product Requirements Document (PRD)

**Version:** 2.0  
**Date:** December 13, 2025  
**Status:** Requirements Definition  
**Document Owner:** Product Team  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Vision](#2-product-vision)
3. [User Personas](#3-user-personas)
4. [Current State Assessment](#4-current-state-assessment)
5. [Complete Property Lifecycle](#5-complete-property-lifecycle)
6. [Functional Requirements](#6-functional-requirements)
7. [Data Models](#7-data-models)
8. [Workflow Specifications](#8-workflow-specifications)
9. [Integration Requirements](#9-integration-requirements)
10. [Mobile App Requirements](#10-mobile-app-requirements)
11. [Reporting Requirements](#11-reporting-requirements)
12. [Non-Functional Requirements](#12-non-functional-requirements)
13. [Implementation Phases](#13-implementation-phases)
14. [Appendices](#14-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

Property Fielder is a comprehensive field service management and compliance tracking platform built on Odoo 19, designed specifically for UK property management companies. The platform manages the complete lifecycle of property certifications under the FLAGE+ framework (Fire, Legionella, Asbestos, Gas, Electrical) including inspection scheduling, fault tracking, remediation workflows, and compliance monitoring.

### 1.2 Business Problem

UK landlords and property managers face:
- Complex statutory compliance requirements across multiple certification types
- Manual tracking of expiry dates across large property portfolios
- Inefficient inspector scheduling and route planning
- No systematic handling of inspection faults and remediation
- Risk of non-compliance leading to legal liability and tenant safety issues
- Difficulty coordinating access with tenants for inspections

### 1.3 Solution Overview

Property Fielder provides:
- Centralized property portfolio and certification management
- Automated compliance monitoring with proactive alerts
- AI-powered route optimization for inspector scheduling
- Complete fault tracking with Cat 1/Cat 2 categorization
- Remediation and re-check workflow management
- Mobile app for field inspectors
- Owner and tenant communication workflows
- Comprehensive compliance reporting

---

## 2. Product Vision

### 2.1 Vision Statement

"To be the definitive compliance management platform for UK property managers, ensuring no certification expires unnoticed, no fault goes unresolved, and every property remains safe and compliant."

### 2.2 Success Metrics

| Metric | Target |
|--------|--------|
| Portfolio compliance rate | >98% |
| Certification expiry misses | 0 |
| Cat 1 fault resolution within SLA | 100% |
| Cat 2 fault resolution within SLA | >95% |
| Inspector route efficiency gain | >25% |
| Tenant access confirmation rate | >90% |

### 2.3 Key Differentiators

1. **UK-Specific FLAGE+ Focus** - Purpose-built for UK regulatory requirements
2. **Fault-First Compliance** - Cat 1/Cat 2 fault tracking with automated escalation
3. **End-to-End Workflow** - From property onboarding to certificate issuance
4. **Intelligent Scheduling** - AI-powered route optimization with Timefold
5. **Proactive Monitoring** - Automated alerts before issues become problems

---

## 3. User Personas

### 3.1 Property Manager / Compliance Officer

**Role:** Oversees property portfolio compliance  
**Goals:**
- Ensure all properties maintain valid certifications
- Identify and resolve compliance gaps quickly
- Generate compliance reports for stakeholders
- Manage property onboarding and offboarding

**Key Tasks:**
- Review compliance dashboard daily
- Monitor expiring certifications
- Handle escalated faults
- Approve property offboarding

### 3.2 Dispatch Coordinator / Scheduler

**Role:** Plans and schedules inspection work  
**Goals:**
- Efficiently schedule inspectors across properties
- Minimize travel time and maximize daily job completion
- Handle schedule changes and cancellations
- Coordinate tenant access

**Key Tasks:**
- Bulk-select properties needing inspection
- Optimize routes for inspectors
- Share schedules with inspectors and owners
- Process change requests

### 3.3 Field Inspector

**Role:** Conducts on-site inspections  
**Goals:**
- Complete assigned jobs efficiently
- Accurately record inspection results
- Document faults with evidence
- Issue certificates for passing inspections

**Key Tasks:**
- View daily job list on mobile app
- Navigate to properties
- Conduct inspections
- Record pass/fail with fault details
- Capture photos and signatures

### 3.4 Property Owner / Landlord

**Role:** Property owner requiring compliance services  
**Goals:**
- Maintain compliant properties
- Receive timely notifications about inspections
- Access certificates and compliance reports
- Understand and resolve any faults

**Key Tasks:**
- Receive inspection notifications
- Confirm access arrangements
- Review inspection results
- Arrange remediation for faults

### 3.5 Tenant

**Role:** Occupant of managed property  
**Goals:**
- Know when inspections are scheduled
- Provide access for inspections
- Request schedule changes if needed

**Key Tasks:**
- Receive appointment notifications
- Confirm availability
- Provide access on inspection day

---

## 4. Current State Assessment

### 4.1 What's Built (Existing Functionality)

#### 4.1.1 Property Management Addon
| Feature | Status | Notes |
|---------|--------|-------|
| Property CRUD | ✅ Built | Basic property model with address, GPS, type |
| Owner/Landlord linking | ✅ Built | `partner_id` field on property |
| Tenant linking | ✅ Built | `tenant_id` field on property |
| Property types | ✅ Built | House, Flat, Bungalow, Maisonette, Commercial, Other |
| FLAGE+ status tracking | ✅ Built | Computed compliance status per property |
| GPS coordinates | ✅ Built | Latitude/longitude with reverse geocoding |
| Property states | ⚠️ Partial | Only: Draft/Active/Vacant/Maintenance/Inactive. **Missing: Non-Compliant, Offboarded** |
| Property category | ❌ Not Built | Single Let / HMO / Commercial - **needs adding** |
| Block/Unit hierarchy | ❌ Not Built | Parent/child relationship for flats in blocks - **needs adding** |

#### 4.1.2 Certification System
| Feature | Status | Notes |
|---------|--------|-------|
| Certification types (7) | ✅ Built | Fire, Legionella, Asbestos, Gas, EICR, EPC, PAT |
| Validity periods | ✅ Built | Configurable per cert type (default 365 days) |
| Warning periods | ✅ Built | Configurable days before expiry warning |
| Inspection durations | ✅ Built | Variable duration per cert type |
| Compliance requirements | ✅ Built | With legal references |
| Certificate storage | ✅ Built | Binary file attachment |
| Fault code definitions | ❌ Not Built | Cat 1/Cat 2 fault codes per cert type - **needs adding** |

#### 4.1.3 Inspection System
| Feature | Status | Notes |
|---------|--------|-------|
| Inspection model | ✅ Built | Linked to property + certification type |
| Manual job creation | ✅ Built | `action_create_field_service_job()` |
| Batch job creation wizard | ✅ Built | `CreateJobsWizard` |
| Inspection states | ✅ Built | Draft, Scheduled, In Progress, Completed, Failed, Cancelled |
| Result recording | ⚠️ Partial | Only Pass/Fail/Conditional. **Missing: fault details, Cat 1/Cat 2** |
| Fault tracking | ❌ Not Built | Inspection faults model - **needs adding** |
| Remediation tracking | ❌ Not Built | Remediation workflow - **needs adding** |
| Re-check workflow | ❌ Not Built | Follow-up inspections - **needs adding** |

#### 4.1.4 Field Service System
| Feature | Status | Notes |
|---------|--------|-------|
| Job model | ✅ Built | Full job tracking with time windows |
| Inspector model | ✅ Built | Skills, availability, home location |
| Route model | ✅ Built | Optimized route containers |
| Skills system | ✅ Built | Skill matching for job assignment |
| Timefold integration | ✅ Built | Route optimization working |
| OSRM integration | ✅ Built | Travel time calculation working |

#### 4.1.5 Dispatch View
| Feature | Status | Notes |
|---------|--------|-------|
| Map widget (Mapbox GL) | ✅ Built | Job markers, route polylines, clustering |
| Timeline widget (Vis.js) | ✅ Built | Inspector schedules visualization |
| 3-tab layout | ✅ Built | Plan, Optimize, Schedule tabs |
| Optimization controls | ✅ Built | Start, poll, display results |
| Test data management | ✅ Built | Create/delete test data |
| Compliance dashboard | ❌ Not Built | Expiring certs view - **needs adding** |

#### 4.1.6 Communication
| Feature | Status | Notes |
|---------|--------|-------|
| Schedule sharing wizard | ✅ Built | Share with inspectors/owners |
| Email templates | ✅ Built | Inspector schedule, owner appointment, reminders |
| Change request model | ✅ Built | Reschedule/cancel workflow |
| Appointment confirmation system | ✅ Built | Token-based confirm/decline/reschedule via email links |
| Confirmation portal pages | ✅ Built | QWeb templates for owner response pages |
| 24-hour reminder cron | ✅ Built | Daily cron sends appointment reminders |
| Confirmation stats dashboard | ✅ Built | Pending/confirmed/declined counts in dispatch view |
| Awaab's Law notifications | ✅ Built | Breach warnings and cron job alerts |

#### 4.1.7 Mobile App (Flutter)
| Feature | Status | Notes |
|---------|--------|-------|
| App structure | ✅ Built | Flutter project scaffolded |
| Job list | ✅ Built | Today/Upcoming/Completed tabs |
| Check-in/out | ✅ Built | GPS-based |
| Photo capture | ✅ Built | With GPS tagging |
| Signature capture | ✅ Built | Digital signature pad |
| Offline storage | ✅ Built | Hive-based |
| Sync system | ✅ Built | Background sync |
| Inspection templates | ❌ Not Built | Template-driven inspection flow - **needs adding** |
| Fault recording | ❌ Not Built | Cat 1/Cat 2 fault capture - **needs adding** |
| HHSRS hazard checklist | ❌ Not Built | 29 hazard assessment - **needs adding** |

**Note:** Mobile app code exists in `mobile_app/` but requires production testing and validation.

#### 4.1.8 E2E Testing
| Feature | Status | Notes |
|---------|--------|-------|
| Playwright setup | ✅ Built | Test infrastructure in `e2e-tests/` |
| Page objects | ✅ Built | Reusable page components |
| Basic test coverage | ⚠️ Partial | Some tests written, needs expansion |

### 4.2 What's Missing (Gap Analysis)

| Category | Missing Feature | Priority | PRD Section | Status |
|----------|-----------------|----------|-------------|--------|
| **Property** | Non-Compliant/Offboarded states | HIGH | FR-10 | ❌ Not Built |
| **Property** | Property category (Single Let/HMO/Commercial) | HIGH | FR-1.4 | ✅ Built (property_type field) |
| **Faults** | Fault Code model | HIGH | FR-7 | ❌ Not Built |
| **Faults** | Inspection Fault model (Cat 1/Cat 2) | HIGH | FR-7 | ❌ Not Built |
| **Remediation** | Remediation tracking model | HIGH | FR-8 | ✅ Built (HHSRS remediation jobs) |
| **Remediation** | Re-check inspection workflow | HIGH | FR-9 | ❌ Not Built |
| **HHSRS** | HHSRS Hazard model (29 hazards) | HIGH | FR-15.1 | ✅ Built (property_fielder_hhsrs addon) |
| **Awaab's Law** | Deadline calculation and alerts | HIGH | FR-15.2 | ✅ Built (awaab.deadline model + cron) |
| **DHS** | Decent Homes Standard assessment | HIGH | FR-15.3 | ✅ Built (dhs.assessment model) |
| **Templates** | Inspection template system | HIGH | FR-15.5 | ❌ Not Built |
| **Mobile** | Template-driven inspection | HIGH | Phase 7 | ❌ Not Built |
| **Dashboard** | Compliance dashboard | HIGH | FR-2 | ✅ Built (basic stats, charts, quick actions) |
| **Access** | Appointment confirmation | MEDIUM | FR-6 | ✅ Built (confirm/decline/reschedule flow) |

See Section 6 for complete functional requirements addressing all gaps.

---

## 5. Complete Property Lifecycle

### 5.1 Lifecycle Stages Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         PROPERTY LIFECYCLE STAGES                                    │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  STAGE 1          STAGE 2           STAGE 3           STAGE 4          STAGE 5      │
│  ────────         ────────          ────────          ────────         ────────     │
│  Property    →    Initial      →    Ongoing      →    Scheduling  →   Owner/       │
│  Onboarding       Certification     Monitoring        & Dispatch       Tenant       │
│                   Setup                                                Comms        │
│                                                                                      │
│  STAGE 6          STAGE 7           STAGE 8           STAGE 9          STAGE 10     │
│  ────────         ────────          ────────          ────────         ────────     │
│  Inspector   →    Job          →    Fault        →    Remediation →   Certificate  │
│  Dispatch         Execution         Handling          & Re-check       Issuance     │
│                                                                                      │
│  STAGE 11         STAGE 12                                                          │
│  ────────         ────────                                                          │
│  Renewal/    →    Reporting &                                                       │
│  Recurring        Compliance                                                        │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 Detailed Lifecycle Flow

```
PROPERTY ONBOARDING
       │
       ▼
DEFINE REQUIRED CERTIFICATIONS (based on property type)
       │
       ▼
CERTIFICATION GAP ANALYSIS ("Missing: Gas, EICR")
       │
       ▼
SCHEDULE INITIAL INSPECTIONS
       │
       ▼
CONTACT TENANT → CONFIRM ACCESS
       │
       ▼
OPTIMIZE ROUTES → DISPATCH INSPECTORS
       │
       ▼
   ┌───────────────────┐
   │    INSPECTION     │
   └───────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
  PASS        FAIL
    │           │
    ▼           ▼
CERTIFICATE  ┌─────────────────┐
ISSUED       │   FAULT FOUND   │
    │        │  (Cat 1/Cat 2)  │
    │        └─────────────────┘
    │                │
    │                ▼
    │        REMEDIATION SCHEDULED
    │        (24-48hr or 14-28 days)
    │                │
    │                ▼
    │        REMEDIATION COMPLETED
    │                │
    │                ▼
    │        RE-CHECK INSPECTION
    │                │
    │          ┌─────┴─────┐
    │          ▼           ▼
    │        PASS        FAIL
    │          │           │
    │          ▼           ▼
    │     CERTIFICATE   PROPERTY
    │       ISSUED      OFFBOARDED
    │          │
    └──────────┼───────────────────────┐
               │                       │
               ▼                       │
    ONGOING MONITORING                 │
    (Expiry tracking)                  │
               │                       │
               ▼                       │
    RENEWAL DUE (30/60/90 day alerts)  │
               │                       │
               ▼                       │
    SCHEDULE RENEWAL INSPECTION ◄──────┘
               │
               ▼
         (Cycle repeats)
```

### 5.3 Fault Handling Sub-Flow

```
INSPECTION FAIL
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FAULT RECORDING                               │
│  • Category: Cat 1 (Critical) or Cat 2 (Serious)                │
│  • Fault code (per certification type)                          │
│  • Description and location                                      │
│  • Photo evidence (mandatory for Cat 1)                         │
│  • Immediate actions taken (gas capped, supply isolated, etc.)  │
└─────────────────────────────────────────────────────────────────┘
       │
       ├─────────────────────────────────────────┐
       ▼                                         ▼
┌─────────────────┐                    ┌─────────────────┐
│     CAT 1       │                    │     CAT 2       │
│   CRITICAL      │                    │    SERIOUS      │
│  24-48 hours    │                    │   14-28 days    │
└─────────────────┘                    └─────────────────┘
       │                                         │
       ▼                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 AUTOMATIC ACTIONS                                │
│  1. Calculate remediation deadline                              │
│  2. Create remediation work order                               │
│  3. Create draft re-check inspection                            │
│  4. Notify property owner (URGENT for Cat 1)                    │
│  5. Notify tenant (access required)                             │
│  6. Notify manager/dispatcher                                   │
│  7. Update property status to "Non-Compliant"                   │
└─────────────────────────────────────────────────────────────────┘
       │
       ▼
REMEDIATION WORK
       │
       ▼
RE-CHECK INSPECTION
       │
   ┌───┴───┐
   ▼       ▼
 PASS    FAIL
   │       │
   ▼       ▼
CLOSE   OFFBOARD
FAULT   PROPERTY
```

---

## 6. Functional Requirements

### 6.1 Property Onboarding & Setup

#### FR-1.1 Property Import

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.1.1 | System SHALL support bulk import of properties via CSV/Excel file | HIGH |
| FR-1.1.2 | Import SHALL validate required fields: name, address, postcode, owner | HIGH |
| FR-1.1.3 | Import SHALL auto-geocode addresses to obtain GPS coordinates | HIGH |
| FR-1.1.4 | Import SHALL report errors for invalid/incomplete records | HIGH |
| FR-1.1.5 | Import SHALL support update of existing properties (match by reference) | MEDIUM |

#### FR-1.2 Address Validation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.2.1 | System SHALL integrate with UK postcode lookup service | MEDIUM |
| FR-1.2.2 | System SHALL validate postcodes against Royal Mail PAF | MEDIUM |
| FR-1.2.3 | System SHALL auto-complete addresses from postcode entry | MEDIUM |

#### FR-1.3 Property Setup Wizard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.3.1 | System SHALL provide guided wizard for new property setup | HIGH |
| FR-1.3.2 | Wizard SHALL collect: property details, owner, tenant, address | HIGH |
| FR-1.3.3 | Wizard SHALL prompt for required certification types based on property type | HIGH |
| FR-1.3.4 | Wizard SHALL allow scheduling of initial inspections | HIGH |
| FR-1.3.5 | Wizard SHALL create property, link certifications, create inspections in one flow | HIGH |

#### FR-1.4 Required Certifications Matrix

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.4.1 | System SHALL define which certifications are required per property type | HIGH |
| FR-1.4.2 | System SHALL support property categories: Single Let, HMO, Commercial | HIGH |
| FR-1.4.3 | HMO properties SHALL require all FLAGE+ certifications | HIGH |
| FR-1.4.4 | Single Let properties SHALL require minimum: Gas, EICR, EPC | HIGH |
| FR-1.4.5 | System SHALL allow custom required certifications per property | MEDIUM |

#### FR-1.5 Right to Rent Compliance (Immigration Act 2014)

> **Requirement:** UK landlords have a statutory duty to check a tenant's right to rent before granting a tenancy. This is separate from property compliance but critical for complete onboarding.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1.5.1 | System SHALL track Right to Rent check status per tenant | HIGH |
| FR-1.5.2 | Status options: Not Checked, Passed, Failed, Time-Limited (follow-up required) | HIGH |
| FR-1.5.3 | System SHALL store: Check date, Document types verified, Expiry date (if time-limited) | HIGH |
| FR-1.5.4 | System SHALL alert before time-limited check expires | HIGH |
| FR-1.5.5 | System SHALL support document upload for evidence | HIGH |
| FR-1.5.6 | System SHALL support Home Office online share code verification | MEDIUM |
| FR-1.5.7 | System SHALL prevent property activation without valid Right to Rent check | MEDIUM |
| FR-1.5.8 | System SHALL generate Right to Rent audit report | MEDIUM |

### 6.2 Certification Gap Analysis

#### FR-2.1 Compliance Gap Detection

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-2.1.1 | System SHALL automatically identify missing required certifications per property | HIGH |
| FR-2.1.2 | System SHALL calculate gap analysis on property save/update | HIGH |
| FR-2.1.3 | System SHALL display "Missing Certifications" list on property form | HIGH |
| FR-2.1.4 | System SHALL provide action to "Schedule All Missing Certifications" | HIGH |

### 6.3 Ongoing Compliance Monitoring

#### FR-3.1 Expiry Tracking

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.1.1 | System SHALL track expiry dates for all certifications | HIGH |
| FR-3.1.2 | System SHALL calculate days until expiry (positive = valid, negative = expired) | HIGH |
| FR-3.1.3 | System SHALL categorize certifications: Valid, Expiring Soon, Expired | HIGH |
| FR-3.1.4 | "Expiring Soon" threshold SHALL be configurable per certification type | HIGH |
| FR-3.1.5 | Default warning period SHALL be 30 days before expiry | HIGH |

#### FR-3.2 Compliance Dashboard

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.2.1 | System SHALL provide portfolio-wide compliance dashboard | HIGH |
| FR-3.2.2 | Dashboard SHALL show: Total Properties, Compliant, Expiring Soon, Expired, Non-Compliant | HIGH |
| FR-3.2.3 | Dashboard SHALL show pie chart of compliance status distribution | MEDIUM |
| FR-3.2.4 | Dashboard SHALL show list of properties requiring attention (priority order) | HIGH |
| FR-3.2.5 | Dashboard SHALL provide drill-down to property details | HIGH |
| FR-3.2.6 | Dashboard SHALL show upcoming inspections (next 7/14/30 days) | HIGH |

#### FR-3.3 Automated Expiry Alerts

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.3.1 | System SHALL send email alerts at configurable intervals before expiry | HIGH |
| FR-3.3.2 | Default alert intervals SHALL be: 90 days, 60 days, 30 days, 14 days, 7 days | HIGH |
| FR-3.3.3 | Alerts SHALL be sent to property owner and property manager | HIGH |
| FR-3.3.4 | Alerts SHALL include: Property details, certification type, expiry date, action required | HIGH |
| FR-3.3.5 | System SHALL log all sent alerts for audit purposes | MEDIUM |
| FR-3.3.6 | System SHALL support "Digest Mode" for non-urgent notifications | MEDIUM |
| FR-3.3.7 | Digest Mode SHALL batch Advisory/Standard/Warning alerts into daily summary email | MEDIUM |
| FR-3.3.8 | Only Immediate/Emergency alerts SHALL be sent as real-time push notifications | HIGH |
| FR-3.3.9 | User SHALL be able to configure notification preferences (Real-time vs Digest) | MEDIUM |

> **Design Decision (Per Gemini Review - Iteration 3 - Notification Fatigue):**
> With Awaab's Law, Cat 1, Cat 2, and Access notifications, a Portfolio Manager might receive 500 emails a day. To prevent notification fatigue:
> - **Real-time (Push):** Danger/Emergency alerts only (Cat 1, Awaab's Law 24hr deadline, Lone Worker panic)
> - **Daily Digest:** Advisory/Standard/Warning alerts batched into a single morning email

#### FR-3.4 Renewal Queue

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-3.4.1 | System SHALL provide "Renewal Queue" view | HIGH |
| FR-3.4.2 | Queue SHALL list all certifications expiring within configurable window | HIGH |
| FR-3.4.3 | Default window SHALL be 30 days | HIGH |
| FR-3.4.4 | Queue SHALL group by certification type | MEDIUM |
| FR-3.4.5 | Queue SHALL allow bulk selection for inspection scheduling | HIGH |

### 6.4 Job Creation Workflow (Preferred Workflow)

#### FR-4.1 Inspections Due List

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.1.1 | System SHALL provide "Inspections Due" list view | HIGH |
| FR-4.1.2 | List SHALL show properties with ANY certification expiring within configurable window | HIGH |
| FR-4.1.3 | Default window SHALL be 14-30 days from current date | HIGH |
| FR-4.1.4 | List SHALL display: Property, Address, Certification Type, Expiry Date, Days Until Expiry | HIGH |
| FR-4.1.5 | List SHALL be sortable by expiry date, property, certification type | HIGH |
| FR-4.1.6 | List SHALL be filterable by certification type, area, owner | HIGH |

#### FR-4.2 Bulk Property Selection

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.2.1 | System SHALL allow multi-select of properties via checkboxes | HIGH |
| FR-4.2.2 | System SHALL provide "Select All" / "Deselect All" functionality | HIGH |
| FR-4.2.3 | System SHALL show count of selected properties | HIGH |
| FR-4.2.4 | System SHALL provide "Create Jobs for Selected" action button | HIGH |

#### FR-4.3 Bulk Job Creation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.3.1 | System SHALL create inspection records for selected properties | HIGH |
| FR-4.3.2 | System SHALL create field service jobs linked to inspections | HIGH |
| FR-4.3.3 | System SHALL allow setting target date range for jobs | HIGH |
| FR-4.3.4 | System SHALL inherit duration from certification type | HIGH |
| FR-4.3.5 | System SHALL validate property has required data (GPS, address, owner) | HIGH |
| FR-4.3.6 | System SHALL report any properties skipped with reasons | HIGH |

#### FR-4.4 Inspector Assignment Preferences

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-4.4.1 | System SHALL support preferred inspector per property | MEDIUM |
| FR-4.4.2 | System SHALL support preferred inspector per area/postcode | MEDIUM |
| FR-4.4.3 | Optimizer SHALL consider preferences when assigning routes | MEDIUM |
| FR-4.4.4 | System SHALL allow override of preferences during manual assignment | MEDIUM |

### 6.5 Owner/Tenant Communication

#### FR-5.1 Access Booking Workflow

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.1.1 | System SHALL track tenant contact details for each property | HIGH |
| FR-5.1.2 | System SHALL send appointment notification to tenant when job scheduled | HIGH |
| FR-5.1.3 | Notification SHALL include: Date, Time window, Duration, Contact number | HIGH |
| FR-5.1.4 | System SHALL support email and SMS notifications | HIGH |
| FR-5.1.5 | System SHALL track notification delivery status | MEDIUM |

#### FR-5.2 Access Confirmation Tracking

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.2.1 | System SHALL track access confirmation status per job | HIGH |
| FR-5.2.2 | Status options: Pending, Confirmed, Declined, No Response | HIGH |
| FR-5.2.3 | System SHALL send reminder if no confirmation within 48 hours | HIGH |
| FR-5.2.4 | System SHALL alert dispatcher for declined or no-response jobs | HIGH |
| FR-5.2.5 | System SHALL track if keys are available (key holder location) | MEDIUM |

#### FR-5.3 Schedule Change Requests

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.3.1 | System SHALL allow tenants to request schedule changes | HIGH |
| FR-5.3.2 | System SHALL allow owners to request schedule changes | HIGH |
| FR-5.3.3 | Change requests SHALL include: Reason, Preferred alternative dates | HIGH |
| FR-5.3.4 | System SHALL route change requests to dispatcher for approval | HIGH |
| FR-5.3.5 | Approved changes SHALL trigger re-optimization if route affected | HIGH |
| FR-5.3.6 | System SHALL notify all affected parties of schedule changes | HIGH |

#### FR-5.4 No-Access Handling

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.4.1 | Inspector SHALL be able to record "No Access" outcome | HIGH |
| FR-5.4.2 | No Access reasons: No Answer, Access Refused, Property Inaccessible, Tenant Absent | HIGH |
| FR-5.4.3 | System SHALL automatically schedule re-visit for No Access jobs | HIGH |
| FR-5.4.4 | System SHALL notify owner of No Access with reason | HIGH |
| FR-5.4.5 | System SHALL track each access attempt as a linked record (not just a count) | HIGH |
| FR-5.4.6 | After 3 No Access attempts, system SHALL escalate to manager | HIGH |
| FR-5.4.7 | System SHALL generate PDF "Access Refusal Log" for legal defence | HIGH |
| FR-5.4.8 | Access Log SHALL include: Dates, times, methods of communication, evidence | HIGH |

#### FR-5.5 Proof of Service (Section 21 Compliance)

> **Requirement:** UK landlords cannot serve a valid Section 21 eviction notice unless they can prove the tenant received the Gas Safety Certificate, EPC, and "How to Rent" guide.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.5.1 | System SHALL track delivery of compliance documents to tenant | HIGH |
| FR-5.5.2 | Delivery methods: Email (with tracking), Post (recorded), Hand delivery (signed) | HIGH |
| FR-5.5.3 | System SHALL record: Document type, Delivery date, Delivery method, Evidence | HIGH |
| FR-5.5.4 | Email delivery SHALL track open/receipt confirmation where possible | MEDIUM |
| FR-5.5.5 | Hand delivery SHALL require signature receipt | HIGH |
| FR-5.5.6 | System SHALL generate "Proof of Service" report per property | HIGH |
| FR-5.5.7 | System SHALL alert if required documents not delivered after cert issued | HIGH |

#### FR-5.6 Landlord Remediation Notification

> **Requirement:** In "Let Only" management agreements, the agent finds the fault but the landlord is responsible for fixing it.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-5.6.1 | System SHALL support "Landlord Managed" remediation workflow | HIGH |
| FR-5.6.2 | Landlord notification SHALL include: Fault details, Severity SLA, Legal deadline | HIGH |
| FR-5.6.3 | System SHALL pause internal SLA tracking when assigned to landlord | MEDIUM |
| FR-5.6.4 | System SHALL continue reminder notifications to landlord until resolved | HIGH |
| FR-5.6.5 | System SHALL allow landlord to upload completion evidence | HIGH |
| FR-5.6.6 | System SHALL track landlord response time for compliance reporting | MEDIUM |

### 6.6 Inspection Execution

#### FR-6.1 Inspection Recording

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.1.1 | Inspector SHALL record inspection result: Pass, Fail, Conditional | HIGH |
| FR-6.1.2 | Pass result SHALL allow certificate generation | HIGH |
| FR-6.1.3 | Fail result SHALL REQUIRE fault details (see FR-7) | HIGH |
| FR-6.1.4 | Conditional result SHALL REQUIRE fault details AND conditions | HIGH |
| FR-6.1.5 | System SHALL capture: Findings, Recommendations, Photos, Signature | HIGH |

#### FR-6.2 Mobile App Sync

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-6.2.1 | Mobile app SHALL sync inspection results to backend | HIGH |
| FR-6.2.2 | Sync SHALL update inspection status in Odoo | HIGH |
| FR-6.2.3 | Sync SHALL upload photos and signatures | HIGH |
| FR-6.2.4 | Sync SHALL work with intermittent connectivity | HIGH |
| FR-6.2.5 | Sync SHALL handle conflict resolution (last-write-wins or prompt) | MEDIUM |

### 6.7 Fault Tracking (Native Codes + Severity SLA)

> **Design Decision:** Industry fault codes (EICR C1/C2, Gas ID/AR) and HHSRS hazard categories use different classification systems. Rather than flattening these into a simplified "Cat 1/Cat 2" internal category (which can mislead users about actual SLA requirements), the system maintains **native fault codes** and maps them to a **Severity SLA** for deadline calculation.

#### FR-7.1 Severity SLA Classifications

| Severity SLA | Description | Remediation Window | Example Codes |
|--------------|-------------|--------------------|---------------|
| **Immediate** | Danger present, requires same-day action | 24 hours | Gas ID, EICR C1, FSH, ADF |
| **Urgent** | Potentially dangerous, requires rapid action | 7 days | Gas AR, EICR C2, FSR, ARD |
| **Standard** | Non-urgent but requires resolution | 28 days | LRF (Legionella Risk Factors) |
| **Advisory** | Improvement recommended, no SLA | N/A | Gas NCS, EICR C3, FI |

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.1.1 | System SHALL maintain native fault codes per industry standard (GIUSP, 18th Edition, etc.) | HIGH |
| FR-7.1.2 | Each fault code SHALL map to a Severity SLA (Immediate/Urgent/Standard/Advisory) | HIGH |
| FR-7.1.3 | Immediate SLA faults SHALL require remediation within 24 hours | HIGH |
| FR-7.1.4 | Urgent SLA faults SHALL require remediation within 7 days | HIGH |
| FR-7.1.5 | Standard SLA faults SHALL require remediation within 28 days | HIGH |
| FR-7.1.6 | Remediation window SHALL be configurable per fault code | MEDIUM |
| FR-7.1.7 | System SHALL enforce fault recording when inspection fails | HIGH |

#### FR-7.2 Fault Recording

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.2.1 | Fault record SHALL include: Native Code, Severity SLA (computed), Description, Location | HIGH |
| FR-7.2.2 | Fault codes SHALL be defined per certification type with industry-standard codes | HIGH |
| FR-7.2.3 | Photo evidence SHALL be mandatory for Immediate SLA faults | HIGH |
| FR-7.2.4 | Photo evidence SHALL be recommended for Urgent/Standard SLA faults | MEDIUM |
| FR-7.2.5 | System SHALL record immediate actions taken (gas capped, supply isolated) | HIGH |
| FR-7.2.6 | System SHALL auto-calculate remediation deadline based on Severity SLA | HIGH |
| FR-7.2.7 | System SHALL display native code alongside computed SLA to prevent confusion | HIGH |

#### FR-7.3 Fault Codes by Certification Type (Industry Standards)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.3.1 | **Gas Safety (GIUSP):** ID → Immediate, AR → Urgent, NCS → Advisory | HIGH |
| FR-7.3.2 | **EICR (18th Edition):** C1 → Immediate, C2 → Urgent, C3 → Advisory, FI → Advisory | HIGH |
| FR-7.3.3 | **Fire Safety (RRO):** FSH → Immediate, FSR → Urgent, FSI → Advisory | HIGH |
| FR-7.3.4 | **Legionella (HSE L8):** LAC → Immediate, LRF → Standard, LMI → Advisory | HIGH |
| FR-7.3.5 | **Asbestos (CAR 2012):** ADF → Immediate, ARD → Urgent, AIM → Advisory | HIGH |
| FR-7.3.6 | System SHALL allow custom fault codes with mandatory SLA mapping | MEDIUM |

#### FR-7.4 Fault Status Tracking

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-7.4.1 | Fault status options: Open, Remediation Scheduled, Remediated, Re-check Scheduled, Re-check Passed, Re-check Failed, Escalated | HIGH |
| FR-7.4.2 | System SHALL track fault status transitions with timestamps | HIGH |
| FR-7.4.3 | System SHALL prevent closing fault without re-check pass | HIGH |
| FR-7.4.4 | System SHALL auto-escalate faults approaching deadline based on SLA | HIGH |

### 6.8 Remediation Workflow

#### FR-8.1 Remediation Work Orders

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.1.1 | System SHALL auto-create remediation work order when fault recorded | HIGH |
| FR-8.1.2 | Work order SHALL include: Fault details (native code + SLA), Deadline, Property access info | HIGH |
| FR-8.1.3 | Work order SHALL be assignable to inspector or external contractor | HIGH |
| FR-8.1.4 | Work order SHALL track: Scheduled date, Completion date, Cost, Invoice reference | HIGH |
| FR-8.1.5 | Completion SHALL require evidence (photos, notes) | HIGH |
| FR-8.1.6 | System SHALL support "Guest Upload" link for external contractors without app access | MEDIUM |

#### FR-8.2 Remediation Scheduling

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.2.1 | Immediate SLA remediation SHALL be scheduled within 24 hours of fault | HIGH |
| FR-8.2.2 | Urgent SLA remediation SHALL be scheduled within 3 days of fault | HIGH |
| FR-8.2.3 | Standard SLA remediation SHALL be scheduled within 14 days of fault | HIGH |
| FR-8.2.4 | System SHALL alert dispatcher of unscheduled remediation | HIGH |
| FR-8.2.5 | System SHALL include remediation in route optimization | MEDIUM |

#### FR-8.2.5 Cost Approval Workflow

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.2.6 | System SHALL support configurable cost approval thresholds per landlord | MEDIUM |
| FR-8.2.7 | Remediation exceeding threshold SHALL require landlord approval before instruction | MEDIUM |
| FR-8.2.8 | System SHALL track approval status and timestamp | MEDIUM |
| FR-8.2.9 | System SHALL send approval request notification to landlord | MEDIUM |

#### FR-8.3 Remediation Completion

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.3.1 | Remediation completion SHALL trigger re-check scheduling | HIGH |
| FR-8.3.2 | System SHALL auto-create re-check inspection linked to fault | HIGH |
| FR-8.3.3 | Re-check SHALL be scheduled before original remediation deadline | HIGH |
| FR-8.3.4 | System SHALL notify tenant of re-check appointment | HIGH |

#### FR-8.5 Landlord Refusal Workflow (Liability Protection)

> **Design Decision (Per Gemini Review):** When a landlord refuses to fund a statutory repair, the managing agent remains liable if they continue managing a non-compliant property. This workflow protects the agent.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.5.1 | System SHALL support "Landlord Declined" status on remediation work orders | HIGH |
| FR-8.5.2 | Landlord decline SHALL trigger "Termination Warning" workflow | HIGH |
| FR-8.5.3 | System SHALL auto-generate formal warning letter to landlord | HIGH |
| FR-8.5.4 | Warning letter SHALL include: Fault details, Legal obligations, Deadline to respond, Consequences | HIGH |
| FR-8.5.5 | System SHALL track landlord response to warning | HIGH |
| FR-8.5.6 | If no response within 14 days, system SHALL escalate to senior manager | HIGH |
| FR-8.5.7 | System SHALL support "Terminate Management" action if landlord refuses statutory repair | HIGH |
| FR-8.5.8 | Termination SHALL generate formal termination letter with compliance history | HIGH |
| FR-8.5.9 | All refusal communications SHALL be logged for legal defence | HIGH |

#### FR-8.6 Section 21 Eviction Ban (Compliance Blocker)

> **Design Decision (Per Gemini Review):** UK landlords cannot legally serve a Section 21 eviction notice if the property is non-compliant with Gas Safety, EPC, "How to Rent", or Deposit Protection requirements.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.6.1 | System SHALL compute "Section 21 Blocked" status per property | HIGH |
| FR-8.6.2 | Blocked if: Gas certificate expired OR EPC expired OR How to Rent not served OR Deposit not protected OR Prescribed deposit info not served | HIGH |
| FR-8.6.3 | System SHALL display prominent "EVICTION BAN" warning on property dashboard | HIGH |
| FR-8.6.4 | Warning SHALL explain which requirement(s) are blocking Section 21 | HIGH |
| FR-8.6.5 | System SHALL include Section 21 status in compliance reports | MEDIUM |
| FR-8.6.6 | System SHALL alert property manager when Section 21 becomes blocked | HIGH |
| FR-8.6.7 | Deposit protection must be completed within 30 days of receipt | HIGH |
| FR-8.6.8 | Prescribed deposit information must be served to tenant | HIGH |

> **Design Decision (Per Gemini Review - Iteration 3 - Deposit Protection):**
> If the tenancy deposit isn't protected within 30 days AND the prescribed information served to the tenant, Section 21 is also blocked. This is a common oversight that invalidates eviction notices.

#### FR-8.7 Invoice Blocking on Failed Re-Check

> **Design Decision (Per Gemini Review - Iteration 3):** If a contractor marks a job complete but the Re-check Inspection fails (poor workmanship), the invoice should not be approved for payment.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.7.1 | System SHALL link Remediation Work Order to Re-Check Inspection | HIGH |
| FR-8.7.2 | Invoice approval status SHALL be blocked if linked Re-Check result = Fail | HIGH |
| FR-8.7.3 | System SHALL display "Re-Check Failed - Invoice Blocked" warning | HIGH |
| FR-8.7.4 | Manager SHALL be able to override block with mandatory reason | MEDIUM |
| FR-8.7.5 | Override SHALL be logged for audit trail | HIGH |
| FR-8.7.6 | System SHALL notify contractor of failed Re-Check and blocked invoice | HIGH |

#### FR-8.4 External Contractor Portal (Guest Upload)

> **Requirement:** External contractors (plumbers/electricians) typically won't install a proprietary mobile app for a one-off job. A lightweight web portal or "magic link" allows them to complete work orders.

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.4.1 | System SHALL generate secure "magic link" for external contractors | HIGH |
| FR-8.4.2 | Magic link SHALL expire after 72 hours or upon completion | HIGH |
| FR-8.4.3 | Guest portal SHALL display: Work order details, Property access info, Deadline | HIGH |
| FR-8.4.4 | Guest portal SHALL allow: Upload photos (before/after), Add notes, Mark complete | HIGH |
| FR-8.4.5 | Guest portal SHALL allow: Upload invoice/receipt | MEDIUM |
| FR-8.4.6 | Completion via guest portal SHALL trigger re-check scheduling | HIGH |
| FR-8.4.7 | Guest portal SHALL NOT require app installation or account creation | HIGH |
| FR-8.4.8 | System SHALL send email notification with magic link to contractor | HIGH |

### 6.9 Re-Check Inspection

#### FR-9.1 Re-Check Scheduling

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-9.1.1 | Re-check inspection SHALL be linked to original fault | HIGH |
| FR-9.1.2 | Re-check SHALL display original fault details to inspector | HIGH |
| FR-9.1.3 | Re-check SHALL verify specific fault items were resolved | HIGH |
| FR-9.1.4 | Re-check SHOULD be performed by different inspector than original | MEDIUM |

#### FR-9.2 Re-Check Outcomes

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-9.2.1 | Re-check Pass SHALL close the fault | HIGH |
| FR-9.2.2 | Re-check Pass SHALL allow certificate issuance | HIGH |
| FR-9.2.3 | Re-check Pass SHALL update property status to Compliant | HIGH |
| FR-9.2.4 | Re-check Fail SHALL trigger property offboarding | HIGH |
| FR-9.2.5 | Re-check Fail SHALL record additional fault details | HIGH |

### 6.10 Property Offboarding

#### FR-10.1 Offboarding Trigger

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10.1.1 | Property SHALL be offboarded when re-check inspection fails | HIGH |
| FR-10.1.2 | Property MAY be offboarded after 3 failed access attempts | MEDIUM |
| FR-10.1.3 | Property MAY be manually offboarded by manager | HIGH |
| FR-10.1.4 | Offboarding SHALL require confirmation dialog | HIGH |

#### FR-10.2 Offboarding Actions

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10.2.1 | System SHALL change property status to "Offboarded" | HIGH |
| FR-10.2.2 | System SHALL cancel any pending jobs/inspections for property | HIGH |
| FR-10.2.3 | System SHALL notify property owner with formal letter | HIGH |
| FR-10.2.4 | System SHALL notify tenant if property uninhabitable (Cat 1) | HIGH |
| FR-10.2.5 | System SHALL generate offboarding report with fault history | HIGH |
| FR-10.2.6 | System SHALL retain all records for compliance audit | HIGH |

#### FR-10.3 Offboarding Reversal

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-10.3.1 | Offboarded property MAY be re-activated by manager | MEDIUM |
| FR-10.3.2 | Re-activation SHALL require proof of remediation | MEDIUM |
| FR-10.3.3 | Re-activation SHALL trigger full re-inspection | MEDIUM |

### 6.11 Certificate Issuance

#### FR-11.1 Certificate Generation

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-11.1.1 | System SHALL auto-generate certificate when inspection passes | HIGH |
| FR-11.1.2 | Certificate SHALL include: Property, Inspector, Date, Expiry, Findings | HIGH |
| FR-11.1.3 | Certificate number SHALL be auto-generated with unique sequence | HIGH |
| FR-11.1.4 | System SHALL calculate expiry based on certification type validity period | HIGH |
| FR-11.1.5 | System SHALL store certificate as PDF attachment | HIGH |

#### FR-11.2 Certificate Delivery

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-11.2.1 | System SHALL email certificate copy to property owner | HIGH |
| FR-11.2.2 | System SHALL make certificate available in owner portal | MEDIUM |
| FR-11.2.3 | System SHALL retain certificate for minimum 6 years (UK requirement) | HIGH |

### 6.12 Recurring Inspections

#### FR-12.1 Automatic Renewal Scheduling

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-12.1.1 | System SHALL auto-create inspection when certificate approaches expiry | MEDIUM |
| FR-12.1.2 | Auto-creation trigger SHALL be configurable (e.g., 60 days before expiry) | MEDIUM |
| FR-12.1.3 | System SHALL send notification when renewal inspection created | MEDIUM |
| FR-12.1.4 | System SHALL NOT auto-create if inspection already exists | MEDIUM |

### 6.13 Route Optimization & Dispatch

#### FR-13.1 Route Optimization

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-13.1.1 | System SHALL optimize routes using Timefold solver | HIGH |
| FR-13.1.2 | Optimization SHALL consider: Travel time, Time windows, Inspector skills, Vehicle capacity | HIGH |
| FR-13.1.3 | Optimization SHALL use OSRM for accurate travel times | HIGH |
| FR-13.1.4 | System SHALL support multi-day route planning | MEDIUM |
| FR-13.1.5 | System SHALL allow manual route adjustments post-optimization | HIGH |

#### FR-13.2 Schedule Sharing

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-13.2.1 | System SHALL share optimized schedules with inspectors via email | HIGH |
| FR-13.2.2 | System SHALL share appointment details with property owners via email | HIGH |
| FR-13.2.3 | System SHALL include change request link in shared schedules | HIGH |
| FR-13.2.4 | Change requests SHALL trigger re-optimization workflow | HIGH |

---

## 7. Data Models

### 7.1 Core Models (Existing)

#### 7.1.1 Property (`property_fielder.property`)

**Currently Implemented:**

| Field | Type | Description | Status |
|-------|------|-------------|--------|
| name | Char | Property name/reference | ✅ Built |
| property_number | Char | Unique auto-generated number | ✅ Built |
| street, street2, city, state, zip | Char | Address fields | ✅ Built |
| country_id | Many2one | Country reference | ✅ Built |
| latitude, longitude | Float | GPS coordinates | ✅ Built |
| property_type | Selection | House/Flat/Bungalow/Maisonette/Commercial/Other | ✅ Built |
| bedrooms, bathrooms | Integer | Property details | ✅ Built |
| floor_area | Float | Square meters | ✅ Built |
| year_built | Integer | Construction year | ✅ Built |
| partner_id | Many2one | Owner/Landlord (res.partner) | ✅ Built |
| tenant_id | Many2one | Current tenant (res.partner) | ✅ Built |
| state | Selection | **Only:** Draft/Active/Vacant/Maintenance/Inactive | ⚠️ Partial |
| certification_ids | One2many | Related certifications | ✅ Built |
| inspection_ids | One2many | Related inspections | ✅ Built |
| compliance_status | Selection | Computed: Compliant/Expiring Soon/Expired/Non-Compliant | ✅ Built |
| flage_*_status | Selection | Per-category FLAGE status | ✅ Built |
| notes | Text | Additional notes | ✅ Built |

**NEW FIELDS REQUIRED (Not Yet Built):**

| Field | Type | Description |
|-------|------|-------------|
| uprn | Char | Unique Property Reference Number (UK government standard) |
| state (extend) | Selection | **Add:** 'non_compliant' and 'offboarded' states |
| property_category | Selection | Single Let / HMO / Commercial |
| required_certification_type_ids | Many2many | Which certs are required for this property |
| preferred_inspector_id | Many2one | Preferred inspector |
| key_holder_id | Many2one | Key holder contact (res.partner) |
| key_holder_notes | Text | Key collection instructions |
| access_notes | Text | Access instructions for inspectors |
| offboarding_date | Date | When property was offboarded |
| offboarding_reason | Text | Reason for offboarding |
| parent_id | Many2one | Parent property (Block/Estate) for flats/units - recursive |
| child_ids | One2many | Child properties (Units/Blocks) if this is a parent |
| is_block | Boolean | Is this a Block (parent) property? |
| height_meters | Float | Building height in meters (for EWS1 requirement) |
| section_21_blocked | Boolean | Computed: Cannot serve Section 21 if non-compliant |
| is_compliant | Boolean | Computed: All required certs valid AND parent compliant |
| deposit_protected | Boolean | Is tenancy deposit protected within 30 days? |
| deposit_prescribed_info_served | Boolean | Has prescribed deposit info been served? |

> **Design Decision (Per Gemini Review - Iteration 3 - UPRN):**
> The UPRN (Unique Property Reference Number) is the gold standard for UK government data and is required for many newer compliance integrations, including the upcoming national landlord register under the Renters' Rights Bill. Add this field immediately in Phase 1.

> **Design Decision (Per Gemini Review - Block/Unit Hierarchy):**
> For flats/apartments, compliance is split: The **Block** needs Fire Risk Assessment (FRA) and Asbestos survey; the **Unit** needs Gas/EICR. The `parent_id` field enables:
> - Block-level certifications (FRA, Asbestos) cascade visibility to all Units
> - Unit-level certifications (Gas, EICR) are tracked per flat
> - Compliance dashboard shows both Block and Unit status
> - Fire Safety Act 2021 compliance for multi-unit buildings

> **Design Decision (Per Gemini Review - Cascading Compliance):**
> A Unit's `is_compliant` computed field MUST return `False` if `parent_id.is_compliant` is `False`. This ensures no one moves into a flat in a dangerous building. Example: Flat 4 has valid Gas Cert (Unit level), but the Block has expired Fire Risk Assessment (Block level) → Flat 4 is NOT compliant.

#### 7.1.2 Certification Type (`property_fielder.certification.type`)

**Currently Implemented:**

| Field | Type | Description | Status |
|-------|------|-------------|--------|
| name | Char | Certification name | ✅ Built |
| code | Char | Unique code (FIRE, GAS, etc.) | ✅ Built |
| description | Text | Description | ✅ Built |
| flage_category | Selection | F/L/A/G/E/Other | ✅ Built |
| validity_period | Integer | Days valid | ✅ Built |
| warning_period | Integer | Days before expiry warning | ✅ Built |
| default_duration_minutes | Integer | Inspection duration | ✅ Built |
| requirement_ids | One2many | Compliance requirements | ✅ Built |
| color, sequence | Integer | Display options | ✅ Built |
| active | Boolean | Active flag | ✅ Built |

**NEW FIELDS REQUIRED (Not Yet Built):**

| Field | Type | Description |
|-------|------|-------------|
| cat1_remediation_hours | Integer | Hours for Cat 1 remediation (default: 48) |
| cat2_remediation_days | Integer | Days for Cat 2 remediation (default: 28) |
| fault_code_ids | One2many | Available fault codes for this type |

#### 7.1.3 Property Certification (`property_fielder.property.certification`)

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Certificate number |
| property_id | Many2one | Property reference |
| certification_type_id | Many2one | Certification type |
| flage_category | Selection | Related FLAGE category |
| issue_date | Date | When issued |
| expiry_date | Date | When expires |
| next_inspection_date | Date | Computed |
| days_until_expiry | Integer | Computed |
| status | Selection | Valid/Expiring Soon/Expired/Cancelled |
| inspector_id | Many2one | Inspector who issued |
| inspector_company | Char | Company name |
| inspector_license | Char | License number |
| certificate_file | Binary | PDF attachment |
| is_compliant | Boolean | Computed |
| compliance_notes | Text | Notes |
| inspection_id | Many2one | Related inspection |

#### 7.1.4 Property Inspection (`property_fielder.property.inspection`)

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Inspection number |
| property_id | Many2one | Property |
| certification_type_id | Many2one | Certification type |
| scheduled_date | Date | Scheduled date |
| completed_date | Date | Completion date |
| inspector_id | Many2one | Assigned inspector |
| job_id | Many2one | Linked field service job |
| state | Selection | Draft/Scheduled/In Progress/Completed/Failed/Cancelled |
| result | Selection | Pass/Fail/Conditional |
| findings | Text | Inspection findings |
| recommendations | Text | Recommendations |
| certification_id | Many2one | Generated certificate |
| report_file | Binary | Report attachment |
| photo_ids | Many2many | Photos |
| notes | Text | Notes |

**NEW FIELDS REQUIRED:**

| Field | Type | Description |
|-------|------|-------------|
| fault_ids | One2many | Related faults found |
| is_recheck | Boolean | Is this a re-check inspection? |
| original_fault_id | Many2one | If re-check, link to original fault |
| access_status | Selection | Pending/Confirmed/Declined/No Response |
| access_confirmed_date | Datetime | When access was confirmed |
| no_access_reason | Selection | If no access, why |

### 7.2 New Models Required

#### 7.2.1 Fault Code (`property_fielder.fault.code`)

> **Design Decision:** Fault codes maintain their industry-standard names (C1, ID, AR, etc.) and map to a `severity_sla` for deadline calculation. This prevents confusion between different industry coding systems.

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Native fault code (e.g., "ID", "C1", "AR") |
| display_name | Char | Full description (e.g., "C1 - Danger Present") |
| certification_type_id | Many2one | Which cert type |
| industry_standard | Char | Reference standard (e.g., "GIUSP", "18th Edition", "RRO") |
| severity_sla | Selection | immediate / urgent / standard / advisory |
| remediation_hours | Integer | Hours for remediation (e.g., 24, 168, 672) |
| requires_immediate_action | Boolean | Must take immediate action on-site? |
| action_required | Text | What action is required |
| photo_mandatory | Boolean | Is photo evidence mandatory? |
| active | Boolean | Active flag |

**Severity SLA Mapping:**

| severity_sla | remediation_hours | Example Codes |
|--------------|-------------------|---------------|
| immediate | 24 | Gas ID, EICR C1, FSH, ADF, LAC |
| urgent | 168 (7 days) | Gas AR, EICR C2, FSR, ARD |
| standard | 672 (28 days) | LRF |
| advisory | NULL (no SLA) | Gas NCS, EICR C3/FI, FSI, AIM, LMI |

#### 7.2.2 Inspection Fault / Defect (`property_fielder.defect`)

> **Design Decision:** We use a unified "Defect" model that can represent both regulatory faults (Gas/EICR codes) and HHSRS hazards. This prevents data duplication when a single issue (e.g., broken boiler) triggers both a Gas Fault and an HHSRS Hazard.

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Defect reference number (auto-generated) |
| defect_type | Selection | regulatory_fault / hhsrs_hazard |
| inspection_id | Many2one | Source inspection |
| property_id | Many2one | Property (for quick access) |
| certification_type_id | Many2one | Certification type (for regulatory faults) |
| fault_code_id | Many2one | Native fault code (C1, ID, etc.) |
| hhsrs_hazard_type_id | Many2one | HHSRS hazard type (1-29) if hhsrs_hazard |
| hhsrs_band | Selection | A-J (HHSRS severity band) |
| severity_sla | Selection | immediate / urgent / standard / advisory (computed from code) |
| description | Text | Detailed description |
| location | Char | Location in property |
| photo_ids | Many2many | Evidence photos |
| immediate_action_taken | Text | Actions taken on-site |
| gas_capped | Boolean | Was gas supply capped? |
| supply_isolated | Boolean | Was supply isolated? |
| remediation_deadline | Datetime | Calculated from severity_sla |
| state | Selection | See FR-7.4.1 |
| remediation_id | Many2one | Related remediation work |
| recheck_inspection_id | Many2one | Re-check inspection |
| linked_defect_ids | Many2many | Related defects (e.g., Gas fault → HHSRS hazard) |
| escalated | Boolean | Has been escalated? |
| escalated_date | Datetime | When escalated |
| escalated_to | Many2one | Who it was escalated to (res.users) |
| closed_date | Datetime | When closed |
| closed_by | Many2one | Who closed it (res.users) |
| awaab_category | Selection | emergency / significant / out_of_scope (for Awaab's Law) |
| awaab_day_zero | Date | Day 0 for Awaab's Law calculation |

#### 7.2.3 Remediation Work (`property_fielder.remediation`)

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Work order number |
| fault_id | Many2one | Related fault |
| property_id | Many2one | Property |
| work_description | Text | What needs to be done |
| contractor_type | Selection | Internal Inspector / External Contractor |
| inspector_id | Many2one | If internal |
| contractor_id | Many2one | If external (res.partner) |
| scheduled_date | Datetime | When scheduled |
| completed_date | Datetime | When completed |
| deadline | Datetime | Must complete by |
| completion_notes | Text | What was done |
| before_photo_ids | Many2many | Before photos |
| after_photo_ids | Many2many | After photos |
| cost | Float | Cost of remediation |
| invoice_id | Many2one | Related invoice |
| state | Selection | Draft/Scheduled/In Progress/Completed/Failed |

#### 7.2.4 Access Confirmation (`property_fielder.access.confirmation`)

| Field | Type | Description |
|-------|------|-------------|
| job_id | Many2one | Related job |
| property_id | Many2one | Property |
| tenant_id | Many2one | Tenant contact |
| notification_sent | Datetime | When notification sent |
| notification_method | Selection | Email / SMS / Both |
| response_status | Selection | Pending / Confirmed / Declined / No Response |
| response_date | Datetime | When responded |
| decline_reason | Text | If declined, why |
| alternative_dates | Text | Suggested alternatives |
| reminder_count | Integer | How many reminders sent |
| last_reminder_date | Datetime | Last reminder sent |

#### 7.2.5 Access Attempt (`property_fielder.access.attempt`)

> **Design Decision:** Replaces simple `no_access_count` integer on Property. Each access attempt is tracked separately for audit trail and legal defence.

| Field | Type | Description |
|-------|------|-------------|
| job_id | Many2one | Related job/inspection |
| property_id | Many2one | Property |
| attempt_date | Datetime | Date and time of attempt |
| attempt_number | Integer | Attempt number in current chain (1, 2, 3) |
| result | Selection | Success / No Answer / Access Refused / Tenant Absent / Property Inaccessible |
| communication_method | Selection | In Person / Phone Call / Email / Letter |
| notes | Text | Details of the attempt |
| evidence_ids | Many2many | Photos, recordings, letter copies |
| gps_latitude | Float | GPS location when recorded |
| gps_longitude | Float | GPS location when recorded |
| recorded_by | Many2one | Inspector who recorded (res.users) |

#### 7.2.6 Property Compliance Log (`property_fielder.property.compliance.log`)

> **Design Decision:** Audit trail for compliance-related events. Critical for legal defence and regulatory reporting.

| Field | Type | Description |
|-------|------|-------------|
| property_id | Many2one | Property |
| event_date | Datetime | When event occurred |
| event_type | Selection | See below |
| description | Text | Human-readable description |
| old_value | Char | Previous value (if state change) |
| new_value | Char | New value (if state change) |
| related_model | Char | Model name (e.g., property_fielder.defect) |
| related_id | Integer | Record ID of related object |
| user_id | Many2one | User who triggered event (res.users) |
| automatic | Boolean | Was this triggered automatically? |

**Event Types:**

| Code | Description |
|------|-------------|
| state_change | Property status changed (Active → Non-Compliant) |
| cert_expired | Certification expired |
| cert_issued | New certificate issued |
| defect_opened | New defect/fault recorded |
| defect_closed | Defect resolved |
| inspection_failed | Inspection resulted in failure |
| offboard_trigger | Offboarding process started |
| offboard_complete | Property offboarded |
| access_refused | Tenant refused access |
| access_attempt | Access attempt recorded |
| document_delivered | Proof of service recorded |
| awaab_deadline | Awaab's Law deadline triggered |
| escalation | Issue escalated to manager |

#### 7.2.7 Document Delivery / Proof of Service (`property_fielder.document.delivery`)

| Field | Type | Description |
|-------|------|-------------|
| property_id | Many2one | Property |
| tenant_id | Many2one | Tenant who received |
| document_type | Selection | Gas Certificate / EPC / EICR / How to Rent Guide |
| related_certification_id | Many2one | Related certification if applicable |
| delivery_date | Datetime | When delivered |
| delivery_method | Selection | Email / Recorded Post / Hand Delivery |
| email_opened | Boolean | If email, was it opened? |
| email_opened_date | Datetime | When email was opened |
| signature_file | Binary | Signed receipt if hand delivery |
| tracking_number | Char | If recorded post |
| evidence_file | Binary | Screenshot, receipt, etc. |
| notes | Text | Additional notes |

#### 7.2.8 Right to Rent Check (`property_fielder.right.to.rent`)

| Field | Type | Description |
|-------|------|-------------|
| tenant_id | Many2one | Tenant (res.partner) |
| property_id | Many2one | Property (for the tenancy) |
| check_date | Date | When check was performed |
| check_type | Selection | Manual / Online Share Code |
| status | Selection | Passed / Failed / Time-Limited |
| expiry_date | Date | If time-limited, when follow-up required |
| documents_checked | Text | List of documents verified |
| share_code | Char | Home Office share code if used |
| evidence_ids | Many2many | Uploaded document copies |
| checked_by | Many2one | User who performed check (res.users) |
| notes | Text | Additional notes |

#### 7.2.9 Key Set (`property_fielder.key.set`)

> **Design Decision (Per Gemini Review):** Field inspectors spend ~20% of time managing keys. Tracking key location, check-in/check-out is critical for operations.

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Key set identifier (e.g., "SET-001") |
| property_id | Many2one | Property these keys belong to |
| key_count | Integer | Number of keys in set |
| key_types | Text | Description (e.g., "Front door, Back door, Meter cupboard") |
| location | Selection | Office / With Inspector / With Tenant / With Landlord / Lost |
| current_holder_id | Many2one | Current holder (res.partner or res.users) |
| office_location | Char | If at office, which key safe/drawer |
| notes | Text | Additional notes |
| active | Boolean | Is this key set active? |

#### 7.2.10 Key Check-Out Log (`property_fielder.key.checkout`)

| Field | Type | Description |
|-------|------|-------------|
| key_set_id | Many2one | Key set being checked out |
| property_id | Many2one | Related property |
| checked_out_by | Many2one | User who checked out (res.users) |
| checkout_date | Datetime | When checked out |
| expected_return | Datetime | When expected back |
| checkin_date | Datetime | When actually returned |
| checkin_by | Many2one | User who checked in (res.users) |
| job_id | Many2one | Related job if applicable |
| notes | Text | Notes |
| state | Selection | Checked Out / Returned / Overdue / Lost |

#### 7.2.11 Contractor Accreditation (`property_fielder.contractor.accreditation`)

> **Design Decision (Per Gemini Review):** UK liability requires verifying contractor accreditation before assignment. Block job assignment if license expired.

| Field | Type | Description |
|-------|------|-------------|
| contractor_id | Many2one | Contractor (res.partner) |
| accreditation_type | Selection | Gas Safe / NAPIT / NICEIC / OFTEC / HETAS / Other |
| registration_number | Char | Registration/license number |
| issue_date | Date | When issued |
| expiry_date | Date | When expires |
| verification_date | Date | When last verified |
| verification_method | Selection | Online Check / Certificate Copy / Phone Verification |
| certificate_file | Binary | Uploaded certificate copy |
| is_valid | Boolean | Computed: Is currently valid? |
| notes | Text | Additional notes |

#### 7.2.12 Inspector Skill (`property_fielder.inspector.skill`)

> **Design Decision (Per Gemini Review):** Inspector should only be assignable to jobs if they possess the required certification/skill.

| Field | Type | Description |
|-------|------|-------------|
| inspector_id | Many2one | Inspector (res.users) |
| certification_type_id | Many2one | Certification type they can perform |
| skill_level | Selection | Basic / Advanced / Expert |
| qualification_number | Char | Their qualification number |
| qualification_expiry | Date | When qualification expires |
| is_active | Boolean | Can currently perform this inspection type? |
| notes | Text | Additional notes |

> **Design Decision (Per Gemini Review - Iteration 2 - Skill Levels):**
> For Asbestos inspections, a standard surveyor cannot perform a "Refurbishment & Demolition Survey" - only a "Management Survey." The `skill_level` field prevents assigning complex jobs to basic inspectors:
> - **Basic:** Management Survey only (Asbestos), Standard Gas Safety (Gas), Condition Report (EICR)
> - **Advanced:** Refurbishment & Demolition Survey (Asbestos), Commercial Gas (Gas), Full EICR
> - **Expert:** Complex/High-Risk assessments, Training/Mentoring capability

#### 7.2.13 How to Rent Guide Version (`property_fielder.how.to.rent.version`)

> **Design Decision (Per Gemini Review):** Section 21 validity depends on serving the version current at tenancy start. Must track versions.

| Field | Type | Description |
|-------|------|-------------|
| version | Char | Version identifier (e.g., "October 2023") |
| effective_from | Date | When this version became current |
| effective_to | Date | When superseded (null if current) |
| document_file | Binary | PDF of this version |
| is_current | Boolean | Is this the current version? |
| notes | Text | Notes about changes in this version |

#### 7.2.14 HMO License (`property_fielder.hmo.license`)

> **Design Decision (Per Gemini Review - Iteration 2):** Operating an HMO without a license is a criminal offense under Housing Act 2004. Cannot onboard a compliant HMO without recording license details.

| Field | Type | Description |
|-------|------|-------------|
| property_id | Many2one | Link to property |
| license_number | Char | Local authority license number |
| local_authority | Char | Issuing local authority |
| issue_date | Date | License issue date |
| expiry_date | Date | License expiry date |
| max_occupants | Integer | Maximum permitted occupants |
| max_households | Integer | Maximum permitted households |
| conditions | Text | Specific license conditions |
| license_type | Selection | Mandatory / Additional / Selective |
| document_file | Binary | Scanned license document |
| is_active | Boolean | Computed: issue_date <= today <= expiry_date |
| days_until_expiry | Integer | Computed: days remaining |

> **Compliance Rule:** If `property.property_category = 'hmo'` AND no active HMO License exists, property status = Non-Compliant.

#### 7.2.15 EPC Exemption (`property_fielder.epc.exemption`)

> **Design Decision (Per Gemini Review - Iteration 2):** If a property cannot reach EPC E or C rating, landlord must register exemption on PRS Exemptions Register.

| Field | Type | Description |
|-------|------|-------------|
| property_id | Many2one | Link to property |
| exemption_type | Selection | High Cost / All Improvements Made / Consent Refused / Devaluation / Wall Insulation |
| registration_date | Date | Date registered on PRS Exemptions Register |
| expiry_date | Date | Exemption expiry (5 years from registration) |
| reference_number | Char | PRS Exemptions Register reference |
| evidence_file | Binary | Supporting evidence document |
| is_active | Boolean | Computed: registration_date <= today <= expiry_date |

> **Compliance Rule:** If `property.epc_rating < 'E'` AND no active EPC Exemption exists, property status = Non-Compliant.

#### 7.2.16 EWS1 Form (`property_fielder.ews1.form`)

> **Design Decision (Per Gemini Review - Iteration 2):** For blocks over 18m or with specific cladding issues, EWS1 (External Wall System) form is required. This is the biggest pain point in UK block management.

| Field | Type | Description |
|-------|------|-------------|
| property_id | Many2one | Link to Block property (parent) |
| form_date | Date | Date of EWS1 assessment |
| assessor_name | Char | Name of qualified assessor |
| assessor_registration | Char | RICS/CABE registration number |
| rating | Selection | A1 (No combustible) / A2 (Combustible, no remediation) / A3 (Combustible, remediation) / B1 (Remediation required) / B2 (Interim measures) |
| remediation_required | Boolean | Computed: rating in ['A3', 'B1', 'B2'] |
| remediation_cost_estimate | Float | Estimated remediation cost |
| remediation_deadline | Date | Deadline for remediation works |
| document_file | Binary | Scanned EWS1 form |
| notes | Text | Additional notes |

> **Compliance Rule:** If `property.is_block = True` AND `property.height_meters >= 18` AND no EWS1 Form exists, property status = Non-Compliant.

---

## 8. Workflow Specifications

### 8.1 Property Onboarding Workflow

```text
START
  │
  ▼
[User creates new property or imports batch]
  │
  ▼
[System validates required fields]
  │
  ├──(Invalid)──► [Show errors, prompt for corrections]
  │
  ▼ (Valid)
[System geocodes address]
  │
  ▼
[System determines required certifications based on property type/category]
  │
  ▼
[User confirms required certifications]
  │
  ▼
[System performs gap analysis - all certs are "missing" for new property]
  │
  ▼
[User opts to schedule initial inspections]
  │
  ├──(Yes)──► [Create inspection records for each required cert type]
  │                │
  │                ▼
  │           [Property status = Active]
  │
  ├──(No)──► [Property status = Draft (incomplete)]
  │
  ▼
END
```

### 8.2 Bulk Job Creation Workflow

```text
START
  │
  ▼
[Dispatcher opens "Inspections Due" list view]
  │
  ▼
[System displays properties with certifications expiring in 14-30 days]
  │
  ▼
[Dispatcher applies filters: cert type, area, owner]
  │
  ▼
[Dispatcher selects multiple properties via checkboxes]
  │
  ▼
[Dispatcher clicks "Create Jobs for Selected"]
  │
  ▼
[System opens wizard with options:]
  │  - Target date range
  │  - Auto-assign inspectors (Y/N)
  │
  ▼
[User confirms]
  │
  ▼
[System creates inspection records for each property/cert type]
  │
  ▼
[System creates field service job for each inspection]
  │
  ▼
[System reports: X jobs created, Y skipped (with reasons)]
  │
  ▼
[Dispatcher proceeds to Dispatch View for optimization]
  │
  ▼
END
```

### 8.3 Fault Recording Workflow

```text
START: Inspection Result = FAIL
  │
  ▼
[Inspector MUST record at least one fault]
  │
  ▼
[Fault Recording Form:]
  │  - Select fault code (filtered by cert type)
  │  - Category auto-populated from code (Cat 1 or Cat 2)
  │  - Enter description
  │  - Enter location in property
  │  - Capture photos (MANDATORY for Cat 1)
  │  - Record immediate actions taken
  │  - Gas capped? Supply isolated?
  │
  ▼
[System calculates remediation deadline:]
  │  - Cat 1: Current time + cert_type.cat1_remediation_hours
  │  - Cat 2: Current date + cert_type.cat2_remediation_days
  │
  ▼
[System creates Remediation Work Order]
  │
  ▼
[System creates draft Re-check Inspection]
  │
  ▼
[System updates Property status = "Non-Compliant"]
  │
  ▼
[System sends notifications:]
  │  - Owner (URGENT for Cat 1)
  │  - Tenant (access required for remediation)
  │  - Dispatcher/Manager (action required)
  │
  ▼
END
```

### 8.4 Remediation & Re-Check Workflow

```text
START: Fault recorded
  │
  ▼
[Remediation work order in queue]
  │
  ▼
[Dispatcher/Contractor schedules remediation]
  │
  ├──(Not scheduled within deadline/2)──► [System alerts dispatcher]
  │
  ▼
[Contractor performs remediation work]
  │
  ▼
[Contractor records completion with evidence photos]
  │
  ▼
[System triggers re-check scheduling]
  │
  ▼
[Dispatcher schedules re-check inspection]
  │
  ▼
[Re-check must be BEFORE original remediation deadline]
  │
  ▼
[Inspector performs re-check]
  │
  ▼
[Inspector reviews original fault details]
  │
  ▼
[Inspector records result:]
  │
  ├──(PASS)──► [Fault status = Re-check Passed]
  │                │
  │                ▼
  │           [Property status = Active (Compliant)]
  │                │
  │                ▼
  │           [Certificate issued]
  │                │
  │                ▼
  │           [Notify owner - certificate attached]
  │
  ├──(FAIL)──► [Fault status = Re-check Failed]
                   │
                   ▼
              [PROPERTY OFFBOARDING TRIGGERED]
                   │
                   ▼
              [Property status = Offboarded]
                   │
                   ▼
              [Cancel all pending jobs]
                   │
                   ▼
              [Generate offboarding report]
                   │
                   ▼
              [Notify owner - formal letter]
                   │
                   ▼
              [Notify tenant (Cat 1 - property may be uninhabitable)]
```

### 8.5 Tenant Access Confirmation Workflow

```text
START: Job scheduled
  │
  ▼
[System sends appointment notification to tenant]
  │  - Email and/or SMS
  │  - Includes: Date, Time, Duration, Inspector contact
  │  - Includes: Confirm/Decline links
  │
  ▼
[System waits for response]
  │
  ├──(Confirmed)──► [Access status = Confirmed]
  │                      │
  │                      ▼
  │                 [Job proceeds as scheduled]
  │
  ├──(Declined)──► [Access status = Declined]
  │                    │
  │                    ▼
  │               [Alert dispatcher]
  │                    │
  │                    ▼
  │               [Dispatcher reschedules with tenant alternatives]
  │
  ├──(No response within 48h)──► [Send reminder]
  │                                   │
  │                                   ▼
  │                              [Wait another 24h]
  │                                   │
  │                              ├──(Response)──► [Process response]
  │                              │
  │                              ├──(No response)──► [Alert dispatcher]
  │                                                       │
  │                                                       ▼
  │                                                  [Call tenant directly]
  │
  ▼
END
```

### 8.6 No-Access Handling Workflow

```text
START: Inspector arrives at property
  │
  ▼
[Inspector cannot gain access]
  │
  ▼
[Inspector records No-Access with reason:]
  │  - No Answer
  │  - Access Refused
  │  - Property Inaccessible
  │  - Tenant Absent (agreed time)
  │
  ▼
[System increments no_access_count for property]
  │
  ▼
[System notifies owner with reason]
  │
  ▼
[System auto-schedules re-visit]
  │
  ├──(no_access_count < 3)──► [Create new job for re-visit]
  │                                │
  │                                ▼
  │                           [Notify tenant of new appointment]
  │
  ├──(no_access_count >= 3)──► [ESCALATE to manager]
                                    │
                                    ▼
                               [Manager decides:]
                                    │
                                    ├──(Continue trying)──► [Manual scheduling]
                                    │
                                    ├──(Offboard property)──► [Offboarding workflow]
```

### 8.7 Escalation & Deadline Monitoring

```text
CRON JOB: Runs every hour
  │
  ▼
[Query all open faults where deadline approaching]
  │
  ▼
[For Cat 1 faults:]
  │  - 4 hours before deadline: Alert manager
  │  - 2 hours before deadline: Alert senior manager
  │  - Past deadline: Alert director + auto-escalate
  │
  ▼
[For Cat 2 faults:]
  │  - 7 days before deadline: Alert dispatcher
  │  - 3 days before deadline: Alert manager
  │  - 1 day before deadline: Alert senior manager
  │  - Past deadline: Alert director + auto-escalate
  │
  ▼
[For certifications expiring soon:]
  │  - 90 days: Email owner
  │  - 60 days: Email owner + manager
  │  - 30 days: Email all + create inspection if not exists
  │  - 14 days: URGENT notification
  │  - Expired: Compliance violation logged
  │
  ▼
END
```

### 8.8 Void Management Workflow

> **Design Decision (Per Gemini Review - Iteration 2):** When a property is empty ("Void"), compliance requirements change. Insurance policies typically require weekly security visits and water system flushing (to prevent Legionella stagnation).

```text
TRIGGER: Property state changes to "Vacant"
  │
  ▼
[System activates "Void Profile" for property]
  │
  ├──► [Suspend annual Gas/EICR scheduling]
  │
  ├──► [Create recurring "Security & Flush" job template]
  │    │
  │    ├── Frequency: Weekly
  │    ├── Duration: 30 minutes
  │    ├── Tasks: Security check, water flush, heating check
  │    └── Inspector: Any available
  │
  ├──► [Notify property manager of void status]
  │
  ▼
[Weekly jobs auto-generated until property re-let]
  │
  ▼
TRIGGER: Property state changes from "Vacant" to "Active"
  │
  ├──► [Deactivate Void Profile]
  ├──► [Cancel remaining Security & Flush jobs]
  ├──► [Resume normal certification scheduling]
  └──► [Trigger pre-tenancy inspection if required]
```

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.8.1 | System SHALL detect property state change to Vacant | HIGH |
| FR-8.8.2 | Void Profile SHALL generate weekly Security & Flush jobs | HIGH |
| FR-8.8.3 | Security & Flush template SHALL include: External security check, Internal security check, Run all taps for 2 minutes, Check heating system, Check for pest evidence | HIGH |
| FR-8.8.4 | System SHALL suspend annual certification scheduling during void | MEDIUM |
| FR-8.8.5 | System SHALL resume normal scheduling when property re-let | HIGH |
| FR-8.8.6 | System SHALL log all void period activity for insurance compliance | HIGH |

### 8.9 Legal Entry (Forced Access) Workflow

> **Design Decision (Per Gemini Review - Iteration 2):** In emergency situations (Gas leak, Water leak - Awaab's Law "Emergency"), the landlord has a right to enter. This workflow authorizes "Locksmith Entry" for Cat 1/Emergency situations, separate from the standard "Try again later" loop.

```text
TRIGGER: Cat 1/Emergency fault AND 2+ failed access attempts
  │
  ▼
[System flags property for "Legal Entry Review"]
  │
  ▼
[Manager reviews situation]
  │
  ├──(Not emergency)──► [Continue standard access attempts]
  │
  ▼ (Emergency confirmed)
[Manager authorizes Legal Entry]
  │
  ├──► [System generates "Notice of Entry" letter (24 hours)]
  ├──► [System books locksmith contractor]
  ├──► [System notifies tenant of forced entry date/time]
  │
  ▼
[Locksmith + Inspector attend]
  │
  ├──► [Log entry with photos of lock state]
  ├──► [Complete emergency inspection/repair]
  ├──► [Secure property (new lock if required)]
  ├──► [Leave new keys with tenant/key holder]
  │
  ▼
[System logs all evidence for legal defence]
```

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-8.9.1 | System SHALL flag properties for Legal Entry Review after 2+ failed access attempts on Cat 1/Emergency faults | HIGH |
| FR-8.9.2 | Manager SHALL authorize Legal Entry with reason and evidence | HIGH |
| FR-8.9.3 | System SHALL generate Notice of Entry letter (minimum 24 hours notice) | HIGH |
| FR-8.9.4 | System SHALL track locksmith booking and attendance | HIGH |
| FR-8.9.5 | Inspector SHALL photograph lock state before and after entry | HIGH |
| FR-8.9.6 | System SHALL log all Legal Entry evidence for liability defence | HIGH |
| FR-8.9.7 | Legal Entry SHALL only be available for Immediate/Emergency SLA faults | HIGH |

---

## 9. Integration Requirements

### 9.1 External Service Integrations

| Integration | Purpose | Priority | Status |
|-------------|---------|----------|--------|
| **Timefold Solver** | Route optimization | HIGH | ✅ Implemented |
| **OSRM** | Travel time calculation | HIGH | ✅ Implemented |
| **Mapbox GL JS** | Map rendering | HIGH | ✅ Implemented |
| **UK Postcode API** | Address validation/geocoding | MEDIUM | ❌ Required |
| **Email Service** | Transactional emails | HIGH | ✅ Via Odoo |
| **SMS Gateway** | SMS notifications | MEDIUM | ❌ Required |
| **Document Storage** | Certificate/report storage | HIGH | ✅ Via Odoo |
| **Calendar Integration** | Sync with Google/Outlook | LOW | ❌ Future |

### 9.2 API Requirements

#### 9.2.1 Mobile App API

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/jobs` | GET | List jobs for inspector |
| `/api/v1/jobs/{id}` | GET | Get job details |
| `/api/v1/jobs/{id}/checkin` | POST | Check in to job |
| `/api/v1/jobs/{id}/checkout` | POST | Check out of job |
| `/api/v1/jobs/{id}/complete` | POST | Complete job with result |
| `/api/v1/inspections/{id}` | PUT | Update inspection |
| `/api/v1/inspections/{id}/faults` | POST | Record fault |
| `/api/v1/faults/{id}/photos` | POST | Upload fault photos |
| `/api/v1/sync` | POST | Bulk sync offline data |
| `/api/v1/routes` | GET | Get optimized routes |

#### 9.2.2 External Webhooks

| Event | Webhook Payload |
|-------|-----------------|
| Job Created | Job details, property, inspection |
| Job Completed | Job details, result, faults |
| Fault Recorded | Fault details, category, deadline |
| Certificate Issued | Certificate details, PDF URL |
| Schedule Changed | Change details, affected jobs |

### 9.3 Data Import/Export

| Format | Import | Export | Purpose |
|--------|--------|--------|---------|
| CSV | ✅ | ✅ | Properties, bulk data |
| Excel (XLSX) | ✅ | ✅ | Properties with validation |
| PDF | ❌ | ✅ | Certificates, reports |
| iCalendar (ICS) | ❌ | ✅ | Schedule export |
| JSON | ✅ | ✅ | API data exchange |

---

## 10. Mobile App Requirements

### 10.1 Functional Requirements

#### 10.1.1 Authentication

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-1.1 | App SHALL authenticate with Odoo backend | HIGH |
| MA-1.2 | App SHALL support biometric authentication | MEDIUM |
| MA-1.3 | App SHALL maintain session for offline access | HIGH |
| MA-1.4 | App SHALL auto-logout after configurable inactivity | MEDIUM |

#### 10.1.2 Job Management

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-2.1 | App SHALL display today's jobs with route order | HIGH |
| MA-2.2 | App SHALL display job details: property, time, cert type | HIGH |
| MA-2.3 | App SHALL navigate to property using Google/Apple Maps | HIGH |
| MA-2.4 | App SHALL support GPS-based check-in/check-out | HIGH |
| MA-2.5 | Check-in SHALL validate inspector is within geofence of property | HIGH |
| MA-2.6 | Geofence validation SHALL allow override with mandatory reason code | HIGH |
| MA-2.7 | Override SHALL force capture of GPS timestamp for audit trail | HIGH |
| MA-2.8 | Override reasons: GPS Inaccuracy, New Build (not on maps), Rural Location | HIGH |
| MA-2.9 | App SHALL provide "View Previous Inspection" button on job details | MEDIUM |
| MA-2.10 | Previous inspection view SHALL be read-only | MEDIUM |
| MA-2.11 | Previous inspection SHALL show: Last year's readings, meter location, boiler make/model | MEDIUM |

> **Design Decision (Per Gemini Review - Iteration 2):** When doing a Gas Safety check, the engineer needs to see the *previous* readings (meter location, boiler make/model) to verify consistency. This reduces errors and speeds up inspections.

#### 10.1.3 Inspection Recording (Template-Driven)

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-3.1 | App SHALL load inspection template for job's certification type | HIGH |
| MA-3.2 | App SHALL display template sections in configured order | HIGH |
| MA-3.3 | App SHALL support skip logic / conditional branching | HIGH |
| MA-3.4 | Skip logic SHALL hide sections based on prior answers (e.g., "No gas?" → hide Gas section) | HIGH |
| MA-3.5 | App SHALL support response types: yes/no, severity scale, numeric, text, photo | HIGH |
| MA-3.6 | App SHALL enforce mandatory items before completion | HIGH |
| MA-3.7 | App SHALL display guidance notes per item | MEDIUM |
| MA-3.8 | App SHALL auto-create defect when item triggers threshold | HIGH |
| MA-3.9 | App SHALL record pass/fail/conditional result | HIGH |
| MA-3.10 | App SHALL enforce fault recording when result = fail | HIGH |
| MA-3.11 | App SHALL capture photos with GPS tagging | HIGH |
| MA-3.12 | App SHALL capture digital signatures | HIGH |

#### 10.1.4 Fault/Defect Recording

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-4.1 | App SHALL display native fault codes for cert type (C1, ID, AR, etc.) | HIGH |
| MA-4.2 | App SHALL auto-compute severity_sla based on fault code | HIGH |
| MA-4.3 | App SHALL display both native code AND severity SLA to inspector | HIGH |
| MA-4.4 | App SHALL enforce photo capture for Immediate SLA defects | HIGH |
| MA-4.5 | App SHALL record immediate actions taken (gas capped, supply isolated) | HIGH |
| MA-4.6 | App SHALL show remediation deadline after defect recorded | HIGH |
| MA-4.7 | App SHALL allow linking defects to HHSRS hazards | MEDIUM |

#### 10.1.5 Photo Capture & Image Handling

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-5.1 | App SHALL compress images before storing locally | HIGH |
| MA-5.2 | Compression target: <500KB per image (from ~10MB originals) | HIGH |
| MA-5.3 | App SHALL maintain acceptable quality for compliance evidence | HIGH |
| MA-5.4 | App SHALL embed GPS coordinates in image EXIF data | HIGH |
| MA-5.5 | App SHALL embed timestamp in image EXIF data | HIGH |
| MA-5.6 | App SHALL support batch photo upload (max 50 photos per inspection) | MEDIUM |
| MA-5.7 | App SHALL provide basic image annotation tools (red pen, arrow, circle) | MEDIUM |
| MA-5.8 | Annotations SHALL be saved as overlay layer (original image preserved) | MEDIUM |
| MA-5.9 | App SHALL burn Date/Time/GPS watermark onto photo pixels for Cat 1/Cat 2 evidence | HIGH |
| MA-5.10 | Watermark SHALL be visible text overlay (not just EXIF metadata) | HIGH |
| MA-5.11 | Watermark format: "DD/MM/YYYY HH:MM - Lat: XX.XXX, Lon: XX.XXX" | MEDIUM |

> **Design Decision (Per Gemini Review - Iteration 2):** Inspectors often need to draw circles or arrows on photos to highlight specific defects (e.g., crack in wall, damp patch). This reduces ambiguity for remediation contractors.

> **Design Decision (Per Gemini Review - Iteration 3 - Photo Watermarking):** EXIF data is often stripped when photos are emailed or converted to PDF for certificates. Burning the timestamp and GPS coordinates directly onto the photo pixels ensures the evidence is preserved regardless of how the image is processed.

#### 10.1.6 Offline Support & Sync

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-6.1 | App SHALL work offline with cached data | HIGH |
| MA-6.2 | App SHALL queue changes for sync when online | HIGH |
| MA-6.3 | App SHALL indicate sync status (synced/pending) per item | HIGH |
| MA-6.4 | App SHALL auto-sync when connectivity restored | HIGH |
| MA-6.5 | App SHALL prioritize text data sync over photo upload | HIGH |
| MA-6.6 | App SHALL handle sync conflicts gracefully (last-write-wins or prompt) | HIGH |
| MA-6.7 | App SHALL compress images BEFORE queuing for sync | HIGH |
| MA-6.8 | App SHALL display estimated data size pending upload | MEDIUM |
| MA-6.9 | App SHALL warn if pending upload exceeds 100MB | MEDIUM |
| MA-6.10 | App SHALL implement Check-out/Check-in locking for inspections | HIGH |
| MA-6.11 | When inspector downloads job, inspection record SHALL be locked in Odoo | HIGH |
| MA-6.12 | Lock SHALL be released on upload OR manual release OR 24-hour timeout | HIGH |
| MA-6.13 | Locked inspections SHALL show "In Progress by [Inspector]" in Odoo | MEDIUM |

> **Design Decision (Per Gemini Review - Iteration 2 - Sync Locking):** Syncing complex nested data (Inspection → Section → Item → Response → Photo) bi-directionally is the #1 cause of failure in field service apps. A strict "Check-out/Check-in" lock model prevents concurrent edits and data corruption.

#### 10.1.7 Lone Worker Safety

> **Design Decision (Per Gemini Review):** Field inspectors enter properties alone. Safety timer and panic button protect workers and reduce liability.

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-7.1 | App SHALL start safety timer on job check-in | HIGH |
| MA-7.2 | Timer duration SHALL be job estimated duration + configurable buffer (default 30 min) | HIGH |
| MA-7.3 | App SHALL display countdown timer to inspector | MEDIUM |
| MA-7.4 | App SHALL alert inspector 5 minutes before timer expires | HIGH |
| MA-7.5 | Inspector SHALL be able to extend timer if needed | HIGH |
| MA-7.6 | If timer expires without check-out, system SHALL alert Dispatcher | HIGH |
| MA-7.7 | Alert SHALL include: Inspector name, Property address, Last known GPS, Time overdue | HIGH |
| MA-7.8 | App SHALL provide "Panic Button" for emergency situations | HIGH |
| MA-7.9 | Panic Button SHALL immediately alert Dispatcher with GPS location | HIGH |
| MA-7.10 | Panic Button SHALL be accessible from any screen in the app | HIGH |
| MA-7.11 | System SHALL log all safety timer events for audit | MEDIUM |

#### 10.1.8 Draft/Partial Save Mode

> **Design Decision (Per Gemini Review):** Inspectors may need to pause (battery dying, waiting for keys). Allow saving partial state.

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-8.1 | App SHALL allow saving inspection in "Draft" state | HIGH |
| MA-8.2 | Draft save SHALL NOT trigger validation rules | HIGH |
| MA-8.3 | Draft save SHALL persist to local Hive database | HIGH |
| MA-8.4 | App SHALL display "Draft" indicator on incomplete inspections | HIGH |
| MA-8.5 | Inspector SHALL be able to resume draft inspection | HIGH |
| MA-8.6 | Draft inspections SHALL NOT sync to backend until completed | HIGH |
| MA-8.7 | App SHALL warn if draft inspection is older than 24 hours | MEDIUM |

#### 10.1.9 Keyword Safety Check (Liability Protection)

> **Design Decision (Per Gemini Review):** If inspector notes mention hazard keywords but records "Pass", block submission to prevent liability.

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-9.1 | App SHALL scan text fields for hazard keywords before submission | HIGH |
| MA-9.2 | Hazard keywords: "mould", "mold", "damp", "leak", "gas smell", "crack", "unsafe", "dangerous", "asbestos", "carbon monoxide" | HIGH |
| MA-9.3 | If hazard keyword found AND result = Pass, app SHALL block submission | HIGH |
| MA-9.4 | Block message: "Your notes mention [keyword]. Please record a Defect or remove the observation." | HIGH |
| MA-9.5 | Inspector SHALL be able to override with mandatory reason | MEDIUM |
| MA-9.6 | Override SHALL be logged for manager review | HIGH |
| MA-9.7 | App SHALL display disclaimer: "This check is an aid only. The Inspector remains fully liable for accurate fault recording." | HIGH |

> **Design Decision (Per Gemini Review - Iteration 2 - Liability Disclaimer):** The Keyword Check is a double-edged sword. If the system *fails* to flag a keyword (e.g., inspector types "mold" instead of "mould"), the landlord could argue "The system didn't warn me, so it's your software's fault." The disclaimer protects the software vendor and reinforces inspector responsibility.

### 10.2 Technical Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| MA-T1 | Built with Flutter for iOS/Android | HIGH |
| MA-T2 | Offline storage using Hive | HIGH |
| MA-T3 | Background sync using WorkManager/Background Fetch | HIGH |
| MA-T4 | Minimum OS: iOS 14, Android 9 | HIGH |
| MA-T5 | Target device: Budget Android phones (2GB RAM) | HIGH |
| MA-T6 | Image compression using flutter_image_compress or similar | HIGH |
| MA-T7 | Compression ratio: configurable (default 80% quality, max 500KB) | HIGH |

---

## 11. Reporting Requirements

### 11.1 Compliance Reports

| Report | Description | Frequency | Priority |
|--------|-------------|-----------|----------|
| **Portfolio Compliance Summary** | Overall compliance status, % compliant | Daily/Weekly | HIGH |
| **Expiring Certifications** | List of certs expiring in next 30/60/90 days | Weekly | HIGH |
| **Overdue Inspections** | Inspections past due date | Daily | HIGH |
| **Fault Summary** | Open Cat 1/Cat 2 faults by property/type | Daily | HIGH |
| **Remediation Status** | Remediation work orders by status | Daily | HIGH |
| **Offboarded Properties** | Properties offboarded with reasons | Monthly | MEDIUM |

### 11.2 Operational Reports

| Report | Description | Frequency | Priority |
|--------|-------------|-----------|----------|
| **Inspector Productivity** | Jobs completed per inspector per day | Weekly | MEDIUM |
| **Route Efficiency** | Actual vs planned travel time | Weekly | MEDIUM |
| **No-Access Rate** | No-access visits by area/inspector | Weekly | MEDIUM |
| **SLA Compliance** | % faults resolved within deadline | Weekly | HIGH |
| **Optimization Metrics** | Optimization success rate, duration | Weekly | LOW |

### 11.3 Audit Reports

| Report | Description | Frequency | Priority |
|--------|-------------|-----------|----------|
| **Certificate History** | All certificates for property over time | On-demand | HIGH |
| **Inspection History** | All inspections with results | On-demand | HIGH |
| **Fault History** | All faults and resolutions | On-demand | HIGH |
| **Compliance Timeline** | Property compliance over time | On-demand | MEDIUM |
| **Notification Log** | All notifications sent | On-demand | MEDIUM |

---

## 12. Non-Functional Requirements

### 12.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-P1 | Page load time | < 2 seconds |
| NFR-P2 | Route optimization (50 jobs) | < 30 seconds |
| NFR-P3 | Map rendering | < 1 second |
| NFR-P4 | Bulk job creation (100 jobs) | < 10 seconds |
| NFR-P5 | Mobile app sync | < 5 seconds |
| NFR-P6 | Concurrent users supported | 50+ |

### 12.2 Availability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-A1 | System uptime | 99.5% |
| NFR-A2 | Planned maintenance window | Sunday 02:00-06:00 |
| NFR-A3 | Mobile app offline capability | 100% (with cache) |

### 12.3 Security

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-S1 | HTTPS for all traffic | HIGH |
| NFR-S2 | OAuth2/JWT for API authentication | HIGH |
| NFR-S3 | Role-based access control | HIGH |
| NFR-S4 | Audit logging for all changes | HIGH |
| NFR-S5 | GDPR compliance for personal data | HIGH |
| NFR-S6 | Data encryption at rest | MEDIUM |

### 12.4 Scalability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-SC1 | Properties supported | 10,000+ |
| NFR-SC2 | Inspections per year | 50,000+ |
| NFR-SC3 | Concurrent mobile users | 100+ |
| NFR-SC4 | Historical data retention | 6+ years |

### 12.5 Usability

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-U1 | Responsive design (desktop/tablet) | HIGH |
| NFR-U2 | Mobile-first app design | HIGH |
| NFR-U3 | Keyboard navigation support | MEDIUM |
| NFR-U4 | WCAG 2.1 AA accessibility | MEDIUM |

### 12.6 Audit & Liability Protection

> **Design Decision:** Comprehensive audit logging protects the managing agent from liability claims. Every compliance-related action must be logged with timestamp, user, and evidence.

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-L1 | All compliance state changes SHALL be logged to Property Compliance Log | HIGH |
| NFR-L2 | Logs SHALL be immutable (no delete, no edit) | HIGH |
| NFR-L3 | Logs SHALL include: timestamp, user, action, old value, new value | HIGH |
| NFR-L4 | Access attempts SHALL be logged with GPS evidence | HIGH |
| NFR-L5 | Document delivery SHALL be logged with proof of service | HIGH |
| NFR-L6 | Defect creation SHALL log inspector, time, location, photos | HIGH |
| NFR-L7 | Remediation completion SHALL log contractor, time, evidence | HIGH |
| NFR-L8 | System SHALL generate "Liability Defence Pack" per property on demand | MEDIUM |
| NFR-L9 | Defence Pack SHALL include: All access attempts, notifications, defects, remediations | MEDIUM |
| NFR-L10 | Logs SHALL be retained for minimum 6 years (UK limitation period) | HIGH |

### 12.7 Data Migration & Legacy Import

> **Design Decision:** Most clients will have existing compliance data in spreadsheets, legacy systems, or paper records. A robust import wizard is critical for onboarding.

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-M1 | System SHALL provide Property Import Wizard | HIGH |
| NFR-M2 | Import SHALL support CSV/Excel format | HIGH |
| NFR-M3 | Import SHALL validate required fields before processing | HIGH |
| NFR-M4 | Import SHALL geocode addresses automatically | HIGH |
| NFR-M5 | Import SHALL support dry-run mode (preview without commit) | HIGH |
| NFR-M6 | Import SHALL generate error report for failed rows | HIGH |
| NFR-M7 | System SHALL provide Certification Import Wizard | HIGH |
| NFR-M8 | Cert Import SHALL link to existing properties by UPRN or address | HIGH |
| NFR-M9 | Cert Import SHALL support PDF upload for legacy certificates | MEDIUM |
| NFR-M10 | System SHALL support bulk photo upload with property matching | MEDIUM |
| NFR-M11 | Import SHALL log all imported records for audit | HIGH |
| NFR-M12 | Import SHALL support rollback of failed batch imports | MEDIUM |

### 12.8 UX Requirements (Production Analysis - December 2024)

> **Design Decision (Per Gemini UX Analysis):** Following production UX analysis using Gemini 2.0 Flash, the following UX requirements were identified to improve the property manager workflow. Initial UX score: 5/10. Target: 8/10.

#### 12.8.1 Property List View

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UX-1.1 | Property cards SHALL use color-coded compliance badges (green=Compliant, amber=Expiring, red=Non-Compliant/Missing) | HIGH |
| NFR-UX-1.2 | Property list SHALL provide advanced filtering by location, compliance status, property type, owner | HIGH |
| NFR-UX-1.3 | Compliance badges SHALL use minimum 14px font size for readability | MEDIUM |
| NFR-UX-1.4 | Property cards SHALL display tenant name and key action buttons (View, Schedule Inspection) | MEDIUM |
| NFR-UX-1.5 | Property cards SHALL show next inspection date if scheduled | MEDIUM |
| NFR-UX-1.6 | Property cards SHALL show property thumbnail image if available | MEDIUM |

#### 12.8.2 Property Detail Form

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UX-2.1 | FLAGE+ compliance section SHALL use traffic light indicators (green/amber/red circles) for each category | HIGH |
| NFR-UX-2.2 | Form fields SHALL use modern Odoo widgets (date pickers, searchable dropdowns) where available | MEDIUM |
| NFR-UX-2.3 | Tab labels SHALL include descriptive icons alongside text | LOW |
| NFR-UX-2.4 | FLAGE+ section SHALL be prominently positioned and visible without scrolling | HIGH |
| NFR-UX-2.5 | Compliance status badges SHALL include expiry date or "Missing" label | HIGH |

#### 12.8.3 Dispatch View

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UX-3.1 | Search bar SHALL be minimum 300px wide on desktop for prominent discovery | MEDIUM |
| NFR-UX-3.2 | Filter pills (All/Unassigned/Scheduled/Urgent) SHALL have tooltips explaining each status | HIGH |
| NFR-UX-3.3 | Job cards SHALL display job type icons (wrench for repair, clipboard for inspection) | MEDIUM |
| NFR-UX-3.4 | Job cards SHALL display inspector name if assigned | HIGH |
| NFR-UX-3.5 | Job cards SHALL display certification type being inspected | HIGH |
| NFR-UX-3.6 | Empty states SHALL provide helpful guidance and call-to-action buttons | HIGH |

#### 12.8.4 General UX Standards

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-UX-4.1 | All icons and filters SHALL have descriptive tooltips | MEDIUM |
| NFR-UX-4.2 | Visual hierarchy SHALL guide users with consistent whitespace (8px, 16px, 24px grid) | LOW |
| NFR-UX-4.3 | All views SHALL be mobile-responsive (minimum 375px viewport) | HIGH |
| NFR-UX-4.4 | Loading states SHALL display skeleton loaders or spinners | MEDIUM |
| NFR-UX-4.5 | Error states SHALL display user-friendly messages with retry options | HIGH |
| NFR-UX-4.6 | Success states SHALL provide visual confirmation (toast notifications) | MEDIUM |

#### 12.8.5 Quick Wins (Immediate Improvements)

| ID | Requirement | Priority | Effort |
|----|-------------|----------|--------|
| NFR-UX-QW1 | Change Non-Compliant badge to red background with white text | HIGH | 1 hour |
| NFR-UX-QW2 | Increase compliance badge font size from 10px to 14px | HIGH | 1 hour |
| NFR-UX-QW3 | Add tooltips to Dispatch filter pills | HIGH | 2 hours |
| NFR-UX-QW4 | Increase Dispatch search bar width to 300px minimum | MEDIUM | 1 hour |
| NFR-UX-QW5 | Add inspection type icons to job cards in Dispatch view | MEDIUM | 4 hours |

---

## 13. Implementation Phases

> **Design Decision (Per Gemini Review):**
> 1. Inspection Templates moved to Phase 2 - foundational for all inspection types
> 2. HHSRS/Awaab's Law moved to Phase 4 - regulatory urgency
> 3. **Data Import moved to Phase 1** - cannot test system without real data; clients cannot onboard until import works

### Phase 1: Core Compliance, Property States & Data Import (Priority: CRITICAL)

**Objective:** Enable basic compliance tracking, property lifecycle management, AND data import for testing/onboarding

| Task | Description | Effort |
|------|-------------|--------|
| 1.1 | Add property state: Non-Compliant, Offboarded | 2 days |
| 1.2 | Add property category (Single Let/HMO/Commercial) | 2 days |
| 1.3 | Add Block/Unit hierarchy (parent_id for flats) | 2 days |
| 1.4 | Add required certification types per property | 2 days |
| 1.5 | Implement certification gap analysis | 2 days |
| 1.6 | Build Property Import Wizard (CSV/Excel) | 4 days |
| 1.7 | Build Certification Import Wizard | 3 days |
| 1.8 | Build Compliance Dashboard view | 5 days |
| 1.9 | Build "Inspections Due" list (14-30 day window) | 3 days |
| 1.10 | Implement bulk property selection + job creation | 4 days |
| **Total Phase 1** | | **29 days** |

### Phase 2: Inspection Templates & Mobile Foundation (Priority: CRITICAL)

**Objective:** Build template system FIRST - this is the foundation for all inspection types

| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Create Inspection Template model | 2 days |
| 2.2 | Create Template Section model | 1 day |
| 2.3 | Create Template Item model with all response types | 3 days |
| 2.4 | Create Inspection Response model | 2 days |
| 2.5 | Build template management UI (create/edit templates) | 4 days |
| 2.6 | Create default templates (Gas CP12, EICR, Fire, Quick Visit) | 3 days |
| 2.7 | Mobile app: Template-driven inspection flow | 5 days |
| 2.8 | Mobile app: Photo capture with GPS + compression + watermarking | 3 days |
| 2.9 | Mobile app: Offline-first with sync queue | 3 days |
| 2.10 | Mobile app: Skip logic / conditional branching | 2 days |
| 2.11 | Guest Upload Link for external contractors (magic link portal) | 2 days |
| **Total Phase 2** | | **30 days** |

> **Design Decision (Per Gemini Review - Iteration 3 - Guest Portal Priority):**
> The Guest Upload Link is a critical path feature. If internal inspectors find faults that external contractors fix, but the contractor can't easily upload a "Fixed" photo, the compliance dashboard will be permanently out of date (showing "Fault" when it's actually fixed). Move to Phase 2 to unblock the remediation workflow.

### Phase 3: Defects, Faults & Remediation (Priority: HIGH)

**Objective:** Unified defect tracking with native codes + severity SLA

| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Create Fault Code model (native codes + severity_sla mapping) | 3 days |
| 3.2 | Seed fault codes (GIUSP, 18th Edition, RRO, HSE L8, CAR 2012) | 2 days |
| 3.3 | Create unified Defect model (regulatory_fault / hhsrs_hazard) | 3 days |
| 3.4 | Link template responses → auto-create defects | 2 days |
| 3.5 | Implement severity_sla deadline calculation | 1 day |
| 3.6 | Create Remediation Work Order model | 2 days |
| 3.7 | Auto-create remediation from defect | 1 day |
| 3.8 | Build defect/remediation views and filters | 3 days |
| 3.9 | Implement re-check inspection creation and linking | 2 days |
| 3.10 | Re-check pass → close defect, Re-check fail → escalate/offboard | 2 days |
| 3.11 | Cost approval workflow (threshold-based) | 2 days |
| 3.12 | Invoice blocking on failed re-check | 1 day |
| 3.13 | Mobile app: defect recording with native codes | 3 days |
| **Total Phase 3** | | **26 days** |

### Phase 4: HHSRS, DHS & Awaab's Law Compliance (Priority: HIGH)

**Objective:** Full UK housing standards compliance with statutory timelines

| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Create HHSRS Hazard Type reference data (29 hazards) | 1 day |
| 4.2 | Extend Defect model for HHSRS (band A-J, category 1/2) | 2 days |
| 4.3 | Create Damp & Mould tracking fields | 2 days |
| 4.4 | Implement Awaab's Law deadline calculations | 3 days |
| 4.5 | Create DHS assessment template (5 criteria) | 2 days |
| 4.6 | Create Full HHSRS Assessment template (29 hazards) | 2 days |
| 4.7 | Create Damp & Mould Investigation template | 1 day |
| 4.8 | Build HHSRS hazard reporting workflow | 3 days |
| 4.9 | Build DHS compliance dashboard | 3 days |
| 4.10 | Awaab's Law notification alerts (24hr/10 day/5 day) | 3 days |
| 4.11 | Build HHSRS/DHS compliance reports | 3 days |
| **Total Phase 4** | | **25 days** |

### Phase 5: Tenant Communication & Access (Priority: MEDIUM)

**Objective:** Access booking, confirmation, and proof of service tracking

| Task | Description | Effort |
|------|-------------|--------|
| 5.1 | Create Access Attempt model (replaces no_access_count) | 2 days |
| 5.2 | Implement appointment notification | 2 days |
| 5.3 | Build confirmation tracking (Pending/Confirmed/Declined/No Response) | 2 days |
| 5.4 | Implement no-response reminders | 2 days |
| 5.5 | No-access handling workflow with 3-strike escalation | 2 days |
| 5.6 | Generate PDF "Access Refusal Log" for legal defence | 2 days |
| 5.7 | Proof of Service tracking (cert delivery to tenant) | 3 days |
| 5.8 | Handle Owner-Occupier vs Tenant notification logic | 1 day |
| **Total Phase 5** | | **16 days** |

### Phase 6: Automation & Monitoring (Priority: MEDIUM)

**Objective:** Automated alerts, escalation, and deadline monitoring

| Task | Description | Effort |
|------|-------------|--------|
| 6.1 | Implement expiry alert cron job | 2 days |
| 6.2 | Implement defect deadline monitoring cron | 2 days |
| 6.3 | Implement escalation workflow (manager, senior manager) | 3 days |
| 6.4 | Build notification templates (email) | 2 days |
| 6.5 | SMS gateway integration | 3 days |
| 6.6 | Auto-create renewal inspections | 2 days |
| 6.7 | Landlord remediation notification workflow | 2 days |
| **Total Phase 6** | | **16 days** |

### Phase 7: Reporting & Polish (Priority: LOW)

**Objective:** Comprehensive reporting and UX refinements (Import moved to Phase 1)

| Task | Description | Effort |
|------|-------------|--------|
| 7.1 | Build compliance reports (portfolio, property, certification) | 5 days |
| 7.2 | Build operational reports (inspector, SLA, route) | 3 days |
| 7.3 | Build audit reports (compliance log, access log) | 3 days |
| 7.4 | Build Liability Defence Pack generator | 3 days |
| 7.5 | Property setup wizard | 2 days |
| 7.6 | UX refinements based on testing | 5 days |
| **Total Phase 7** | | **21 days** |

### Implementation Timeline Summary

| Phase | Description | Duration | Dependencies |
|-------|-------------|----------|--------------|
| Phase 1 | Core Compliance, Property States & **Data Import** | 29 days | None |
| Phase 2 | **Inspection Templates, Mobile & Guest Portal** | 30 days | Phase 1 |
| Phase 3 | Defects, Faults & Remediation | 26 days | Phase 2 |
| Phase 4 | HHSRS, DHS & Awaab's Law | 25 days | Phase 3 |
| Phase 5 | Tenant Communication & Access | 16 days | Phase 1 |
| Phase 6 | Automation & Monitoring | 16 days | Phase 3, 4 |
| Phase 7 | Reporting & Polish | 21 days | Phase 5, 6 |
| **TOTAL** | | **~163 days** | |

> **Key Changes from Original Roadmap:**
> 1. Templates moved from Phase 7 → Phase 2 (foundational)
> 2. HHSRS/Awaab's Law moved from Phase 8 → Phase 4 (regulatory urgency)
> 3. **Data Import moved to Phase 1** (cannot test without data; client onboarding blocker)
> 4. Unified Defect model eliminates duplicate Fault + Hazard tracking
> 5. Access Attempt model replaces simple no_access_count integer
> 6. Added Proof of Service, Guest Upload, Cost Approval, Landlord Refusal workflows
> 7. Added Block/Unit hierarchy for Fire Safety Act compliance
> 8. Added Key Management, Lone Worker Safety, Contractor Accreditation
> 9. **Guest Upload Link moved to Phase 2** (critical path for remediation workflow)
> 10. Added UPRN field, Deposit Protection, Invoice Blocking, Photo Watermarking, Notification Digest

---

## 14. Appendices

### Appendix A: Fault Code Reference

#### A.1 Gas Safety (CP12) - GIUSP Categories

| Code | Category | Description | Remediation |
|------|----------|-------------|-------------|
| ID | Cat 1 | Immediately Dangerous | 24 hours - gas supply must be capped/isolated immediately |
| AR | Cat 2 | At Risk | 28 days - poses risk if continued use |
| NCS | N/A | Not to Current Standard | Advisory - inform customer, no remediation required |

#### A.2 Electrical (EICR) - 18th Edition Categories

| Code | Category | Description | Remediation |
|------|----------|-------------|-------------|
| C1 | Cat 1 | Danger Present | 24 hours - requires urgent attention |
| C2 | Cat 2 | Potentially Dangerous | 28 days - urgent remedial action required |
| C3 | N/A | Improvement Recommended | Advisory - no action required |
| FI | N/A | Further Investigation | Needs further investigation before classification |

#### A.3 Fire Safety Categories

| Code | Category | Description | Remediation |
|------|----------|-------------|-------------|
| FSH | Cat 1 | Fire Safety Hazard - Immediate | 24 hours |
| FSR | Cat 2 | Fire Safety Risk - Significant | 28 days |
| FSI | N/A | Fire Safety Improvement | Advisory |

#### A.4 Legionella Categories

| Code | Category | Description | Remediation |
|------|----------|-------------|-------------|
| LAC | Cat 1 | Active Legionella Contamination | 48 hours - water system must be isolated/treated |
| LRF | Cat 2 | Risk Factors Present | 28 days |
| LMI | N/A | Minor Improvement | Advisory |

#### A.5 Asbestos Categories

| Code | Category | Description | Remediation |
|------|----------|-------------|-------------|
| ADF | Cat 1 | Damaged/Friable ACM | 24 hours - immediate containment/removal |
| ARD | Cat 2 | ACM Requiring Removal/Treatment | 28 days |
| AIM | N/A | Intact ACM - Manage in Place | Monitor annually |

### Appendix B: UK Legal Requirements Reference

#### B.1 Certification-Specific Legislation

| Certification | Legislation | Requirement | Validity |
|---------------|-------------|-------------|----------|
| Gas Safety (CP12) | Gas Safety (Installation and Use) Regulations 1998 | Annual for rental properties | 12 months |
| EICR | Electrical Safety Standards in the Private Rented Sector (England) Regulations 2020 | Every 5 years or change of tenancy | 5 years |
| EPC | Energy Performance of Buildings Regulations 2012 | Before marketing property | 10 years |
| Fire Safety | Regulatory Reform (Fire Safety) Order 2005 | Risk assessment required | Annual review |
| Legionella | HSE ACOP L8 | Risk assessment required | 2 years |
| Asbestos | Control of Asbestos Regulations 2012 | Survey if built pre-2000 | Re-inspect if disturbed |
| Smoke Alarms | Smoke and Carbon Monoxide Alarm (England) Regulations 2015 | At least one on each storey | Check at tenancy start |
| CO Alarms | Smoke and Carbon Monoxide Alarm (Amendment) Regulations 2022 | In rooms with fixed combustion appliances | Check at tenancy start |

> **Design Decision (Per Gemini Review - Smoke vs CO Alarms):**
> The 2022 Amendment Regulations introduced stricter CO alarm requirements. Templates must explicitly separate:
> - **Smoke Alarms:** Required on each storey (2015 Regulations)
> - **CO Alarms:** Required in rooms with fixed combustion appliances - gas boilers, fires, wood burners (2022 Amendment)
> These have different statutory bases and must be tested/recorded separately.

#### B.2 Housing Standards Legislation

| Legislation | Year | Key Requirements | Applies To |
|-------------|------|------------------|------------|
| Housing Act 2004 | 2004 | Introduced HHSRS; Local authority enforcement powers | All rented housing |
| Homes (Fitness for Human Habitation) Act | 2018 | Properties must be fit for habitation throughout tenancy | All rented housing |
| Social Housing (Regulation) Act | 2023 | Enabled Awaab's Law; Strengthened RSH powers | Social housing |
| Hazards in Social Housing (Prescribed Requirements) Regulations | 2025 | Awaab's Law - statutory repair timescales | Social housing (Oct 2025) |
| Renters' Rights Bill | 2024-25 | Extends Awaab's Law to PRS; Decent Homes Standard for PRS | Private rented sector |
| Minimum Energy Efficiency Standards (MEES) | 2015/2018 | EPC E minimum (current); EPC C by 2030 | All rented housing |

#### B.3 Awaab's Law Statutory Timescales

| Hazard Type | Investigation Deadline | Safety Work Deadline | Written Summary | Supplementary Work |
|-------------|----------------------|---------------------|-----------------|-------------------|
| Emergency | 24 hours | 24 hours | 3 working days | Start within 5 working days |
| Significant | 10 working days | 5 working days after investigation | 3 working days | Start within 5 working days (max 12 weeks) |

#### B.4 Decent Homes Standard Criteria (Reformed 2025)

| Criterion | Requirement | Enforcement Date |
|-----------|-------------|------------------|
| A | Free from Category 1 HHSRS hazards | Current |
| B | Reasonable state of repair (key building components) | Current |
| C | Reasonably modern facilities (3 of 4 core facilities) | Current |
| D | Thermal comfort (MEES compliance, programmable heating) | Current |
| E (NEW) | Free from damp and mould | 2025 |

**Note:** DHS extends to Private Rented Sector from 2035-2037 via Renters' Rights Bill.

### Appendix C: Glossary

| Term | Definition |
|------|------------|
| FLAGE+ | Fire, Legionella, Asbestos, Gas, Electrical + EPC/PAT |
| CP12 | Gas Safety Certificate (Commercial Pipeline 12) |
| EICR | Electrical Installation Condition Report |
| EPC | Energy Performance Certificate |
| PAT | Portable Appliance Testing |
| HMO | House in Multiple Occupation |
| Cat 1 | Category 1 Fault - Critical, requires 24-48hr remediation |
| Cat 2 | Category 2 Fault - Serious, requires 14-28 day remediation |
| GIUSP | Gas Industry Unsafe Situations Procedure |
| ACM | Asbestos Containing Material |
| Re-check | Follow-up inspection after remediation to verify fault resolved |
| Offboarding | Removal of property from active management due to compliance failure |

### Appendix D: User Stories

#### D.1 Property Manager Stories

- **PM-1:** As a Property Manager, I want to see a dashboard of compliance status so I can identify properties needing attention
- **PM-2:** As a Property Manager, I want to receive alerts before certifications expire so I can schedule renewals in time
- **PM-3:** As a Property Manager, I want to view all faults by category so I can prioritize Cat 1 issues
- **PM-4:** As a Property Manager, I want to generate compliance reports for landlords so they can see their portfolio status

#### D.2 Dispatcher Stories

- **DS-1:** As a Dispatcher, I want to bulk-select properties with expiring certifications so I can create multiple jobs efficiently
- **DS-2:** As a Dispatcher, I want to optimize routes for inspectors so they can complete more jobs per day
- **DS-3:** As a Dispatcher, I want to track tenant access confirmations so I can reschedule declined appointments
- **DS-4:** As a Dispatcher, I want to be alerted to unscheduled Cat 1 remediation so I can take immediate action

#### D.3 Inspector Stories

- **IN-1:** As an Inspector, I want to see my daily route on a map so I can navigate efficiently
- **IN-2:** As an Inspector, I want to record inspection results on my mobile so I don't need paperwork
- **IN-3:** As an Inspector, I want to record faults with photos so I have evidence for compliance
- **IN-4:** As an Inspector, I want to work offline so I can complete inspections in areas with poor connectivity

#### D.4 Property Owner Stories

- **PO-1:** As a Property Owner, I want to receive certificates by email so I have records
- **PO-2:** As a Property Owner, I want to be notified of faults so I can arrange remediation
- **PO-3:** As a Property Owner, I want to request schedule changes so I can coordinate with tenants

---

**Document Revision History**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | Product Team | Initial requirements |
| 2.0 | Dec 13, 2025 | Product Team | Added fault tracking, remediation workflow, offboarding, complete lifecycle |

---

## 15. UK Decent Homes Standard & HHSRS Compliance

### 15.1 Decent Homes Standard (DHS) Overview

The Decent Homes Standard is being reformed and extended to the Private Rented Sector via the Renters' Rights Bill (expected enforcement from 2035-2037). Property Fielder must support compliance with all five criteria.

#### 15.1.1 DHS Criteria

| Criterion | Description | Requirements |
|-----------|-------------|--------------|
| **A** | Free from serious hazards | No Category 1 HHSRS hazards present |
| **B** | Reasonable state of repair | Key building components not in disrepair |
| **C** | Reasonably modern facilities | At least 3 of 4 core facilities; window restrictors where fall hazard |
| **D** | Thermal comfort | Meets MEES (EPC C by 2030); programmable heating |
| **E** (NEW) | Free from damp and mould | No significant damp/mould hazards |

### 15.2 HHSRS - Housing Health & Safety Rating System

The HHSRS assesses 29 categories of housing hazard. Property Fielder must track and manage all relevant hazards.

#### 15.2.1 The 29 HHSRS Hazards

**Physiological Requirements (Hazards 1-10):**

| # | Hazard | Health Effects |
|---|--------|---------------|
| 1 | Damp and mould growth | Allergies, asthma, toxins from mould, fungal infections |
| 2 | Excess cold | Respiratory conditions, cardiovascular conditions |
| 3 | Excess heat | Dehydration, trauma, stroke |
| 4 | Asbestos and MMF | Lung damage |
| 5 | Biocides | Breathing, skin contact, swallowing of chemicals |
| 6 | Carbon monoxide and fuel combustion | Dizziness, nausea, unconsciousness |
| 7 | Lead | Nervous disorders, mental health, blood issues |
| 8 | Radiation (Radon) | Lung cancer |
| 9 | Uncombusted fuel gas | Suffocation |
| 10 | Volatile organic compounds | Allergies, headaches, nausea |

**Psychological Requirements (Hazards 11-14):**

| # | Hazard | Health Effects |
|---|--------|---------------|
| 11 | Crowding and space | Psychological distress, hygiene issues |
| 12 | Entry by intruders | Fear, stress, injuries from intruders |
| 13 | Lighting | Depression, eye strain |
| 14 | Noise | Sleep deprivation, headaches, anxiety |

**Protection Against Infection (Hazards 15-18):**

| # | Hazard | Health Effects |
|---|--------|---------------|
| 15 | Domestic hygiene, pests and refuse | Stomach disease, infection, asthma |
| 16 | Food safety | Stomach disease, diarrhoea, vomiting |
| 17 | Personal hygiene, sanitation and drainage | Stomach disease, skin infections |
| 18 | Water supply | Dehydration, legionnaires disease |

**Protection Against Accidents (Hazards 19-29):**

| # | Hazard | Health Effects |
|---|--------|---------------|
| 19 | Falls associated with baths | Physical injuries |
| 20 | Falls on level surfaces | Bruising, fractures, head injuries |
| 21 | Falls associated with stairs and steps | Bruising, fractures, spinal injuries |
| 22 | Falls between levels | Physical injuries, death |
| 23 | Electrical hazards | Electric shock and burns |
| 24 | Fire | Burns, smoke inhalation, death |
| 25 | Flames, hot surfaces and materials | Burns, scalds, scarring |
| 26 | Collision and entrapment | Cuts, bruising |
| 27 | Explosions | Physical injuries, crushing |
| 28 | Ergonomics | Strain and sprain injuries |
| 29 | Structural collapse and falling elements | Physical injuries, death |

#### 15.2.2 HHSRS Categories

| Category | Band | Description | Action Required |
|----------|------|-------------|-----------------|
| **Category 1** | A, B, C | Most dangerous - significant risk of harm within 12 months | Mandatory enforcement action |
| **Category 2** | D to J | Less serious - lower risk | Discretionary enforcement |

### 15.3 Awaab's Law Requirements

Awaab's Law (in force from October 2025 for social housing, extending to PRS) sets statutory timescales for landlords to respond to hazards.

#### 15.3.1 Awaab's Law Timescales

| Hazard Type | Investigation | Safety Work | Supplementary Work |
|-------------|---------------|-------------|-------------------|
| **Emergency Hazard** | Within 24 hours | Within 24 hours | Start within 5 working days |
| **Significant Hazard** | Within 10 working days | Within 5 working days of investigation | Start within 5 working days, complete within 12 weeks |

#### 15.3.2 Awaab's Law Phased Implementation

| Phase | Effective Date | Hazards Covered |
|-------|----------------|-----------------|
| Phase 1 | October 2025 | All emergency hazards + Damp & Mould |
| Phase 2 | 2026 | Excess cold/heat, Falls, Structural collapse, Fire, Electrical, Hygiene |
| Phase 3 | 2027 | All remaining HHSRS hazards (except overcrowding) |

#### 15.3.3 Emergency Hazard Examples

- Gas or carbon monoxide leaks
- Broken boilers (especially in cold weather)
- Total loss of water supply
- Exposed electrical wiring
- Significant water leaks
- Broken external doors/windows (security risk)
- Prevalent damp/mould affecting tenant health
- Significant structural defects

#### 15.3.4 Awaab's Law Process Requirements

| Step | Requirement | Timeframe |
|------|-------------|-----------|
| 1 | Become aware of potential hazard | Day 0 |
| 2 | Triage and categorise (emergency/significant/out-of-scope) | Immediate |
| 3a | Emergency: Investigate and complete safety work | Within 24 hours |
| 3b | Significant: Investigate | Within 10 working days |
| 4 | Provide written summary to tenant | Within 3 working days of investigation |
| 5 | Complete relevant safety work | Within 5 working days of investigation |
| 6 | Begin supplementary preventative work | Within 5 working days (or 12 weeks if delay) |
| 7 | If property cannot be made safe | Provide alternative accommodation at landlord's expense |
| 8 | Keep tenant updated throughout | Ongoing |

### 15.4 Updated Functional Requirements for DHS/HHSRS/Awaab's Law

#### FR-15.1 HHSRS Hazard Tracking

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-15.1.1 | System SHALL support all 29 HHSRS hazard categories | HIGH |
| FR-15.1.2 | System SHALL classify hazards as Category 1 or Category 2 | HIGH |
| FR-15.1.3 | System SHALL support hazard severity scoring (Bands A-J) | MEDIUM |
| FR-15.1.4 | System SHALL link hazards to property and inspection records | HIGH |
| FR-15.1.5 | System SHALL track hazard status: Open, Under Investigation, Remediated, Closed | HIGH |

#### FR-15.2 Awaab's Law Compliance

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-15.2.1 | System SHALL classify hazards as Emergency, Significant, or Out-of-Scope | HIGH |
| FR-15.2.2 | System SHALL auto-calculate investigation deadline (24hr or 10 working days) | HIGH |
| FR-15.2.3 | System SHALL auto-calculate safety work deadline (24hr or 5 working days) | HIGH |
| FR-15.2.4 | System SHALL track when landlord "became aware" of hazard (Day 0) | HIGH |
| FR-15.2.5 | System SHALL generate written investigation summary for tenant | HIGH |
| FR-15.2.6 | System SHALL track written summary delivery (within 3 working days) | HIGH |
| FR-15.2.7 | System SHALL escalate missed deadlines with URGENT alerts | HIGH |
| FR-15.2.8 | System SHALL track alternative accommodation provision if required | MEDIUM |
| FR-15.2.9 | System SHALL maintain full audit trail of all actions for legal defence | HIGH |

#### FR-15.3 Damp & Mould Specific (Criterion E)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-15.3.1 | System SHALL specifically track damp and mould hazards | HIGH |
| FR-15.3.2 | System SHALL record mould severity: Minor, Moderate, Severe, Pervasive | HIGH |
| FR-15.3.3 | System SHALL record mould location: Bedroom, Living Room, Kitchen, Bathroom | HIGH |
| FR-15.3.4 | System SHALL track tenant health impact reported | HIGH |
| FR-15.3.5 | System SHALL track vulnerable occupants (children, elderly, respiratory conditions) | HIGH |
| FR-15.3.6 | System SHALL NOT allow "lifestyle" blame without investigation | HIGH |

#### FR-15.4 Decent Homes Standard Assessment

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-15.4.1 | System SHALL assess property against all 5 DHS criteria | MEDIUM |
| FR-15.4.2 | System SHALL track Criterion A: No Category 1 HHSRS hazards | HIGH |
| FR-15.4.3 | System SHALL track Criterion B: Building components condition | MEDIUM |
| FR-15.4.4 | System SHALL track Criterion C: Modern facilities | MEDIUM |
| FR-15.4.5 | System SHALL track Criterion D: EPC rating and heating | MEDIUM |
| FR-15.4.6 | System SHALL track Criterion E: Damp and mould free | HIGH |
| FR-15.4.7 | System SHALL report properties failing DHS criteria | HIGH |
| FR-15.4.8 | System SHALL track window restrictors where fall hazard exists | MEDIUM |

#### FR-15.5 Building Components Tracking (Criterion B)

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-15.5.1 | System SHALL track condition of key building components | MEDIUM |
| FR-15.5.2 | Key components: External walls, Roof, Windows/doors, Chimneys, Central heating, Gas fires, Storage heaters, Plumbing, Electrics | MEDIUM |
| FR-15.5.3 | Other components: Kitchens, Bathrooms, External elements, Common areas | MEDIUM |
| FR-15.5.4 | System SHALL record component condition: Good, Fair, Poor, Failed | MEDIUM |
| FR-15.5.5 | System SHALL flag when key component in poor condition | MEDIUM |

### 15.5 Inspection Templates System

#### 15.5.1 Template-Based Inspection Approach

HHSRS is a risk-based assessment system, NOT a checklist. Different inspection types require different levels of hazard assessment:

| Template Type | Hazards Checked | Performed By | Duration | Use Case |
|---------------|----------------|--------------|----------|----------|
| Quick Property Visit | 8-10 key indicators | Housing Officer | 15-20 mins | Routine visits, tenant contact |
| Damp & Mould Investigation | 5-8 related hazards | Surveyor | 30-45 mins | Damp/mould complaint under Awaab's Law |
| Full HHSRS Assessment | All 29 hazards | HHSRS Trained Assessor | 1-2 hours | New tenancy, periodic, enforcement |
| Pre-Tenancy Check | 15-20 key hazards | Inspector | 45-60 mins | Before new tenant moves in |
| Decent Homes Assessment | All 5 DHS criteria | Surveyor | 60-90 mins | DHS compliance verification |
| Gas Safety (CP12) | Gas-specific + hazards 6, 9 | Gas Safe Engineer | 30-45 mins | Annual gas safety |
| EICR | Electrical-specific + hazard 23 | Electrician | 2-4 hours | Electrical safety |
| Fire Risk Assessment | Fire-specific + hazards 24, 27 | Fire Assessor | 1-2 hours | Fire safety compliance |

#### 15.5.2 Hazard Groupings for Practical Inspection

| Group | Hazard #s | Quick Check Questions |
|-------|-----------|----------------------|
| **Damp & Temperature** | 1, 2, 3 | Visible damp/mould? Heating working? Ventilation adequate? |
| **Toxic Substances** | 4, 5, 6, 7, 8, 9, 10 | Gas/CO alarms? Asbestos survey current? Lead paint? |
| **Security & Space** | 11, 12, 13, 14 | Secure doors/windows? Adequate lighting? Noise issues? |
| **Hygiene** | 15, 16, 17, 18 | Kitchen/bathroom functional? Pest evidence? Water OK? |
| **Falls** | 19, 20, 21, 22 | Stairs safe? Floors OK? Window restrictors? Balcony secure? |
| **Fire & Electrical** | 23, 24, 25 | Smoke alarms? Electrics safe? Hot surfaces guarded? |
| **Structure** | 26, 27, 28, 29 | Doors/windows safe? Structural cracks? Ergonomic issues? |

#### 15.5.3 Functional Requirements - Inspection Templates

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-15.5.1 | System SHALL support configurable inspection templates | HIGH |
| FR-15.5.2 | Templates SHALL contain sections with ordered inspection items | HIGH |
| FR-15.5.3 | Inspection items SHALL link to HHSRS hazard types (1-29) where applicable | HIGH |
| FR-15.5.4 | Items SHALL support response types: yes/no, severity scale, numeric, text, photo | HIGH |
| FR-15.5.5 | Items SHALL support conditional follow-up questions | MEDIUM |
| FR-15.5.6 | Items SHALL define conditions that auto-create hazard records | HIGH |
| FR-15.5.7 | Templates SHALL specify mandatory vs optional items | HIGH |
| FR-15.5.8 | Templates SHALL specify photo requirements per item/condition | HIGH |
| FR-15.5.9 | Templates SHALL include guidance notes for inspectors | MEDIUM |
| FR-15.5.10 | Templates SHALL specify required inspector qualifications | MEDIUM |
| FR-15.5.11 | System SHALL support template versioning | MEDIUM |
| FR-15.5.12 | System SHALL sync templates to mobile app for offline use | HIGH |

#### 15.5.4 Mobile App - Template-Driven Inspection Flow

```text
START: Inspector opens assigned job
  │
  ▼
[App loads appropriate template based on inspection type]
  │
  ▼
[Inspector sees sections in order:]
  │
  ├── Section 1: Property Details (auto-filled from job)
  ├── Section 2: Tenant Interview (if applicable)
  ├── Section 3: External Inspection
  ├── Section 4: Room-by-Room (or hazard-by-hazard)
  └── Section N: Summary & Sign-off
  │
  ▼
[For each item in section:]
  │
  ├── Display question + guidance
  ├── Capture response (per response_type)
  ├── If severity threshold met → prompt for photo
  ├── If triggers_hazard → auto-create hazard record
  └── Show follow-up questions if conditional
  │
  ▼
[Section complete → move to next]
  │
  ▼
[All sections complete:]
  │
  ├── Generate inspection summary
  ├── List all hazards identified
  ├── Calculate pass/fail/conditional result
  ├── Capture inspector signature
  └── Capture tenant signature (if present)
  │
  ▼
[Sync to backend when online]
  │
  ▼
END: Job marked complete, hazards created, alerts triggered
```

#### 15.5.5 Example Template: Quick Property Visit

```text
TEMPLATE: Quick Property Visit
DURATION: 15-20 minutes
QUALIFICATIONS: Housing Officer

SECTION 1: Tenant Contact
├── Is tenant present? (yes/no)
├── Any issues tenant wants to report? (text)
└── Tenant contact details confirmed? (yes/no)

SECTION 2: Damp & Temperature (Hazards 1, 2, 3)
├── Is there visible damp or mould? (severity: none/minor/moderate/severe)
│   └── [If moderate+] Photo required, location? (text)
│   └── [If any] Which rooms affected? (multi-select)
├── Is heating system operational? (yes/no/not_tested)
│   └── [If no] Create emergency hazard (Hazard 2)
└── Is ventilation adequate? (yes/no/unknown)

SECTION 3: Security (Hazard 12)
├── Are external doors secure? (yes/no)
│   └── [If no] Create hazard, photo required
├── Are windows secure and lockable? (yes/no)
└── Is there evidence of break-in attempt? (yes/no)

SECTION 4: Falls (Hazards 19-22)
├── Are stairs in safe condition? (yes/no/na)
├── Are floor surfaces in good condition? (yes/no)
└── [If upper floor] Are window restrictors fitted where needed? (yes/no/na)

SECTION 5: Fire Safety (Hazard 24)
├── Are smoke alarms present on each floor? (yes/no)
├── Are smoke alarms working? (tested/not_tested/failed)
│   └── [If failed] Create hazard, arrange replacement
├── Are carbon monoxide alarms present in rooms with combustion appliances? (yes/no/na)
│   └── [Required per Smoke and Carbon Monoxide Alarm (Amendment) Regulations 2022]
├── Are CO alarms working? (tested/not_tested/failed/na)
│   └── [If failed] Create hazard, arrange replacement
└── Is escape route clear? (yes/no)

SECTION 6: General Condition
├── Any obvious disrepair? (yes/no)
│   └── [If yes] Description and photo required
├── Any pest evidence? (yes/no)
└── Overall property condition? (good/fair/poor)

SECTION 7: Summary
├── Auto-generated list of hazards identified
├── Recommended follow-up actions
├── Inspector notes (text)
└── Signatures
```

#### 15.5.6 Example Template: Full HHSRS Assessment

```text
TEMPLATE: Full HHSRS Assessment
DURATION: 1-2 hours
QUALIFICATIONS: HHSRS Level 2 Certificate

SECTION 1: Property Information
├── Property type, age, construction
├── Number of occupants, ages, vulnerabilities
└── Previous hazard history

SECTION 2-8: All 29 Hazards (grouped as per 15.5.2)
For EACH hazard:
├── Is this hazard present? (yes/no/na)
├── [If yes] Severity assessment:
│   ├── Likelihood of occurrence (1-4 scale)
│   ├── Likely health outcome (Class I-IV)
│   └── Spread of outcomes (percentage across classes)
├── Calculated score → Band (A-J)
├── Category determination (1 or 2)
├── Photo evidence (mandatory if Category 1)
├── Location in property
├── Recommended remedial action
└── Timescale for action

SECTION 9: Summary
├── Total hazards identified by category
├── Highest band hazard
├── Overall HHSRS compliance status
├── Recommended actions with priorities
├── Inspector certification and signature
└── Date of next assessment
```

### 15.6 New Data Models for Inspection Templates

#### 15.6.1 Inspection Template (`property_fielder.inspection.template`)

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Template name (e.g., "Full HHSRS Assessment") |
| code | Char | Unique code (e.g., "HHSRS_FULL") |
| description | Text | Template description and purpose |
| certification_type_id | Many2one | Link to certification type if applicable |
| estimated_duration | Float | Estimated time in minutes |
| required_qualifications | Char | Required inspector qualifications |
| is_hhsrs_assessment | Boolean | Is this an HHSRS assessment template? |
| hazard_coverage | Selection | all_29 / grouped / targeted / basic |
| version | Integer | Template version number |
| active | Boolean | Is template currently active? |
| section_ids | One2many | Template sections |

#### 15.6.2 Template Section (`property_fielder.inspection.template.section`)

| Field | Type | Description |
|-------|------|-------------|
| template_id | Many2one | Parent template |
| name | Char | Section name (e.g., "Damp & Temperature") |
| sequence | Integer | Display order |
| hazard_group | Selection | Which hazard group this covers |
| description | Text | Section instructions |
| item_ids | One2many | Section items |

#### 15.6.3 Template Item (`property_fielder.inspection.template.item`)

| Field | Type | Description |
|-------|------|-------------|
| section_id | Many2one | Parent section |
| sequence | Integer | Display order within section |
| question | Char | Question text |
| help_text | Text | Guidance notes for inspector |
| hhsrs_hazard_id | Many2one | Link to HHSRS hazard type (1-29) |
| response_type | Selection | yes_no / severity / numeric / text / photo / multi_select |
| severity_options | Char | JSON array of severity options |
| select_options | Char | JSON array of select options |
| is_mandatory | Boolean | Must be answered? |
| photo_required | Boolean | Always require photo? |
| photo_required_condition | Char | Condition for photo (e.g., "severity >= moderate") |
| creates_hazard_condition | Char | Condition to auto-create hazard |
| hazard_category_if_triggered | Selection | cat1 / cat2 |
| awaab_category_if_triggered | Selection | emergency / significant |
| follow_up_item_ids | One2many | Conditional follow-up questions |
| parent_item_id | Many2one | Parent item if this is a follow-up |
| show_if_condition | Char | Condition to show this follow-up |

#### 15.6.4 Inspection Response (`property_fielder.inspection.response`)

| Field | Type | Description |
|-------|------|-------------|
| inspection_id | Many2one | Parent inspection |
| template_item_id | Many2one | Template item being answered |
| response_yes_no | Boolean | Yes/No response |
| response_severity | Selection | Severity selection |
| response_numeric | Float | Numeric response |
| response_text | Text | Text response |
| response_select | Char | Selected option(s) |
| photo_ids | Many2many | Photo attachments |
| hazard_created_id | Many2one | Hazard record created from this response |
| answered_at | Datetime | When answered |
| location_lat | Float | GPS latitude when answered |
| location_lng | Float | GPS longitude when answered |

### 15.7 New Data Models for DHS/HHSRS Compliance

#### 15.5.1 HHSRS Hazard (`property_fielder.hhsrs.hazard`)

| Field | Type | Description |
|-------|------|-------------|
| name | Char | Hazard reference number |
| property_id | Many2one | Property |
| hazard_type_id | Many2one | HHSRS hazard type (1-29) |
| category | Selection | cat1 / cat2 |
| band | Selection | A-J |
| awaab_category | Selection | emergency / significant / out_of_scope |
| description | Text | Detailed description |
| location | Char | Location in property |
| reported_date | Datetime | When reported/discovered |
| awareness_date | Datetime | When landlord "became aware" (Day 0) |
| investigation_deadline | Datetime | Calculated deadline |
| safety_work_deadline | Datetime | Calculated deadline |
| tenant_vulnerable | Boolean | Vulnerable occupants present |
| vulnerability_details | Text | Details of vulnerabilities |
| tenant_health_impact | Text | Reported health impacts |
| state | Selection | reported / investigating / awaiting_work / in_progress / resolved / closed |
| investigation_completed_date | Datetime | When investigation finished |
| investigation_summary | Text | Written summary for tenant |
| summary_sent_date | Datetime | When summary sent to tenant |
| safety_work_completed_date | Datetime | When safety work finished |
| supplementary_work_started_date | Datetime | When supplementary work started |
| supplementary_work_completed_date | Datetime | When fully resolved |
| alternative_accommodation_provided | Boolean | Was temp accommodation needed? |
| alternative_accommodation_details | Text | Details of accommodation |
| photo_ids | Many2many | Evidence photos |
| audit_log | Text | Full audit trail |

#### 15.5.2 Damp & Mould Record (`property_fielder.damp.mould`)

| Field | Type | Description |
|-------|------|-------------|
| property_id | Many2one | Property |
| hazard_id | Many2one | Link to HHSRS hazard |
| severity | Selection | minor / moderate / severe / pervasive |
| location_ids | Many2many | Rooms affected |
| cause | Selection | condensation / penetrating_damp / rising_damp / structural / unknown |
| root_cause_identified | Boolean | Has root cause been found? |
| root_cause_description | Text | Description of root cause |
| mould_wash_completed | Boolean | Surface treatment done? |
| ventilation_installed | Boolean | Mechanical ventilation installed? |
| insulation_improved | Boolean | Insulation improved? |
| recurring | Boolean | Has this issue recurred? |
| previous_reports_count | Integer | Number of previous reports |
| photo_ids | Many2many | Evidence photos |

#### 15.5.3 Building Component (`property_fielder.building.component`)

| Field | Type | Description |
|-------|------|-------------|
| property_id | Many2one | Property |
| component_type | Selection | See key/other components list |
| is_key_component | Boolean | Is this a key component for DHS? |
| condition | Selection | good / fair / poor / failed |
| last_inspected | Date | Last inspection date |
| age_years | Integer | Age of component |
| notes | Text | Condition notes |
| replacement_due | Boolean | Due for replacement? |
| replacement_date | Date | Estimated replacement date |

### 15.6 Updated Workflows

#### 15.6.1 HHSRS Hazard Reporting Workflow

```text
START: Hazard reported or discovered
  │
  ▼
[System records awareness date (Day 0)]
  │
  ▼
[Dispatcher/Manager triages hazard:]
  │
  ├──(Out of Scope)──► [Log reason, close or refer elsewhere]
  │
  ├──(Emergency)──► [24-hour track]
  │     │
  │     ▼
  │  [Investigation MUST complete within 24 hours]
  │     │
  │     ▼
  │  [Safety work MUST complete within 24 hours]
  │     │
  │     ├──(Cannot make safe)──► [Provide alternative accommodation]
  │     │
  │     ▼
  │  [Supplementary work starts within 5 working days]
  │     │
  │     ▼
  │  [Complete within reasonable time]
  │
  ├──(Significant)──► [10-day track]
        │
        ▼
     [Investigation MUST complete within 10 working days]
        │
        ▼
     [Send written summary to tenant within 3 working days]
        │
        ▼
     [Safety work MUST complete within 5 working days of investigation]
        │
        ├──(Cannot make safe)──► [Provide alternative accommodation]
        │
        ▼
     [Supplementary work starts within 5 working days]
        │
        ├──(Cannot start in 5 days)──► [Must start within 12 weeks]
        │
        ▼
     [Complete within reasonable time]
        │
        ▼
END: Hazard resolved, full audit trail retained
```

### 15.7 Reporting Requirements for DHS/HHSRS

| Report | Description | Frequency | Priority |
|--------|-------------|-----------|----------|
| **DHS Compliance Summary** | % of properties meeting all 5 DHS criteria | Monthly | HIGH |
| **DHS Failures by Criterion** | Properties failing each criterion | Monthly | HIGH |
| **HHSRS Hazard Register** | All open hazards by category and band | Weekly | HIGH |
| **Awaab's Law Compliance** | Investigations/work completed within deadline | Weekly | HIGH |
| **Awaab's Law Breaches** | Missed deadlines requiring urgent action | Daily | CRITICAL |
| **Damp & Mould Dashboard** | All damp/mould cases and status | Weekly | HIGH |
| **Emergency Hazard Log** | All emergency hazards and response times | Weekly | HIGH |
| **Alternative Accommodation Log** | Properties requiring temp accommodation | Weekly | MEDIUM |

### 15.10 Implementation Phases (Additional)

#### Phase 7: Inspection Templates (Priority: HIGH)

| Task | Description | Effort |
|------|-------------|--------|
| 7.1 | Create Inspection Template model | 2 days |
| 7.2 | Create Template Section model | 1 day |
| 7.3 | Create Template Item model with all response types | 3 days |
| 7.4 | Create Inspection Response model | 2 days |
| 7.5 | Build template management UI (create/edit templates) | 3 days |
| 7.6 | Create default templates (Quick Visit, Full HHSRS, Damp Investigation) | 2 days |
| 7.7 | Mobile app: Template-driven inspection flow | 5 days |
| 7.8 | Mobile app: Offline template sync | 2 days |
| 7.9 | Mobile app: Photo capture per item | 2 days |
| 7.10 | Mobile app: Conditional questions logic | 2 days |
| 7.11 | Auto-create hazard from inspection response | 2 days |
| 7.12 | Inspection completion → result calculation | 2 days |
| **Total Phase 7** | | **28 days** |

#### Phase 8: DHS & HHSRS Compliance (Priority: HIGH)

| Task | Description | Effort |
|------|-------------|--------|
| 8.1 | Create HHSRS Hazard Type reference data (29 hazards) | 1 day |
| 8.2 | Create HHSRS Hazard model | 3 days |
| 8.3 | Create Damp & Mould tracking model | 2 days |
| 8.4 | Create Building Component model | 2 days |
| 8.5 | Implement Awaab's Law deadline calculations | 2 days |
| 8.6 | Build HHSRS hazard reporting workflow | 3 days |
| 8.7 | Create DHS assessment views | 3 days |
| 8.8 | Build tenant notification templates (investigation summary) | 2 days |
| 8.9 | Implement deadline monitoring cron jobs | 2 days |
| 8.10 | Build HHSRS/DHS compliance reports | 3 days |
| 8.11 | Mobile app: Hazard reporting screen | 3 days |
| **Total Phase 8** | | **26 days** |

#### Updated Total Implementation Effort

| Phase | Description | Effort |
|-------|-------------|--------|
| Phase 1 | Core Compliance Dashboard | 15 days |
| Phase 2 | Fault & Remediation Workflow | 18 days |
| Phase 3 | Field Service Enhancements | 12 days |
| Phase 4 | Mobile App Core | 20 days |
| Phase 5 | Automation & Integrations | 15 days |
| Phase 6 | Reporting & Analytics | 10 days |
| Phase 7 | Inspection Templates | 28 days |
| Phase 8 | DHS & HHSRS Compliance | 26 days |
| **TOTAL** | | **~144 days** |

---

## 16. Glossary Additions

| Term | Definition |
|------|------------|
| DHS | Decent Homes Standard - UK minimum quality standard for rented housing |
| HHSRS | Housing Health and Safety Rating System - 29-hazard assessment system |
| Awaab's Law | Legislation setting statutory repair timescales for hazards |
| Category 1 Hazard | Most serious HHSRS hazards (Bands A-C) requiring mandatory action |
| Category 2 Hazard | Less serious HHSRS hazards (Bands D-J) with discretionary action |
| Emergency Hazard | Hazard requiring investigation and safety work within 24 hours |
| Significant Hazard | Hazard requiring investigation within 10 working days |
| Day 0 | Date landlord becomes aware of potential hazard |
| Safety Work | Work to make property immediately safe |
| Supplementary Work | Additional work to prevent hazard recurring |
| MEES | Minimum Energy Efficiency Standards (EPC C by 2030) |
| Inspection Template | Configurable checklist defining what to check during an inspection |
| Template Item | Individual question/check within a template section |
| Response Type | How an item is answered: yes/no, severity, numeric, text, photo |

---

## 17. Odoo Addon Architecture

This section defines the modular addon structure for Property Fielder, enabling phased rollout, optional features, and clean separation of concerns.

### 17.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LAYER 4: OPTIONAL BUSINESS ADDONS                    │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│  │ property_fielder │ │ property_fielder │ │ property_fielder │               │
│  │ _property_      │ │ _property_      │ │ _owner_portal   │               │
│  │ _marketing      │ │ _analytics      │ │                 │               │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘               │
├─────────────────────────────────────────────────────────────────────────────┤
│                         LAYER 3: DOMAIN ADDONS                               │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│  │ property_fielder │ │ property_fielder │ │ property_fielder │               │
│  │ _hhsrs          │ │ _tenant_access  │ │ _defects        │               │
│  │ (HHSRS/DHS)     │ │ (Access/Booking)│ │ (Remediation)   │               │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘               │
├─────────────────────────────────────────────────────────────────────────────┤
│                         LAYER 2: FEATURE ADDONS                              │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐               │
│  │ property_fielder │ │ property_fielder │ │ property_fielder │               │
│  │ _templates      │ │ _import         │ │ _field_service  │               │
│  │ (Inspections)   │ │ (Data Import)   │ │ _mobile         │               │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘               │
├─────────────────────────────────────────────────────────────────────────────┤
│                         LAYER 1: CORE ADDONS                                 │
│  ┌────────────────────────────────┐ ┌────────────────────────────────┐     │
│  │ property_fielder_field_service │ │ property_fielder_property_     │     │
│  │ (Jobs, Routes, Inspectors)     │ │ _management (Properties, FLAGE+)│     │
│  └────────────────────────────────┘ └────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────────────────────┤
│                         LAYER 0: ODOO CORE                                   │
│              base, mail, web, hr, contacts, project, account                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 17.2 Current State (Built)

| Addon | Layer | Purpose | Status |
|-------|-------|---------|--------|
| `property_fielder_field_service` | 1 | Jobs, Routes, Inspectors, Dispatch, Route Optimization | ✅ Built |
| `property_fielder_field_service_mobile` | 2 | Mobile backend: Photos, Signatures, Check-in, REST API | ✅ Built |
| `property_fielder_property_management` | 1 | Properties, FLAGE+ Certifications, Inspections | ✅ Built |

### 17.3 Compliance Addon Architecture (PRD Phases 1-7)

These addons deliver the core compliance functionality defined in this PRD.

#### 17.3.1 `property_fielder_import` (Phase 1)

**Purpose:** Data import for client onboarding - cannot test or deploy without real data.

| Model | Purpose |
|-------|---------|
| `import.batch` | Import batch tracking with status |
| `import.mapping` | Column → field mapping configuration |
| `import.validation.rule` | Custom validation rules |
| `import.log` | Row-level import log with errors |

**Features:**
- CSV/Excel file upload with preview
- Column auto-detection and mapping
- Property import with address parsing
- Certificate import with date validation
- UPRN-based duplicate detection
- Dry-run mode before commit
- Legacy Document Processor (OCR for scanned PDFs)
- Error reporting with row/column reference

**Depends on:** `property_fielder_property_management`

---

#### 17.3.2 `property_fielder_templates` (Phase 2)

**Purpose:** Template-driven inspections for mobile app - foundation for all inspection types.

| Model | Purpose |
|-------|---------|
| `inspection.template` | Template definition (name, certification type, active) |
| `inspection.template.section` | Grouped sections within template |
| `inspection.template.item` | Question/check items with response types |
| `inspection.response` | Inspector's answers linked to inspection |
| `condition.trigger` | Skip logic rules (if Q1=No, skip Q2-Q5) |

**Response Types:** `yes_no`, `pass_fail`, `severity` (C1/C2/NCS), `numeric`, `text`, `photo`, `select_one`, `select_multi`, `date`, `signature`

**Features:**
- Template builder UI with drag-drop section ordering
- Skip logic configuration
- Photo requirements per item
- Auto-defect creation from "fail" responses
- Default templates: Quick Visit, Full HHSRS, Gas Safety (CP12), EICR, Fire Risk Assessment
- Template versioning (archive old, create new)
- Mobile: Template-driven inspection flow with offline support

**Depends on:** `property_fielder_property_management`, `property_fielder_field_service_mobile`

---

#### 17.3.3 `property_fielder_defects` (Phase 3)

**Purpose:** Unified defect/fault tracking with native industry codes and SLA management.

| Model | Purpose |
|-------|---------|
| `fault.code` | Reference data: GIUSP, 18th Edition, RRO, HSE L8, CAR 2012 |
| `defect` | Unified defect record with type, severity, deadline |
| `defect.remediation` | Remediation work records with contractor, cost |
| `contractor` | Contractor management with trades |
| `contractor.accreditation` | Gas Safe, NICEIC, NAPIT, etc. with expiry |
| `cost.approval` | Landlord cost approval workflow |

**Key Fields on `defect`:**
- `defect_type`: `regulatory_fault` | `hhsrs_hazard`
- `fault_code_id`: Many2one to `fault.code`
- `severity_sla`: Char (e.g., "ID", "AR", "NCS", "C1", "C2", "C3")
- `deadline_date`: Computed from severity using SLA mapping
- `assigned_contractor_id`: Many2one to `contractor`
- `state`: `reported` → `acknowledged` → `in_progress` → `fixed` → `verified` → `closed`

**Features:**
- Native fault codes with severity → deadline mapping
- Contractor assignment with accreditation check
- Cost approval workflow (landlord must approve over threshold)
- Re-check scheduling after fix
- Invoice blocking on failed re-check
- Landlord refusal tracking with tenancy termination warning
- Guest Upload Link for external contractors (magic link portal)

**Depends on:** `property_fielder_templates`, `property_fielder_property_management`

---

#### 17.3.4 `property_fielder_tenant_access` (Phase 5)

**Purpose:** Access booking, confirmation, and proof of service tracking.

| Model | Purpose |
|-------|---------|
| `access.attempt` | Each access attempt with result |
| `access.booking` | Appointment booking with confirmation status |
| `proof.of.service` | Delivery confirmation (certificate given to tenant) |
| `access.escalation` | No-access escalation workflow |

**Features:**
- Appointment notification (email/SMS)
- Confirmation tracking: `pending` → `confirmed` → `declined` → `no_response`
- 3-strike no-access escalation
- Injunction application workflow (Legal Entry)
- Proof of service (tenant signature for certificate delivery)
- Owner-Occupier vs Tenant notification logic
- How to Rent Guide delivery tracking with version

**Depends on:** `property_fielder_property_management`

---

#### 17.3.5 `property_fielder_hhsrs` ✅ Built

**Purpose:** HHSRS, DHS, and Awaab's Law compliance for UK social housing.

**Status:** ✅ Built (December 2024)

| Model | Purpose | Status |
|-------|---------|--------|
| `property_fielder.hhsrs.hazard.type` | 29 hazard categories (reference data) | ✅ Built |
| `property_fielder.hhsrs.likelihood.band` | 16 official HHSRS likelihood bands | ✅ Built |
| `property_fielder.hhsrs.assessment` | Full HHSRS assessment with scoring | ✅ Built |
| `property_fielder.awaab.deadline` | Awaab's Law deadline tracking | ✅ Built |
| `property_fielder.awaab.access.refusal` | Access refusal clock-stopping | ✅ Built |
| `property_fielder.damp.mould` | Damp & mould tracking with severity | ✅ Built |
| `property_fielder.damp.mould.timeline` | Damp & mould timeline events | ✅ Built |
| `property_fielder.dhs.assessment` | Decent Homes Standard 4-criteria | ✅ Built |
| `property_fielder.building.component` | Component condition tracking | ✅ Built |

**HHSRS Assessment Features:**
- Full scoring formula: score = 1000 × (Class I × 1.0 + Class II × 0.1 + Class III × 0.01 + Class IV × 0.001)
- Automatic band assignment (A-J) based on score
- Automatic category assignment (1 = Band A-C, 2 = Band D-J)
- Remediation job creation from assessment
- Integration with field service jobs

**Awaab's Law Deadlines:**
| Hazard Type | Investigation | Start Repairs | Complete Repairs |
|-------------|---------------|---------------|------------------|
| Emergency | 24 hours | 24 hours | 24 hours |
| Non-Emergency | 14 days | 7 days | Reasonable time |
| Damp & Mould | 14 days | 7 days | As specified |

**Additional Features Built:**
- Daily cron job for deadline breach checking
- Email alerts for breach warnings (7-day, 3-day, 1-day)
- PDF reports for HHSRS and DHS assessments
- Remediation job integration with field service
- Security groups and access control

**Depends on:** `property_fielder_property_management`, `property_fielder_field_service`

---

### 17.4 Property Management Addon Architecture (Future Phases)

These addons extend Property Fielder into a full property management platform.

#### Phase A: Core Operations (Post-Compliance)

| Addon | Purpose | Effort |
|-------|---------|--------|
| `property_fielder_property_leasing` | Lease & tenancy management, rent amounts, deposits, guarantors, renewals | 40-60h |
| `property_fielder_property_accounting` | Rent invoicing, payment tracking, arrears, late fees, statements | 50-70h |
| `property_fielder_property_maintenance` | Maintenance requests, work orders, asset register, warranties | 40-60h |
| `property_fielder_tenant_portal` | Tenant self-service: pay rent, submit requests, view documents | 30-40h |

---

#### Phase B: Financial & Compliance

| Addon | Purpose | Effort |
|-------|---------|--------|
| `property_fielder_property_accounting` (enhanced) | Property P&L, owner statements, budget tracking, tax reporting | 50-70h |
| `property_fielder_property_documents` | Document repository, version control, e-signatures, OCR | 30-40h |
| `property_fielder_contractor_management` | Contractor database, accreditation tracking, ratings, invoicing | 30-40h |

---

#### Phase C: Growth & Efficiency

| Addon | Purpose | Effort |
|-------|---------|--------|
| `property_fielder_tenant_screening` | Applications, credit checks, references, Right to Rent, ID verification | 40-60h |
| `property_fielder_property_marketing` | Listings, syndication (Rightmove, Zoopla), viewings, leads | 30-40h |
| `property_fielder_owner_portal` | Owner self-service: reports, statements, maintenance updates | 30-40h |

---

#### Phase D: Advanced Features

| Addon | Purpose | Effort |
|-------|---------|--------|
| `property_fielder_utilities_management` | Utility billing, meter readings, supplier management | 20-30h |
| `property_fielder_insurance_management` | Insurance policy tracking, renewals, claims | 20-30h |
| `property_fielder_key_management` | Key sets, check-out logs, key holder tracking | 20-30h |
| `property_fielder_inventory_management` | Property inventory, condition reports, check-in/out | 20-30h |
| `property_fielder_property_analytics` | Advanced reporting, KPIs, dashboards, forecasting | 40-60h |

---

### 17.5 Complete Addon Dependency Graph

```
Odoo Core (base, mail, web, hr, contacts, project, account)
    │
    ├── property_fielder_field_service ──────────────────────────────────┐
    │       │                                                             │
    │       ├── property_fielder_field_service_mobile                    │
    │       │                                                             │
    │       └── property_fielder_property_management ────────────────────┤
    │               │                                                     │
    │               ├── property_fielder_import                          │
    │               │                                                     │
    │               ├── property_fielder_templates ──┐                   │
    │               │       │                        │                   │
    │               │       └── property_fielder_defects ──┐             │
    │               │               │                      │             │
    │               │               └── property_fielder_hhsrs           │
    │               │                                                     │
    │               ├── property_fielder_tenant_access                   │
    │               │                                                     │
    │               ├── property_fielder_property_leasing ───────────────┤
    │               │       │                                             │
    │               │       └── property_fielder_property_accounting ────┤
    │               │                                                     │
    │               ├── property_fielder_property_maintenance            │
    │               │                                                     │
    │               ├── property_fielder_tenant_portal                   │
    │               │                                                     │
    │               ├── property_fielder_property_documents              │
    │               │                                                     │
    │               ├── property_fielder_contractor_management           │
    │               │                                                     │
    │               ├── property_fielder_tenant_screening                │
    │               │                                                     │
    │               ├── property_fielder_property_marketing              │
    │               │                                                     │
    │               ├── property_fielder_owner_portal                    │
    │               │                                                     │
    │               └── [Phase D addons...]                              │
    │                                                                     │
    └─────────────────────────────────────────────────────────────────────┘
```

---

### 17.6 Addon Summary Table

| # | Addon | Layer | Phase | Status | Effort |
|---|-------|-------|-------|--------|--------|
| 1 | `property_fielder_field_service` | Core | - | ✅ Built | - |
| 2 | `property_fielder_field_service_mobile` | Feature | - | ✅ Built | - |
| 3 | `property_fielder_property_management` | Core | - | ✅ Built | - |
| 4 | `property_fielder_hhsrs` | Domain | - | ✅ Built | - |
| 5 | `property_fielder_import` | Feature | 1 | 🔜 Planned | 15 days |
| 6 | `property_fielder_templates` | Feature | 2 | 🔜 Planned | 18 days |
| 7 | `property_fielder_defects` | Domain | 3 | 🔜 Planned | 26 days |
| 8 | `property_fielder_tenant_access` | Domain | 5 | 🔜 Planned | 16 days |
| 9 | `property_fielder_property_leasing` | Business | A | 🔜 Planned | 40-60h |
| 10 | `property_fielder_property_accounting` | Business | A/B | 🔜 Planned | 50-70h |
| 11 | `property_fielder_property_maintenance` | Business | A | 🔜 Planned | 40-60h |
| 12 | `property_fielder_tenant_portal` | Business | A | 🔜 Planned | 30-40h |
| 13 | `property_fielder_property_documents` | Business | B | 🔜 Planned | 30-40h |
| 14 | `property_fielder_contractor_management` | Business | B | 🔜 Planned | 30-40h |
| 15 | `property_fielder_tenant_screening` | Business | C | 🔜 Planned | 40-60h |
| 16 | `property_fielder_property_marketing` | Business | C | 🔜 Planned | 30-40h |
| 17 | `property_fielder_owner_portal` | Business | C | 🔜 Planned | 30-40h |
| 18 | `property_fielder_utilities_management` | Business | D | 🔜 Planned | 20-30h |
| 19 | `property_fielder_insurance_management` | Business | D | 🔜 Planned | 20-30h |
| 20 | `property_fielder_key_management` | Business | D | 🔜 Planned | 20-30h |
| 21 | `property_fielder_inventory_management` | Business | D | 🔜 Planned | 20-30h |
| 22 | `property_fielder_property_analytics` | Business | D | 🔜 Planned | 40-60h |

**Compliance Addons (PRD Phases 1-7):** ~163 days
**Property Management Addons (Phases A-D):** ~490-700 hours (~12-18 weeks)
**Total Platform:** ~8-10 months with 2-3 developers

---

### 17.7 Benefits of Modular Architecture

| Benefit | Description |
|---------|-------------|
| **Phased Rollout** | Deploy core compliance first, add property management later |
| **Optional Features** | Clients can skip HHSRS if not social housing; skip marketing if not letting agents |
| **Separation of Concerns** | Templates don't know about HHSRS; HHSRS extends Defects cleanly |
| **Independent Testing** | Each addon can be tested and validated independently |
| **Easy Upgrades** | Update one addon without affecting others |
| **Licensing Flexibility** | Can license premium addons (HHSRS, Analytics) separately |
| **Team Parallelization** | Multiple developers can work on different addons simultaneously |

---

### Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2025 | Product Team | Initial requirements |
| 2.0 | Dec 13, 2025 | Product Team | Added fault tracking, remediation workflow, offboarding |
| 2.1 | Dec 13, 2025 | Product Team | Added UK Decent Homes Standard, HHSRS 29 hazards, Awaab's Law compliance |
| 2.2 | Dec 13, 2025 | Product Team | Added Inspection Templates system for mobile app |
| 2.3 | Dec 13, 2025 | Product Team | Updated current state to accurately reflect what's built vs planned |
| 2.4 | Dec 13, 2025 | Product Team | Gemini Review Iteration 1: Fixed terminology (native codes + severity_sla), unified Defect model, re-ordered phases (Templates → Phase 2, HHSRS → Phase 4), added Proof of Service, Contractor Portal, Right to Rent, Access Attempt model, Compliance Log, enhanced mobile requirements (skip logic, image compression, geofence override), added liability logging and import wizard |
| 2.5 | Dec 13, 2025 | Product Team | Gemini Review Iteration 2: Added Key Management (Key Set + Check-Out Log), Contractor Accreditation Verification, Inspector Skills Matrix, How to Rent Guide versioning, Lone Worker Safety (timer + panic button), Draft/Partial Save mode, Keyword Safety Check, Block/Unit hierarchy (parent_id for Fire Safety Act), Smoke vs CO Alarm separation (2022 Regulations), Landlord Refusal workflow with termination warning, Section 21 Eviction Ban flag, moved Data Import to Phase 1 |
| 2.6 | Dec 13, 2025 | Product Team | Gemini Review Iteration 3: Added HMO License model (Housing Act 2004 compliance), EPC Exemption tracking (PRS Exemptions Register), EWS1 Form tracking for blocks over 18m, Void Management Workflow (weekly Security & Flush), Legal Entry (Forced Access) Workflow for emergencies, Cascading Block Compliance (Unit inherits parent compliance status), Inspector Skill Levels (Basic/Advanced/Expert for Asbestos), Mobile Image Annotation tools, Historical Data View (previous inspection readings), Sync Locking Mechanism (Check-out/Check-in), Keyword Check Disclaimer (liability protection) |
| 2.7 | Dec 14, 2025 | Product Team | Gemini Review Iteration 4: Added UPRN field (UK government standard for national landlord register), Deposit Protection to Section 21 blocking, Invoice Blocking on failed Re-Check, Photo Timestamp Watermarking (burned into pixels), Notification Digest Mode (Real-time vs Daily Summary), moved Guest Upload Link to Phase 2 (critical path), updated timeline totals |
| 2.8 | Dec 14, 2025 | Product Team | Added Section 17: Complete Odoo Addon Architecture with 22 addons across 4 layers. Incorporated Property Management Roadmap (leasing, accounting, maintenance, tenant portal, documents, contractors, screening, marketing, owner portal, utilities, insurance, key management, inventory, analytics). Added dependency graph, effort estimates, and phased rollout plan. |

---

*End of Document*
