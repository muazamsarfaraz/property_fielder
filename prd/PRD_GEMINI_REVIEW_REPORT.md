# PRD Review Report by Gemini 3 Pro Preview

**Generated:** 2025-12-14 10:35:08

**Total PRDs Reviewed:** 23

## Summary

| PRD | Status | Score |
|-----|--------|-------|
| MAIN | ✅ | 96% |
| FIELD_SERVICE | ✅ | 94% |
| FIELD_SERVICE_MOBILE | ✅ | 92% |
| PROPERTY_MANAGEMENT | ✅ | 92% |
| DEFECTS | ✅ | 85% |
| HHSRS | ✅ | 94% |
| IMPORT | ✅ | 92% |
| TEMPLATES | ✅ | 95% |
| TENANT_ACCESS | ✅ | 95% |
| CONTRACTOR_MANAGEMENT | ✅ | 85% |
| INSURANCE_MANAGEMENT | ✅ | 92% |
| INVENTORY_MANAGEMENT | ✅ | 92% |
| KEY_MANAGEMENT | ✅ | 96% |
| OWNER_PORTAL | ✅ | 96% |
| PROPERTY_ACCOUNTING | ✅ | 100% |
| PROPERTY_ANALYTICS | ✅ | 96% |
| PROPERTY_DOCUMENTS | ✅ | 88% |
| PROPERTY_LEASING | ✅ | 92% |
| PROPERTY_MAINTENANCE | ✅ | 92% |
| PROPERTY_MARKETING | ✅ | 92% |
| TENANT_PORTAL | ✅ | 90% |
| TENANT_SCREENING | ✅ | 90% |
| UTILITIES_MANAGEMENT | ✅ | 94% |

---

## MAIN

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\PRD_MAIN.md`

This is an exceptionally high-quality Product Requirements Document. It demonstrates a profound understanding of both the Odoo ecosystem and the specific, high-stakes regulatory environment of UK property management.

The inclusion of "unhappy paths" (Landlord Refusal, Legal Entry, Section 21 blockers) elevates this from a standard software spec to a robust operational compliance tool.

Here is my expert review.

---

### 1. Completeness
**Status: Excellent**
The PRD covers the end-to-end lifecycle comprehensively.
*   **Missing Element (Minor): Commercial Lease Responsibility Matrix.**
    *   While you distinguish between Commercial and Residential property types (FR-1.4.2), Commercial compliance is often dictated by the **Lease Type** (FRI - Full Repairing and Insuring vs. Internal Repairing).
    *   **Requirement:** The system needs to know *who* is responsible for a specific compliance area (Landlord vs. Commercial Tenant). You don't want to auto-schedule a Fire Risk Assessment if the Commercial Tenant is contractually liable for it.
*   **Missing Element (Minor): Deposit Scheme Integration.**
    *   You correctly identify that failure to protect a deposit blocks Section 21 (FR-8.6). However, there is no requirement for API integration with TDS, DPS, or MyDeposits to auto-verify this. Currently, it relies on manual data entry (`deposit_protected = Boolean`).

### 2. UK Regulatory Accuracy
**Status: Outstanding**
The regulatory logic is precise and up-to-date with 2024/2025 legislation.
*   **Awaab’s Law & HHSRS:** The translation of Awaab's Law timescales (24h/10 days) into the workflow is accurate. The distinction between Emergency and Significant hazards is handled well.
*   **Section 21 (Eviction) Blockers:** The inclusion of the "How to Rent" guide version history and the Deregulation Act requirements is a critical value-add that many US-centric property systems miss.
*   **Fire Safety Act 2021:** The Block vs. Unit hierarchy logic (cascading compliance) effectively addresses the "External Wall System" (EWS1) and communal area requirements mandated by the Fire Safety Act.

### 3. Workflow Gaps
**Status: Very Good**
*   **Gap: "Fixed on Site" Workflow.**
    *   *Scenario:* A Gas Engineer finds a loose bracket (Minor/NCS) or a generic handyman finds a loose handle during an inspection. They fix it immediately.
    *   *Current Flow:* Inspection Fail -> Defect Recorded -> Remediation Order -> Re-check.
    *   *Issue:* This creates unnecessary administrative overhead for minor issues resolved instantly.
    *   *Recommendation:* Add a `fixed_during_visit` boolean to the Fault/Defect model. If checked, allow the Inspection to result in "Pass" (or "Pass with Rectification") and close the Defect immediately without triggering the Remediation/Re-check loop.
*   **Gap: RAMS (Risk Assessment and Method Statements).**
    *   For Block Management and Commercial remediation (Phase 3/8), you cannot send a contractor on-site without receiving their RAMS, especially for Asbestos or Working at Height.
    *   *Recommendation:* Add a "RAMS Required" flag to the `remediation` model for high-risk work.

### 4. Data Model Issues
**Status: Robust**
*   **Observation:** The `defect` model is trying to serve two masters: Binary Regulatory Faults (Gas/EICR) and Weighted Risk Assessments (HHSRS Likelihood x Severity).
    *   *Risk:* The UI for this form could become cluttered.
    *   *Mitigation:* Ensure Odoo views use `invisible=""` attributes heavily based on `defect_type` so a Gas Engineer never sees "HHSRS Band" fields.
*   **Key Management:** The `key.set` model is good, but lacks a `key_return_date` on the checkout log for alerting when keys are overdue *before* the job is finished.

### 5. Implementation Priorities
**Status: Logical**
*   **Smart Move:** Moving **Data Import to Phase 1** is the correct decision. You cannot validate the complex "Gap Analysis" logic without real, messy legacy data.
*   **Smart Move:** Moving **Guest Upload Link to Phase 2** is critical. Without this, the remediation workflow breaks because external contractors won't adopt a new app for one-off jobs.

### 6. Mobile App Requirements
**Status: Build Ready**
*   **Template System:** The definition of the template engine (Sections -> Items -> Logic) is well structured.
*   **Sync Locking:** The "Check-out/Check-in" lock is essential for data integrity in Odoo.
*   **Liability Protection:** The photo watermarking (burning pixels) is a brilliant detail that saves legal arguments later.

### 7. Risks & Concerns
1.  **Notification Fatigue:** Even with the "Digest Mode," a portfolio manager with 500 properties could get overwhelmed by Awaab's Law countdowns.
    *   *Mitigation:* The dashboard needs a "Traffic Light" system rather than just lists.
2.  **Performance on Budget Devices:** Parsing complex HHSRS templates (29 hazards x 5 questions each + photos) on a 2GB RAM Android device using Flutter might be sluggish if the state management isn't optimized.
3.  **Liability of the "Keyword Check":** If the app scans for "mould" and blocks submission, but the inspector misspells it as "mold" (and the regex misses it), and then a tenant gets sick, the agency might blame the software.
    *   *Mitigation:* Ensure the disclaimer is legally watertight and perhaps add a "fuzzy search" or dictionary check for keywords.

### 8. Recommendations

1.  **Add "Lease Responsibility" Logic:** For the `property` model, add a field to define if compliance is Landlord or Tenant managed (crucial for Commercial/Let Only).
2.  **Implement "Fixed on Site" Logic:** Allow inspectors to close a defect immediately during the inspection to avoid the re-check loop for minor repairs.
3.  **Contractor Insurance Expiry:** You track Accreditation (Gas Safe), but you should also track **Public Liability Insurance** expiry for contractors. You cannot dispatch a contractor without valid insurance.
4.  **Tenant Self-Triage (Future):** In the Tenant Access phase, consider a "Report an Issue" wizard for tenants that uses the same "Keyword Safety Check" to auto-triage incoming maintenance requests as Emergency vs. Routine.

---

### SCORE

**96% - Build Ready**

**Summary:**
This PRD is **exceptionally strong**. It moves beyond "feature listing" into "risk management," which is the core value proposition for UK property professionals. The specific references to Odoo architecture (addon layers) and the detailed handling of UK legislation (Awaab's Law, Section 21) make this document ready for development. The gaps identified above are minor optimizations, not structural blockers.

**Green Light for Phase 1.**

---

## FIELD_SERVICE

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\core\PRD_FIELD_SERVICE.md`

Here is the expert review for the `property_fielder_field_service` Addon PRD.

### 1. Data Model Completeness
**Score: Strong**
The data models are robust and follow Odoo best practices.
*   **Inheritance Pattern:** The strategy of defining the core `job` model here and allowing higher-layer modules (Property Management, Keys) to inject fields via inheritance is architecturally sound and prevents circular dependencies.
*   **Inspector Skills:** Separating `inspector.skill` to track expiry dates and license numbers is excellent for UK compliance (Gas Safe/NICEIC).
*   **Recurrence:** The `job.recurrence` model is well-structured for standard property maintenance cycles.
*   **Refinement Needed:**
    *   **Geocoding Status:** The `job` model has `latitude/longitude`, but no field to track if geocoding was successful (e.g., `geocoding_status`).
    *   **Travel Time:** The `route` calculates total duration, but the `job` model needs a specific `estimated_travel_time` field (separate from job duration) to feed the optimization engine accurately.

### 2. UK Regulatory Accuracy
**Score: Excellent**
This PRD demonstrates a deep understanding of UK property law.
*   **Section 11 L&T Act:** The "24-hour notice" logic, combined with the tracking of notification methods, is legally accurate.
*   **Emergency Exceptions:** The `is_emergency` override and `verbal_consent` fields cover real-world scenarios where the 24-hour rule is legally waived (e.g., gas leaks).
*   **HSE Lone Worker:** The implementation of safety timers and panic buttons directly addresses HSE guidelines for field staff.
*   **GDPR:** The specific cron job to anonymize GPS data (postcode centroid) after a retention period is a standout compliance feature.

### 3. Dependency Chain
**Score: Good**
*   **Explicit Dependencies:** `base`, `web`, `mail`, `contacts`, `hr`.
*   **Missing Dependency:** Section 6 utilizes `resource.calendar` and `resource.resource`. You must add `'resource'` to the `depends` list in the manifest.
*   **External Dependencies:** The PRD mentions Timefold and OSRM. These should be listed as Python/Binary dependencies in the manifest (`external_dependencies`) or clearly marked as requiring a separate connector module.

### 4. Feature Completeness
**Score: High**
*   **Included:** Scheduling, Routing, Skills, Recurrence, Safety, Compliance.
*   **Missing (Critical for Field Service):**
    *   **Offline Capability:** Field inspectors (especially in basements/rural UK) often lose signal. The PRD does not define how data is cached or if an Odoo Mobile framework (like the Enterprise app or a custom PWA) is required.
    *   **Dynamic Risk Assessment:** While Lone Worker covers *safety*, UK HSE often requires a specific "Point of Work Risk Assessment" (POWRA) checklist *before* work starts (e.g., "Is there Asbestos?", "Are there loose pets?"). This is distinct from the generic `checkin`.

### 5. Integration Points
**Score: Very Good**
*   The architecture correctly identifies `property_fielder_property_management` as a consumer of this module, not a dependency.
*   **Gap:** There is no mention of **Invoicing**. If a field service job is billable (e.g., a repair), how does this flow to `account.move`? Consider adding an optional link or a `is_billable` flag that higher layers can utilize.

### 6. Risks & Gaps
*   **Geocoding Reliability:** UK Addresses are notoriously difficult to geocode perfectly without a paid API (Google/Loqate). Relying on free OSM might result in routing errors.
*   **Solver Complexity:** Integrating Timefold (OptaPlanner) is technically complex. Ensure the "fallback" logic (Haversine) is robust enough to work if the solver service is down.
*   **Notification Deliverability:** Section 11 compliance relies on the tenant *receiving* the email/SMS. There is no mention of tracking delivery status (e.g., Sendgrid webhooks or Odoo mail tracking status).

### 7. Recommendations

1.  **Add `resource` to Depends:** Ensure the manifest includes the resource module.
2.  **Add `risk_assessment_ids`:** Create a simple One2many on the job for "Pre-work Risk Assessment" questions to fully satisfy HSE requirements.
3.  **Define Geocoding Trigger:** Add a method `action_geocode()` and a computed field `is_geocoded` to the Job model. Specify which provider (OSM vs Google) is default.
4.  **Offline State Definition:** Explicitly state if this requires the Odoo Enterprise Mobile App or if a custom offline mode is out of scope for *this* specific addon.
5.  **Address Validation:** Add a constraint that prevents `state='scheduled'` if `latitude/longitude` is missing (forces geocoding).

---

### SCORE: 94%
**Build Ready.**
This is an exceptionally well-specified PRD for a UK market module. The regulatory features (Section 11, Lone Worker, GDPR) are standout. With the minor addition of the `resource` dependency and a clear geocoding strategy, this is ready for development.

---

## FIELD_SERVICE_MOBILE

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\core\PRD_FIELD_SERVICE_MOBILE.md`

Here is the expert review for the `property_fielder_field_service_mobile` Addon PRD.

### 1. Data Model Completeness
**Status: Strong, with minor consolidation needed.**
*   **Completeness:** The core models (`photo`, `signature`, `checkin`, `mobile.device`) cover the necessary fields for a mobile backend.
*   **Field Types:** Correctly utilizes `ir.attachment` for binary storage (crucial for database performance) and `Selection` fields for statuses.
*   **Inheritance Issue:** You have defined `JobPhoto` inheritance twice (Section 3.6 and Section 8.1). Section 3.6 adds `checklist_item_id` and `room_id`; Section 8.1 adds `room_id` (duplicate) and `room_area`. These need to be consolidated into a single schema definition.
*   **Safety Timer:** The `property_fielder.safety.timer` model is well-defined but needs a `last_location_lat/long` field to assist responders if the timer escalates.

### 2. UK Regulatory Accuracy
**Status: Excellent.**
*   **Lone Worker Safety:** The inclusion of the Safety Timer (Section 9) aligns perfectly with UK Health & Safety Executive (HSE) guidelines for lone workers.
*   **Evidence Chain:** Digital signatures with SHA-256 hashes and IP logging, plus photo watermarking, meet the evidence standards required for UK Tenancy Deposit Scheme (TDS) disputes.
*   **GDPR:** Explicit `gdpr_consent` flags and `include_in_report` booleans enable compliance with Right to Erasure and Subject Access Requests.

### 3. Dependency Chain
**Status: Needs clarification.**
*   **Odoo Modules:** `depends = ['base', 'web', 'mail', 'property_fielder_field_service']` is listed. However, the model `property_fielder.property.room` is referenced. If this exists in a base module (e.g., `property_fielder_property`), that module must be in the dependency list (unless `field_service` already depends on it).
*   **Python Libraries:** The JWT authentication (Section 10) requires the `PyJWT` library. This must be listed in the `external_dependencies` section of the manifest (`__manifest__.py`).

### 4. Feature Completeness
**Status: High.**
*   **Included:** Offline-first architecture logic, device registration, and safety features are comprehensive.
*   **Missing API Logic:**
    *   **Panic Button:** The endpoint `/mobile/api/safety/panic` is listed, but the backend logic (e.g., immediate SMS/Email to manager, webhook trigger) is not defined in Section 9 like the timer logic is.
    *   **Chunked Uploads:** Mobile networks in the UK (especially rural) can be spotty. High-res photo uploads via standard POST often fail. The API should support chunked uploads or multipart/form-data specifically optimized for unstable connections.

### 5. Integration Points
*   **Mobile App:** The REST API structure is standard and compatible with Flutter.
*   **Checklists:** The link `checklist_item_id` (Section 3.6) correctly bridges the gap between a generic job photo and a specific inspection question response.
*   **Notifications:** The `property_fielder.mobile.device` model prepares the system for Push Notifications, though the actual transport layer (connection to Firebase/APNs) is marked as "Implementation depends."

### 6. Risks & Gaps
*   **JWT Security:** Storing the JWT secret in `ir.config_parameter` is standard, but ensure the code reading it uses `sudo()` cautiously.
*   **Sync Conflict Strategy:** Section 4.4 mentions "Conflict resolution," but the PRD does not define the strategy (e.g., Server Wins vs. Client Wins). Without this, data overwrites on job notes or statuses are a risk.
*   **Filestore Bloat:** High-res photos will consume disk space rapidly. There is no mention of image compression/resizing *on the server side* (Odoo usually stores the original). Consider adding an automated server-side resize hook to limit max dimension (e.g., 1920x1080) upon receipt to save space.

### 7. Recommendations
1.  **Consolidate Photo Model:** Merge Section 3.6 and 8.1 into a single inheritance definition to avoid code duplication errors.
2.  **Define Panic Logic:** Explicitly define what `_trigger_panic_mode()` does (e.g., `mail.channel` notification to `safety_manager_group`).
3.  **Add Python Dependency:** Add `external_dependencies': {'python': ['jwt']},` to the manifest requirements.
4.  **Compression Policy:** Add a requirement for server-side image resizing on the `create` method of `job.photo` to prevent storage bloat.
5.  **Safety Location:** Add `last_known_lat` and `last_known_long` to `property_fielder.safety.timer` so emergency contacts know where to send help.

---

### SCORE: 92%
**Build Ready.**
The PRD is high quality and addresses specific UK safety and legal requirements excellently. With the minor consolidation of the Photo model and explicit Python dependency listing, this is ready for development.

---

## PROPERTY_MANAGEMENT

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\core\PRD_PROPERTY_MANAGEMENT.md`

Here is the focused review for the **Property Fielder Property Management** addon.

### 1. Data Model Completeness
**Status: Strong, but one definition missing.**
*   **Property Model:** Excellent structure. Separating `hmo_room`, `utility_meter`, and `certification` into separate models is the correct relational database approach.
*   **Missing Definition:** You reference `property_fielder.job` in relations (`job_ids`, `inspection_id.job_id`), but the model definition for `property_fielder.job` is missing from Section 3. Even if it exists in the dependency (`property_fielder_field_service`), you must specify if you are adding fields to it (like `property_id`) or if those links already exist.
*   **Field Types:** Correctly identified (e.g., `Monetary` for insurance sums, `Date` vs `Datetime`).

### 2. UK Regulatory Accuracy
**Status: Excellent.**
*   **HMO Standards:** The inclusion of specific room size validation (6.51sqm / 10.22sqm) is spot on with the Housing Act 2004 (as amended 2018).
*   **Fire Safety:** The **EWS1** cascade logic (Block → Unit) is a sophisticated and necessary feature for post-Grenfell UK compliance.
*   **MEES:** Future-proofing the EPC rating cutoff via `ir.config_parameter` is a smart architectural decision given the shifting government targets (EPC C by 2030 proposals).
*   **Council Tax:** Note that while England/Scotland use Bands A-H, **Wales** uses Bands A-I. You should add **'I'** to the selection to cover the full UK.

### 3. Dependency Chain
**Status: Caution Required.**
*   **Circular Risk:** You listed `depends = ['property_fielder_field_service']`.
    *   Usually, a "Core" Property module is the base, and Field Service depends on Property.
    *   If `property_fielder_property_management` is Layer 1 (Core), it should generally **not** depend on an execution layer like Field Service.
    *   **Correction:** Ideally, `property_fielder_property_management` should be the base. The link between Inspections and Jobs should be defined in `property_fielder_field_service` (inheriting `property_management`), or a bridge module. If you keep this dependency, you cannot install Property Management without Field Service, which limits modularity.

### 4. Feature Completeness
**Status: High.**
*   **Key Management:** The `key.set` model tracks `current_holder_id`, but for insurance and security, you need a **History/Audit Log**. Knowing who has it *now* is not enough; you need to know who had it *last week*.
*   **Asset Management:** Separating `property_fielder.property.asset` (Boilers/Circuits) from the Property itself is excellent practice.

### 5. Integration Points
*   **Documents:** Good usage of `ir.attachment`.
*   **Accounting:** `income_account_id` allows seamless invoice generation later.
*   **Leasing:** Clear separation of concerns (Tenancy is separate).

### 6. Risks & Gaps
*   **Land Registry Title Number:** You have UPRN (Location), but you are missing the **Title Number** (Legal Ownership). This is critical for UK landlords.
*   **Key Audit:** Missing check-in/check-out log table.
*   **Address Format:** Standardize on UK format. Ensure `state_id` (used in Odoo for 'Federal State') is hidden or renamed to 'County' via view inheritance to avoid confusion, as UK addresses use County, not State.

### 7. Recommendations

1.  **Add Title Number:** Add `land_registry_title_number` (Char) to `property_fielder.property`.
2.  **Add Key History:** Create a model `property_fielder.key.movement` (Key Set ID, Partner ID, Date Out, Date In) to track the chain of custody.
3.  **Council Tax:** Add Band 'I' to the selection for Welsh properties.
4.  **Refine Dependency:** Re-evaluate if `property_management` should depend on `field_service`. It is cleaner if Property is the base. If you need the `inspection` -> `job` link, consider doing that in the Field Service module using `_inherit`.
5.  **Smart Meter Readings:** Add a boolean `is_estimate` to `meter.reading` explicitly, or rely on `reading_type`. Ensure the dashboard highlights consecutive estimated readings (a common billing issue).

---

### SCORE: 92%
**Build Ready.**
The PRD is exceptionally detailed regarding UK compliance. The logic for HMOs and EWS1 is production-grade. Address the Dependency structure and Key History recommendations during the technical design phase, but the requirements are clear enough to code.

---

## DEFECTS

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\compliance\PRD_DEFECTS.md`

Here is the expert Product Management and Compliance review for the `property_fielder_defects` addon.

### 1. Data Model Completeness
**Score: High**
The data models are comprehensive, particularly the specialized models for `access.attempt`, `improvement.notice`, and `section20.consultation`.
*   **Correction Needed:** The `property_fielder.contractor` model is an **Odoo Anti-Pattern**. Do not create a separate table for contractors. Instead, `_inherit = 'res.partner'` and add an `is_contractor` boolean field. This ensures native integration with Odoo's `purchase` and `account` modules without complex syncing or bridge tables.
*   **Refinement:** `severity_sla` is defined as a `Char` in the defect model but acts as a selection. It should be a `Selection` field or a `Many2one` to a `severity.level` model to ensure data consistency for the computed logic.

### 2. UK Regulatory Accuracy
**Score: Excellent**
The regulatory context is exceptional.
*   **Retaliatory Eviction (Deregulation Act 2015):** The logic blocking Section 21 based on `improvement.notice` is legally accurate. Blocking it based on internal severity (e.g., C1/ID) is a safe "policy" decision (best practice) even if not strictly statutory until the LA serves notice.
*   **Section 20 (L&T Act 1985):** The £250 threshold and 30-day observation periods are correct.
*   **Access:** Logging access attempts is critical for defending against disrepair claims and obtaining injunctions.

### 3. Dependency Chain
**Score: Good**
*   **Circular Dependency Risk:** You noted `property_fielder_templates` in dependencies. Ensure `templates` does **not** depend on `defects`. `defects` should depend on `templates` and extend `inspection.response`. This direction is correct in your PRD, but verify `templates` has no fields pointing to `defects` (use computed fields or transient models if the reverse link is needed for UI).
*   **Missing:** `contacts` (usually part of base, but explicit is better given the contractor logic).

### 4. Feature Completeness
**Score: Very Good**
*   **Missing - Awaab's Law (Damp & Mould):** In the current UK climate, a specific flag for "Damp & Mould" is essential. These defects require strictly accelerated timescales (often 24h investigation, 7d repair) regardless of standard severity codes.
*   **Missing - CDM 2015:** For larger works (Section 20), you should flag **CDM (Construction Design & Management)** compliance. Even minor works require a "Construction Phase Plan" technically, though a light-touch checkbox for "Health & Safety Plan Reviewed" would suffice.

### 5. Integration Points
**Score: Moderate (due to Contractor model)**
*   **Purchase/Finance:** The integration logic described (`action_create_invoice`) works, but if you stick with a separate `contractor` model, the `partner_id` on the invoice will be the generic partner, splitting the audit trail. **Fixing the `res.partner` inheritance resolves this immediately.**
*   **Guest Upload:** The "Magic Link" integration is well-designed and secure.

### 6. Risks & Gaps
1.  **Contractor Data Silo:** Using a separate model for contractors risks disconnecting vendor bills and purchase orders from the actual contractor compliance data (accreditations).
2.  **Section 20 Calculation:** The PRD mentions "30 days". Legally, this must allow for postage. The calculation should be `Date Sent + 2 days (postage) + 30 days`.
3.  **Tenant Recharge:** The PRD mentions creating an invoice. This needs to integrate with the Deposit Management logic (Phase 4?) to potentially flag the deposit for deduction rather than just invoicing the tenant immediately.

### 7. Recommendations

1.  **Refactor Contractor Model:** Change `property_fielder.contractor` to `res.partner` (inherit). Move trades and accreditations to tabs on the partner view.
2.  **Enhance SLA Logic:** Create a `sla.policy` model rather than hardcoding deadlines in Python dicts (`SEVERITY_DEADLINES`). This allows admins to adjust deadlines (e.g., changing "7 days" to "5 days") without code deployments.
3.  **Damp & Mould Flag:** Add `is_damp_mould = fields.Boolean()` to the defect model. If True, force Priority to 'High' or 'Urgent' and SLA to < 7 days.
4.  **Section 20 Date Safety:** Update the observation deadline computation to `fields.Date.add(days=32)` to account for deemed service (postage rules).

---

### PRD SCORE: 85%
**Status: Minor improvements needed.**

**Summary:** This is a high-quality PRD with exceptional domain knowledge embedded. The logic for Section 21 blocking and Section 20 consultation is standout. The only blocker to "Build Ready" is the architectural decision regarding the Contractor model, which needs to use Odoo's native inheritance to avoid technical debt.

**Next Step:** Refactor section 3.4 to inherit `res.partner`, add the Damp/Mould flag, and proceed to build.

---

## HHSRS

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\compliance\PRD_HHSRS.md`

Here is the expert Product Manager and Compliance review for the `property_fielder_hhsrs` PRD.

### Review Summary

This is an exceptionally strong PRD. It demonstrates a deep understanding of the complex UK regulatory environment (Housing Act 2004, Awaab's Law, Decent Homes Standard) and translates them effectively into Odoo data structures. The mathematical models for HHSRS scoring are legally accurate, and the "Clock Stopping" mechanism for access refusal is a critical real-world feature often missed in generic specifications.

### 1. Data Model Completeness
**Status: Strong**
*   **HHSRS Scoring:** The breakdown of `likelihood.band` (RSP) and `hhsrs.assessment` (Outcome probabilities) is mathematically correct and supports the official formula.
*   **History:** Using a One2many `hhsrs_assessment_ids` on the defect is the correct approach to track the degradation or improvement of a hazard over time.
*   **Decent Homes:** The separation of `building.component` allows for granular data, though linking specific components (Kitchen/Bathroom) to Criterion C (Modern Facilities) logic is implied but not explicitly coded in Section 6.

### 2. UK Regulatory Accuracy
**Status: Excellent**
*   **HHSRS:** The 29 hazards and the weighting (10,000/1,000/300/10) are exact.
*   **Awaab’s Law:** The timescales (24h/14d/7d) align with current consultation guidance. The inclusion of "Access Refusal" (`property_fielder.awaab.access.refusal`) is legally vital, as landlords cannot be penalized for delays caused by tenants.
*   **Decent Homes:** Correctly identifies the 4 criteria (A, B, C, D). The implementation of Criterion A (Statutory Minimum) via auto-detection of Cat 1 hazards is perfect.

### 3. Dependency Chain
**Status: Complete**
*   Dependencies are well-defined.
*   **Verification:** Ensure `property_fielder_property_management` actually contains the `epc_rating` field mentioned in Section 7.1. If not, this field definition needs to move to this module or the dependency needs to be updated.

### 4. Feature Completeness
**Status: High (with minor usability gaps)**
*   **Missing - Hazard Profiles:** Inputting Outcome Probabilities (Class I-IV) manually is extremely difficult for general users. In the real world, surveyors use "National Average" profiles as a starting point.
    *   *Gap:* A feature to "Load Standard Profile" (e.g., Average profile for Falls on Stairs) to pre-fill the % spread would significantly improve usability.
*   **Missing - Post-Work Verification:** For Damp & Mould, a maintenance request marked "Done" does not always mean the hazard is gone (e.g., drying out time).
    *   *Gap:* A "Verification Date" field on `damp.mould` separate from the repair completion date is recommended.

### 5. Integration Points
**Status: Well Defined**
*   **Maintenance:** The auto-update of Awaab deadlines based on `maintenance.request` state (`in_progress` / `done`) is excellent automation.
*   **Mail/Chatter:** Heavy reliance on Chatter (`mail.thread`) for audit trails is the correct architectural choice for compliance defense.

### 6. Risks & Gaps
*   **User Error in Probability Entry:** Users might struggle to make the 4 outcome classes sum exactly to 100.00%. A UI widget or wizard is safer than just a validation error.
*   **Criterion C (Modern Facilities) Logic:** The PRD automates Criterion A, B, and D. It leaves Criterion C (Modern Facilities) as a manual boolean or undefined computation. This is a gap in the "Decent Homes" automation story.
*   **Recurrence:** Awaab's Law focuses heavily on recurring issues. The PRD treats Damp/Mould cases linearly. It needs logic to flag if a *new* case is created for the same location < 6 months after a previous one was closed.

### 7. Recommendations

1.  **Add "Standard Hazard Profiles":** Create a model `hhsrs.hazard.profile` (e.g., "Average Fall on Stairs (1920s Terrace)") containing pre-set Outcome Probability spreads. Add a button on the assessment to "Load Profile" to avoid manual percentage typing.
2.  **Enhance Criterion C Logic:** Explicitly map `building.component` types (Kitchen, Bathroom) to `dhs.assessment` to automate Criterion C (e.g., "Fail if Kitchen > 20 years old").
3.  **Damp Verification Step:** Modify `property_fielder.damp.mould` state flow. After `repairs_completed`, add a `verification_period` state before `resolved`.
4.  **Smart Button on Property:** Add a smart button on the main Property view showing "DHS Status" (Decent/Non-Decent) and "Highest Hazard Band" for quick visibility.

---

### SCORE: 94%
**Build Ready.** The PRD is exceptionally detailed, technically sound, and legally accurate. The recommendations above are refinements for Usability and advanced automation, but the core logic is ready for development.

---

## IMPORT

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\compliance\PRD_IMPORT.md`

Here is the expert Product Manager review for the `property_fielder_import` Addon PRD.

### 1. Data Model Completeness
**Score: High**
The data model is well-architected for a generic import tool.
*   **Dynamic Mapping:** Using `ir.model.fields` allows flexibility without hardcoding fields.
*   **Value Mapping:** The `import.value.mapping` model correctly handles the translation between messy source data (e.g., "3 Bed Flat") and Odoo Selection/Many2one fields.
*   **Optimization:** The logic to only store `source_data` for failed rows (`import.log`) is excellent for database hygiene.
*   **GDPR:** The inclusion of `expiry_date` on the batch for auto-cleanup is a critical compliance feature often overlooked in import tools.

### 2. UK Regulatory Accuracy
**Score: High**
The import tool acts as a transport layer, but specific UK-context validation is correctly identified:
*   **UPRN:** The PRD explicitly mentions UPRN duplicate detection and matching.
*   **Postcodes:** Validating formats before commit is essential for UK data.
*   **Idempotency:** The logic to *update* based on UPRN rather than duplicate is vital for maintaining a clean UK property database.

### 3. Dependency Chain
**Score: Solid**
*   **`queue_job`:** This is the correct architectural choice for bulk imports in Odoo to prevent HTTP timeouts.
*   **`pandas` / `openpyxl`:** Necessary for robust Excel parsing. Ensure these are listed in the `manifest` under `external_dependencies` and in `requirements.txt` for Odoo.sh deployment.

### 4. Feature Completeness
**Score: High**
*   **Error Handling:** The "Export Error CSV" feature is the single most important feature for user experience in data migration. This is well specified.
*   **Rollback:** The "Undo" feature (archiving records) is a smart safety net.
*   **Dry Run:** Essential for testing mappings.

### 5. Integration Points
The integration logic is sound:
*   It does not try to be a generic "Odoo Import" replacement but specifically targets Property, Certification, Tenant, and Contractor models.
*   The `relational.lookup` logic handles the complex linking required between Properties and Landlords (Contacts).

### 6. Risks & Gaps
*   **Binary/Attachment Upload Mechanism:** Section 7.2 mentions `attachment_folder` and importing generic binaries. **Gap:** The PRD does not specify *how* the user uploads the companion files (e.g., PDF certificates). Browsers cannot access local folder paths (e.g., `C:/Users/...`).
    *   *Risk:* Users cannot import historical safety certificates.
*   **Pandas Memory Usage:** Parsing very large Excel files with Pandas can cause OOM (Out of Memory) kills on smaller Odoo containers.
*   **Undo Limitations:** The `action_undo_batch` assumes the target model has an `active` field. If a custom model lacks `active`, this function will crash or fail to hide the records.

### 7. Recommendations

1.  **Add ZIP Support for Attachments:**
    *   Modify `property_fielder.import.batch` to accept a secondary binary field `attachment_zip`.
    *   Update logic: If `is_attachment` is mapped, look for the filename inside the uploaded ZIP file rather than a local path.
2.  **Streaming Parsing:**
    *   Explicitly specify that Excel files should be read in "read_only" mode or chunked if possible to spare memory, or strictly enforce a row limit per batch (e.g., 5000 rows).
3.  **Address Sanitization:**
    *   Add a specific "Transformation" option in `mapping.line` for **UK Address Composition**. (e.g., combining "Line 1" + "Line 2" if the target Odoo field is a single text block, or splitting them if vice versa).
4.  **Safety Check on Undo:**
    *   Update the `action_undo_batch` code snippet to check `if 'active' in record._fields` before attempting to archive. If not present, log a warning or delete (if permissions allow).

---

### SCORE: 92%
**Status: Build Ready**

This is an exceptionally strong PRD. It covers the "Happy Path" (import success) and the "Unhappy Path" (error handling, rollback, GDPR cleanup) effectively. With the minor adjustment for ZIP file handling, this is ready for development.

---

## TEMPLATES

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\compliance\PRD_TEMPLATES.md`

Here is the expert review for the `property_fielder_templates` Addon PRD.

### 1. Data Model Completeness
**Status: Strong**
The data model is highly detailed and structurally sound for Odoo 16/17+.
*   **Relational vs. JSON:** The decision to use proper relational models (`template.item.option`) for standard dropdowns while using `response_json` for complex matrix/tabular data is excellent. It solves the reporting problem for standard KPIs while retaining flexibility for complex grids.
*   **Inheritance:** The Delegation Inheritance (`_inherits`) link to `property_fielder.job` is logically sound ("An Inspection IS A Job"), ensuring inspections integrate natively with scheduling, billing, and timesheets defined in the `field_service` layer.
*   **Matrix Schema:** The inclusion of specific `row` and `column` models allows the mobile app to render grids dynamically without hard-coding, which is critical for HHSRS and room-by-room condition reports.

### 2. UK Regulatory Accuracy
**Status: Excellent**
*   **Gas Safety (CP12):** The inclusion of **ID** (Immediately Dangerous), **AR** (At Risk), and **NCS** (Not to Current Standards) as specific selection types is accurate to current Gas Safe regulations (IGEM/G/11).
*   **Electrical (EICR):** **C1/C2/C3/FI** codes are correctly identified.
*   **Legal Admissibility:** The **Inspector License Snapshot** logic is critical. Storing the license number *at the moment of record creation* (rather than relying on the current user profile) ensures the certificate remains valid even if the inspector's license expires later.

### 3. Dependency Chain
**Status: Correct**
*   **Circular Dependencies Avoided:** The explicit note that `defect_id` is added via inheritance in the `defects` addon (Layer 3) validates that the dependency chain is clean: `field_service` → `templates` → `defects`.
*   **Mobile Optionality:** Keeping `field_service_mobile` optional ensures the backend can be tested and used via the web interface without requiring the mobile environment.

### 4. Feature Completeness
**Status: Very High**
*   **Versioning:** The `draft/active/archived` lifecycle is essential for audit trails.
*   **Pre-fill Logic:** The logic provided (`_get_previous_response`) is robust, handling the specific requirement of finding the *last done* inspection for the *same property* and *same template*.
*   **Calculation Engine:** The inclusion of `safe_eval` logic for scoring (e.g., calculating a specialized HHSRS score) is a sophisticated feature that elevates this beyond a simple form builder.

### 5. Integration Points
**Status: Clear**
*   **Property Assets:** The separation of the Asset model (Layer 1) and the Inspection Asset Response (Layer 2) is correct. It allows the template to iterate over existing assets (Boiler, Cooker) or create new ones on the fly.
*   **Reporting:** The PRD identifies `report_template_id`.

### 6. Risks & Gaps
*   **Report Generation Complexity:** While storing matrix data in `response_json` is efficient for storage, it makes QWeb PDF generation difficult. The standard QWeb engine cannot easily iterate over raw JSON without a specific parsing method in the report abstract model.
*   **Delegation Inheritance Performance:** Using `_inherits` (delegation) creates a database join for every read operation on Inspections. For high-volume systems (100k+ inspections), this can degrade performance compared to standard prototype inheritance (`_inherit`), although it offers cleaner UI integration.
*   **Validation Backend vs. Frontend:** The PRD defines validation rules. Ensure these are enforced in the Python `write()` method, not just the Mobile/Web UI, to prevent API-injected invalid data.

### 7. Recommendations
1.  **Add JSON Parser for Reports:** Add a helper method in `property_fielder.inspection` or an Abstract Report model that converts the `response_json` into a Python dictionary/list object accessible by QWeb reports (e.g., `get_matrix_data(item_id)`).
2.  **Snapshot Template Structure:** When an inspection is completed, the structure of the *questions* at that time should ideally be preserved. If a Template Item is changed in the "Active" version, old inspections might break if they reference an Item ID that has changed meaning. **Recommendation:** Enforce "Immutable" templates—once Active and used, a template cannot be edited; it must be cloned to a new version.
3.  **Fault Code Mapping:** You use a string reference for `fault_code_reference`. Add a method `_get_suggested_fault()` that searches the Fault Code model (in the Defects addon) based on this string to separate the layers cleanly while maintaining functionality.

### Score
**95% - Build Ready**

This is an exceptionally high-quality PRD. The data architecture accurately balances Odoo's ORM strengths with the flexibility required for complex compliance forms. The specific attention to UK regulatory requirements (license snapshots, severity codes) reduces legal risk significantly.

**Action:** Proceed to development. Focus the technical design on the **QWeb Report Parser** for the JSON fields.

---

## TENANT_ACCESS

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\compliance\PRD_TENANT_ACCESS.md`

Here is the expert review for the `property_fielder_tenant_access` Addon PRD.

### 1. Data Model Completeness
**Status:** ✅ **Excellent**
The data models are well-structured and leverage standard Odoo relationships effectively.
*   **Strengths:**
    *   The separation of `access.booking` (planning) and `access.attempt` (execution) is architecturally sound.
    *   `device_timestamp` alongside standard `create_date` is a critical distinction for mobile/offline field operations.
    *   `evidence_bundle_id` handling via `ir.attachment` is the correct Odoo approach for document persistence.
*   **Minor Note:** In `property_fielder.access.booking`, `proposed_time_start` (Float) is standard Odoo, but ensure the UI renders this as `HH:MM` for the tenant portal to avoid UX friction (e.g., displaying "14.5" instead of "14:30").

### 2. UK Regulatory Accuracy
**Status:** ✅ **High**
The PRD demonstrates strong domain knowledge of UK Housing Law.
*   **Accurate:** Section 11 (24h notice) and the "Court-Ordered Entry" (vs Forced Entry) terminology is legally precise.
*   **Escalation Logic:** The 3-step escalation (Card -> Warning -> Notice) aligns perfectly with the pre-action protocol required for obtaining a gas injunction in UK courts.
*   **How to Rent:** Tracking the `guide_version` is crucial as serving an outdated guide invalidates Section 21 notices.

### 3. Dependency Chain
**Status:** ⚠️ **Check Required**
*   **Current:** `base`, `mail`, `sms`, `calendar`, `portal`, `website`, `property_fielder_property_management`, `property_fielder_field_service`.
*   **Missing/Implicit:**
    *   **Contacts (`contacts`):** Implicitly covered by `base`, but often good to list if you are using specific address formatting logic.
    *   **Project/Task:** If `job` inherits from `project.task`, ensure `project` is listed. If `job` is a custom model in `property_fielder_field_service`, the current list is fine.

### 4. Feature Completeness
**Status:** ✅ **Very High**
*   **Conflict Resolution:** The logic defined in `6.3` (Tenant proposes -> Dispatcher approves) is excellent. It prevents the common error of external users overwriting internal staff calendars.
*   **Evidence Bundle:** The automated PDF generation including photos and GPS logs is a high-value feature that solves a major pain point (preparing legal packs manually).
*   **Missing:**
    *   **Timezone Handling:** The PRD mentions timestamps. Legal documents **must** show the time in the Property's local time (Europe/London), not UTC. The report generation logic needs to explicitly handle timezone conversion.

### 5. Integration Points
**Status:** ✅ **Solid**
*   **Calendar:** The integration via `calendar_event_id` is standard.
*   **Portal:** The route logic utilizing a secure token avoids the need for tenants to have full Odoo user accounts, which is the correct license-friendly approach.
*   **Field Service:** The link to `inspector_id` allows for route planning integration later.

### 6. Risks & Gaps
1.  **Message Filtering for Court:** When generating the **Evidence Bundle**, the system must strictly separate "Internal Notes" (Chatter) from "Sent Notifications". You cannot accidentally include an internal note saying "This tenant is difficult" in a court bundle.
    *   *Risk:* High (Legal/Reputational).
2.  **Key Access Bypass:** The workflow assumes the tenant must grant access. In UK Lettings, if "Management Keys" are held, the 24h notice is informational ("We are entering with keys"), not a request for booking.
    *   *Gap:* The model needs a flag on `booking` for `access_method` (Tenant Present vs. Management Keys). If Keys, the workflow shouldn't ask the tenant to "Confirm", but rather "Acknowledge".

### 7. Recommendations

1.  **Refine Evidence Bundle Logic:**
    *   Update `action_generate_evidence_bundle` to explicitly filter `mail.message` to include only subtype `mail.mt_comment` where `partner_ids` includes the tenant, or messages specifically flagged as `is_formal_notice`. Exclude internal notes.
2.  **Add Timezone to Report:**
    *   Ensure the QWeb report explicitly converts `device_timestamp` (UTC) to 'Europe/London' before printing it on the PDF.
3.  **Key Management Toggle:**
    *   Add field `access_method` (Selection: `appointment`, `keys`).
    *   If `keys`: Change notification text from "Please confirm" to "We will attend using management keys. Please contact us if inconvenient."
4.  **Cron for Token Expiry:**
    *   Add a scheduled action to mark bookings as `no_response` if `token_expiry` passes without action (automating the escalation trigger).

---

### SCORE: 95%
**Build Ready.**
This is an exceptionally well-specified PRD. It addresses the "Happy Path" (booking) and the "Unhappy Path" (legal escalation) with equal depth. The technical logic (GPS math, portal conflict resolution) is sound. With the minor addition of Timezone handling and internal note filtering, this is ready for development.

---

## CONTRACTOR_MANAGEMENT

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_CONTRACTOR_MANAGEMENT.md`

Here is the expert review of the **property_fielder_contractor_management** PRD.

### 1. Data Model Completeness
**Status:** ⚠️ **Issues Detected**
*   **Circular Reference:** In Section 5.4 (`PaymentApplication`), the model defines `work_order_id = fields.Many2one('property_fielder.work.order')`.
    *   *Problem:* The PRD explicitly states in Section 2 that `property_fielder_property_maintenance` (where Work Orders live) depends on *this* module. This module **cannot** reference a model (`work_order`) that exists in a downstream module. This will cause an immediate registry error during installation.
*   **Standard Fields:** The use of `_inherit = 'res.partner'` is correct.
*   **Monetary/Currency:** Correctly implemented with `currency_id` pairings.

### 2. UK Regulatory Accuracy
**Status:** ✅ **Excellent**
*   **CIS Implementation:** Using the Odoo `account.tax` engine (negative taxes) is the *only* correct way to handle CIS in Odoo for accurate remittance and accounting. The logic provided is spot-on.
*   **Retention:** Implementing retention via Journal Entries (Liability accounting) rather than just reducing the invoice amount is legally accurate and accounting-friendly.
*   **DRC VAT:** Correctly identified as a tax mapping issue.
*   **Insurance:** The distinction between Public Liability (£2M) and Employers' Liability (£5M) is accurate for UK law.

### 3. Dependency Chain
**Status:** ❌ **Broken**
*   As noted in Data Models, the logic for **Payment Applications** (Section 5.4) belongs in the bridge module `property_fielder_maintenance_accounting` or the `maintenance` module, not here.
*   This base contractor module should strictly handle: Partner Data, Compliance Docs, CIS Settings, and standard Vendor Bills. It should not know about "Work Orders."

### 4. Feature Completeness
**Status:** 🟡 **Partial**
*   **Gas Safe/API:** "Gas Safe Register check" is listed as a feature, but there are no fields to store API Keys, API responses, or "Last Checked Timestamp" in the data model. The logic for *how* this check happens is missing.
*   **Portal:** Features are listed (Submit quotes, invoices), but the *Controllers* or specific Portal Access Rules (Record Rules) are not defined.

### 5. Integration Points
**Status:** ✅ **Good**
*   **Accounting:** The hooks into `account.move` and `account.move.line` for CIS and Retention are well-defined.
*   **Document Management:** Good integration with `ir.attachment` for insurance and self-billing.

### 6. Risks & Gaps
*   **GDPR:** While UTRs are protected, the *Insurance Certificates* and *Self-Billing Agreements* often contain personal signatures/names. These attachments need specific access groups, not just the fields.
*   **Legacy Data:** No migration strategy for importing existing CIS statuses or verification numbers.
*   **Verification History:** While the current status is stored, there is no audit log model defined for *history* of verifications (e.g., "Was this contractor verified on the specific date the job was performed?").

### 7. Recommendations
To make this **Build Ready**:

1.  **MOVE CODE:** Move the entire `property_fielder.payment.application` model (Section 5.4) and the `action_generate_self_bill` method (Section 5.6) to the **bridge module** (`property_fielder_maintenance_accounting`). This resolves the circular dependency with Work Orders.
2.  **API Config:** Add a `res.config.settings` inheritance to store API keys for Gas Safe/NICEIC integrations.
3.  **Verification Log:** Add a simple log model `contractor.verification.log` to track when checks were made and the result (Auditors often ask: "Did you check they were valid *at the time*?").
4.  **Payment Terms:** Explicitly set a default Payment Term for contractors (e.g., "30 Days") in the data files to prevent manual errors.

---

### SCORE: 85%
**Status:** 🟡 **Minor improvements needed**

**Summary:** The regulatory compliance logic (CIS, DRC, Retention) is **outstanding** and represents the hardest part of this requirement. However, the architectural structure regarding **Payment Applications** creates a hard circular dependency that renders the module un-installable as written. Once Section 5.4 is moved to a bridge module, this is a high-quality specification.

---

## INSURANCE_MANAGEMENT

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_INSURANCE_MANAGEMENT.md`

Here is the focused review of the **Property Fielder Insurance Management** Addon PRD.

### 1. Data Model Completeness
**Score: High**
The models are robust and cover the necessary relationships for UK property management (Portfolio policies, HMO requirements, and Block management exceptions).
*   **Observation:** The separation of `premium_net` and `ipt_amount` is excellent.
*   **Gap:** In commercial or block policies, there is often a distinction between "Declared Value" and "Sum Insured" (Day One Reinstatement basis). Currently, you only have `coverage_amount`.
*   **Correction:** `property_ids` (Many2many) correctly handles portfolio policies, but you may need a `coverage_allocation` field on the relation table if the premium/coverage needs to be split analytically per property for P&L reporting.

### 2. UK Regulatory Accuracy
**Score: High**
*   **HMO Compliance:** The £5M Public Liability validation check is spot-on for UK HMO licensing requirements.
*   **FCA Compliance:** Including `ipid_document_id` and `statement_of_facts_id` is a great detail for regulatory record-keeping.
*   **IPT (Insurance Premium Tax):** You have identified the correct standard rate (12%). **However**, hardcoding `0.12` in the Python code (Section 4.6) is a bad practice. UK budgets can change this rate.
    *   *Fix:* Link `ipt_amount` calculation to an Odoo Tax object or a configuration setting, not a hardcoded float.

### 3. Dependency Chain
**Score: Medium**
*   **Missing Dependency:** Section 4.7 (`_check_rent_guarantee_validity`) references `property_fielder.tenant.application`.
    *   However, Section 2 (Dependencies) does **not** list a tenant referencing or onboarding module. This code will cause an `ImportError` or `AttributeError` if that module is not installed.
*   **Correction:** Add `property_fielder_tenant_referencing` (or equivalent) to the manifest dependencies.

### 4. Feature Completeness
**Score: High**
*   **Block Management Awareness:** The `is_block_insured` logic in Gap Detection is vital for UK Leasehold properties. Without this, the system would flag false positives for every leasehold flat.
*   **Missing Workflow - Excess Recovery:** You track `excess_payer = tenant`, but there is no specific "Action" button to **invoice the tenant for the excess**. You have an action to recharge the *premium*, but not the *claim excess*.

### 5. Integration Points
**Score: Very High**
*   **Accounting:** The logic to split the Vendor Bill into Net + IPT lines is excellent for correct tax reporting.
*   **Maintenance:** Linking Claims to Maintenance Requests provides the full audit trail from "Leaking Pipe" -> "Plumber Fixed" -> "Insurance Paid".

### 6. Risks & Gaps
1.  **Hardcoded Tax Rate:** As mentioned, hardcoding 12% IPT is a technical debt risk.
2.  **Unoccupancy Clauses:** UK insurance policies almost universally have a clause reducing cover after 30 or 60 days of vacancy. The system knows if a property is empty (via Property Management module).
    *   *Risk:* A property sits empty for 45 days, the policy lapses to "Fire & Fleet only" silently, and a burst pipe claim is rejected. The system should alert on `Vacancy > Policy Unoccupancy Limit`.
3.  **Claims Inflation:** In the current economy, `coverage_amount` needs index-linking. There is no field to store "Last Index Date" or "Index Percentage" to auto-update sum insured.

### 7. Recommendations

1.  **Refactor IPT Logic:** Change `rec.premium_net * 0.12` to use `self.env['account.tax']` or a `ir.config_parameter` so the rate can be updated by a user without a code deployment.
2.  **Fix Dependency:** Add the module containing `property_fielder.tenant.application` to the `depends` list.
3.  **Add Unoccupancy Alert:** Add a field `unoccupancy_days_limit` (default 30) to the Policy model. Add a scheduled action to check `property.days_vacant > policy.unoccupancy_days_limit` and notify the property manager.
4.  **Add "Invoice Excess" Action:** On the Claim model, add a button `action_invoice_excess_to_tenant()` if `excess_payer == 'tenant'`.
5.  **Refine Portfolio Costing:** If a policy covers 10 properties for £1000, how is that cost allocated in the P&L? Consider adding an analytic distribution logic to `action_create_premium_bill` to split the cost across the 10 properties' analytic accounts.

---

### SCORE: 92% (Build Ready)

**Summary:** This is an exceptionally well-thought-out PRD for the UK market. The data structures for Leasehold vs Freehold (Block insurance) and HMO liability demonstrate deep domain knowledge. With the minor fix to the hardcoded tax rate and the dependency correction, this is ready for immediate development.

---

## INVENTORY_MANAGEMENT

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_INVENTORY_MANAGEMENT.md`

Here is the expert review of the **Property Fielder Inventory Management** Addon PRD.

### 1. Data Model Completeness
**Status: High Quality**
*   **Strengths:** The use of `origin_item_id` and `origin_room_id` for Check-in vs. Check-out comparison is excellent and solves the common "renaming" issue. The inclusion of metadata (IP, GPS) for signatures is crucial for legal non-repudiation in the UK.
*   **Gaps:**
    *   **Template Models:** Section 6.1 references `property_fielder.inventory.room.template` and `item.template`, but these tables are not defined in Section 3.
    *   **Photos:** While `ir.attachment` is used, there is no specific field/flag to distinguish "Check-in Photo" vs "Check-out Photo" on the item itself other than the record context. This is fine, but ensures the UI can separate them clearly.

### 2. UK Regulatory Accuracy
**Status: Excellent**
*   **Strengths:** Explicit handling of **FFHH** (Homes Act 2018) is vital. The **Fair Wear & Tear** logic (being editable rather than computed) is perfectly aligned with TDS/DPS adjudication guidelines.
*   **Minor Adjustment:**
    *   **Smoke/CO Alarms:** The boolean `smoke_alarms_tested` is good, but for full compliance protection, add `smoke_alarm_location` and `smoke_alarm_expiry_date`. Adjudicators often ask *where* the tested alarm was.

### 3. Dependency Chain
**Status: Correct**
*   `account` is correctly included for deposit deductions.
*   `portal` is included for tenant review.
*   `property_fielder_property_maintenance` is included for work orders.
*   **No missing dependencies found.**

### 4. Feature Completeness
**Status: Very Good**
*   **Missing Feature (Interim Inspections):** The overview mentions `inventory_type = interim`. However, the logic for `interim` is missing. Interim inspections should **not** trigger deposit deductions or betterment calculations; they should trigger maintenance or tenant warnings.
*   **Missing Feature (Tenant Evidence):** During the "Tenant Review" (7 days), the tenant can add comments. In the UK, tenants are often allowed to upload their own photos if they dispute a condition claim at check-in. The current model lacks `tenant_upload_ids`.

### 5. Integration Points
**Status: Solid**
*   **Accounting:** The journal entry creation logic (Deposit Liability -> Income) is accurate.
*   **Maintenance:** The trigger from "Damaged" items to Work Orders is well defined.
*   **Gap:** **Leasing Automation.** There is no specified trigger to auto-create the "Check-in Inventory Draft" when a Tenancy is confirmed. This should be added to reduce admin friction.

### 6. Risks & Gaps
*   **Database Bloat (Critical):** Storing high-res photos for every room/item in `ir.attachment` (inside the Postgres DB by default in some configs) will cause the database size to explode.
    *   *Mitigation:* Ensure the implementation enforces filesystem storage for attachments or integrates with an S3 bucket.
*   **Sync Conflict:** The "Server Wins" strategy in offline sync is risky. If a clerk spends 3 hours on a tablet and the server overwrites it because of a state change, data is lost.
*   **API Security:** The `upload_image` endpoint relies on `auth='user'`. Ensure the user has write access specifically to that `inventory_id` to prevent malicious overwrites of other reports.

### 7. Recommendations

1.  **Refine Interim Logic:** Add a constraint that `action_post_deductions` and `betterment` logic are hidden/disabled if `inventory_type == 'interim'`.
2.  **Enhance Tenant Portal:** Add `tenant_photo_ids` (Many2many ir.attachment) to `property_fielder.inventory.item` to allow tenants to upload counter-evidence during the review phase.
3.  **Define Template Models:** Explicitly list the data fields for `inventory.room.template` and `inventory.item.template` in Section 3.
4.  **Alarms Detail:** Change `smoke_alarms_tested` to a One2many model or add `location` and `expiry` fields for robust compliance.
5.  **Storage Strategy:** Add a technical note to configure `ir_attachment.location` to `file` or S3 to prevent database performance degradation.

---

### SCORE: 92%
**Build Ready.**
The PRD is exceptionally strong on the "Business Logic" of property management (Fair wear, betterment, linking). The gaps are minor technical definitions and one missing feature regarding tenant photo uploads. Proceed to build with the recommendations above.

---

## KEY_MANAGEMENT

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_KEY_MANAGEMENT.md`

Here is the expert review for the `property_fielder_key_management` Addon PRD.

### Review Summary

This is an exceptionally well-structured PRD that demonstrates a deep understanding of both Odoo architecture (Bridge modules) and UK Compliance (Tenant Fees Act 2019). The data models are robust, the separation of concerns regarding security (alarm codes) is handled correctly, and the field operations workflows (handshakes) are practical for real-world scenarios.

### 1. Data Model Completeness
**Status: ✅ Excellent**
*   **Key Set:** The separation of `tag_reference` (physical label) and `name` is crucial for property management and is correctly implemented. The `active` flag implementation for archiving is correct.
*   **Alarm Codes:** Creating a separate model `property_fielder.property.alarm.code` with specific ACLs (`group_key_manager`) is the correct architectural decision for data security.
*   **Log:** The inclusion of `signature_attachment_id` and `cost_evidence_attachment_ids` handles the necessary evidentiary requirements well.

### 2. UK Regulatory Accuracy
**Status: ✅ High Compliance**
*   **Tenant Fees Act 2019:** The PRD correctly identifies that landlords/agents cannot charge arbitrary fees for lost keys. The inclusion of `actual_replacement_cost` and `cost_evidence_attachment_ids` on the log specifically addresses the legal requirement to provide evidence of cost before charging a tenant.
*   **GDPR/Security:** The specific instruction to **exclude** property addresses from printed key tags protects against liability if keys are lost in public.

### 3. Dependency Chain
**Status: ✅ Correct**
*   The use of a **Bridge Module** (`property_fielder_field_service_keys`) to link Jobs and Keys is the correct architectural pattern. It ensures the Key module remains usable for "Lettings Only" agencies that do not use the Maintenance/Field Service module.

### 4. Feature Completeness
**Status: ✅ Strong**
*   The "Field-to-Field Transfer" with a "Handshake" (Accept/Reject) mechanism is a high-value feature that solves a common dispute point in property management ("I never received those keys").
*   **Missing:** A specific state for **'Destroyed/Broken'**. Currently, `state` has `lost` or `replaced`. If a key breaks in a lock, it isn't lost, but it is no longer usable.

### 5. Integration Points
**Status: ✅ Good**
*   **QR Scanning:** The `action_scan_key_qr` method implies a frontend scanner.
*   **Job Blocking:** The constraint `_check_key_checkout` preventing job start without key verification is excellent for process enforcement.

### 6. Risks & Gaps
*   **Encryption Implementation:** The PRD mentions "Odoo's encrypted field storage". Standard Odoo `Char` fields are stored in plain text in PostgreSQL. To truly encrypt this `code` field at rest, you must use a specific widget or Python library (like `cryptography.fernet`) in the `create/write/read` methods, or rely on a third-party encryption module.
*   **Scanning UI:** The backend logic for `action_scan_key_qr` is defined, but the UI trigger (e.g., a button in the Mobile view or integration with the Odoo Barcode app) is not explicitly detailed.
*   **Holder cleanup:** If a Staff Member (User) is archived/deactivated, is there a check to ensure they aren't holding keys?

### 7. Recommendations

1.  **Add 'Destroyed' State:** Add `destroyed` to `property_fielder.key.set` state selection to track broken keys that don't trigger the "Lost Key/Security Risk" workflow.
2.  **Define Encryption Strategy:** Be specific about the Alarm Code encryption. Recommend using a `compute` field that decrypts on the fly for authorized users, storing the raw value in an encrypted binary or text field.
3.  **User Deactivation Constraint:** Add a constraint on `res.users` / `res.partner` write methods: Prevent archiving a user/partner if `property_fielder.key.set` shows they are the `current_holder_id`.
4.  **Key Tag UX:** Suggest adding a boolean on the Key Tag report wizard: `Include Alarm Code?` (Defaults to False). Sometimes contractors need the alarm code printed on a temporary slip if they don't have app access.

### SCORE
**96% - Build Ready**

This PRD is excellent. It addresses the specific legal nuance of the UK market and adheres to Odoo best practices. The recommendations above are minor refinements. **Proceed to build.**

---

## OWNER_PORTAL

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_OWNER_PORTAL.md`

Here is the review of the **Property Fielder Owner Portal** PRD.

### Review Summary

This is an **exceptionally high-quality PRD**. It demonstrates a deep understanding of both Odoo's internal accounting logic (`account.move.line` allocation) and UK specific property legislation (NRLS, CMP, GDPR). The security measures designed for bank details updates are bank-grade and exceed standard Odoo implementations. The handling of Joint Ownership via percentage splits on accounting lines is complex but defined with sufficient technical detail to be buildable.

### 1. Data Model Completeness
**Score: High**
The models are robust.
*   **Joint Ownership:** The separation of `property.ownership` from `res.partner` allows for correct historical tracking of ownership changes.
*   **Accounting Links:** Linking `statement.line` back to `account.move.line` with an `amount_allocated` field is the correct architectural decision to support partial payments and joint ownership splits without breaking the general ledger.
*   **Bank Security:** The addition of `pending_bank_account_id` and token fields directly on `res.partner` enables the required security workflow.

### 2. UK Regulatory Accuracy
**Score: Perfect**
*   **NRL Scheme:** The logic explicitly corrects a common error (taxing net payable vs. taxable income) and correctly identifies deductible vs. non-deductible lines.
*   **CMP Compliance:** The inclusion of the Client Money Protection footer fields on the PDF report satisfies UK Trading Standards requirements (Consumer Rights Act 2015).
*   **Tax Basis:** Offering both Cash Basis (standard for individuals) and Accruals Basis (for Ltd Co owners) for the Tax Summary report is a significant value-add.

### 3. Dependency Chain
**Score: Good**
*   Dependencies are listed correctly.
*   **Note:** While `property_fielder_property_accounting` is listed, ensure that the `account` module is strictly depended upon if any direct overrides (like `account.move.line` inheritance) are done in this module, though usually transitive dependencies cover this.

### 4. Feature Completeness
**Score: High**
*   **Happy Path:** Statement generation, PDF download, and payment locking are covered.
*   **Unhappy Path:** Disputes, maintenance approvals, and bank change cooling-off periods are well defined.
*   **Gap:** There is no explicit mention of how **Credit Notes** (refunds to tenants) are handled in the statement wizard. They should appear as negative income or positive expense offsets.

### 5. Integration Points
**Score: Strong**
*   **Accounting:** The logic `_populate_lines_from_accounting` ensures the portal is a view of the GL, not a separate ledger, which ensures data integrity.
*   **Maintenance:** The approval threshold workflow correctly bridges the operational and financial modules.

### 6. Risks & Gaps
*   **Rounding Errors (Currency):** In Joint Ownership, splitting a £100.00 rent 3 ways (33.333%) results in a penny discrepancy (£33.33 * 3 = £99.99). The PRD does not specify how to handle the remainder (e.g., allocate remainder to the "Primary Contact" owner).
*   **Zero-Value Statements:** The wizard should ideally skip generating statements if the opening balance is 0 and there are no move lines in the period, to avoid spamming owners with empty PDFs.
*   **Retained Amount Journal Entries:** When `retained_amount` is used, the funds sit in the client account. The PRD mentions releasing it, but doesn't explicitly state if a journal entry is needed to move funds between a "Retained Funds" liability account and the "Owner Payable" account.

### 7. Recommendations

1.  **Rounding Strategy:** Add logic to the Statement Wizard for joint ownership: *“Calculate share for all secondary owners first, then allocate the remaining `amount_residual_statement` to the Primary Contact owner to resolve rounding differences.”*
2.  **Credit Note Handling:** Explicitly state in Section 5.8 that `account.move.line` searches must include Credit Notes (refunds) and display them correctly on the statement.
3.  **Onboarding Migration:** Add a field `opening_balance_method` to the Statement Wizard. The very first statement for an owner might need a manual opening balance input if migrating from another system, as there will be no previous statement to look up.
4.  **Report Filename:** Define the PDF filename format (e.g., `Statement_YYYY-MM_OwnerName.pdf`) for easier file management by the user.

---

### PRD SCORE: 96%
**Build Ready.**
The document is technically sound, legally compliant, and sufficiently detailed for a senior developer to implement immediately. The recommendations above are edge-case refinements, not structural blockers.

---

## PROPERTY_ACCOUNTING

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_PROPERTY_ACCOUNTING.md`

Here is the expert review for the `property_fielder_property_accounting` PRD.

### 1. Data Model Completeness
**Score: High**
The data models are robust and leverage Odoo's native accounting engine effectively.
*   **Strengths:**
    *   Inheriting `account.payment` and `account.move` rather than creating custom financial tables is the correct architectural decision.
    *   `property_fielder.rent.schedule` correctly handles the abstraction between the Tenancy contract and the Accounting Invoices.
    *   `owner.statement` structure with opening/closing balances and `retained_amount` is essential for property management.
*   **Minor Gaps:**
    *   **Statement Logic Source:** In `property_fielder.owner.statement.line`, it links to `account.move.line`. You must explicitly define if this pulls from *Invoices* (Accrual basis) or *Payments* (Cash basis). 99% of UK agents pay landlords on a **Cash Basis** (only once rent is received). The current model allows for both, but the logic needs to be strict to prevent paying out unpaid rent.

### 2. UK Regulatory Accuracy
**Score: Very High**
The PRD demonstrates a strong understanding of specific UK acts.
*   **Tenant Fees Act 2019:** The implementation of late fees (14 days trigger + 3% over BoE) is legally accurate.
*   **Section 13:** The logic for notice periods (1 month vs 6 months) and the tribunal fields are correct.
*   **NRL Scheme:** Withholding 20% tax for non-residents is critical.
*   **CMP:** Ring-fencing Client Account vs Business Account via Journals is the correct Odoo implementation.

### 3. Dependency Chain
**Score: Complete**
*   `depends = ['base', 'account', 'property_fielder_property_leasing']`
*   This is accurate. It correctly isolates accounting logic from the core leasing module while depending on the native `account` module for ledgers.

### 4. Feature Completeness
**Score: Good**
*   **Missing Workflow: Custodial Deposit Transfers.**
    *   The `security.deposit` model allows marking a deposit as "Protected". However, in the UK, if using a **Custodial Scheme** (e.g., DPS Custodial), the money must physically leave the Client Account and go to the Scheme.
    *   *Requirement:* A feature to generate an outbound payment/journal entry when moving funds to a Custodial scheme.
*   **Missing Workflow: Landlord Shortfalls.**
    *   If `maintenance_costs` > `gross_rent`, the statement balance goes negative. The PRD handles `closing_balance` (carry forward), but there is no mechanism to **Invoice the Landlord** if the agent needs an immediate cash injection to pay a contractor.

### 5. Integration Points
*   **Banks:** The BACS export (Standard 18) is a great inclusion.
*   **Odoo Accounting:** The integration is tight. Using `account.move.line` extensions (`is_included_in_statement`) is the best way to prevent double-counting transactions in owner statements.

### 6. Risks & Gaps
*   **The "Paid" vs "Invoiced" Trap:** The code snippet for Owner Statements (`_compute_management_fee`) uses `gross_rent`. It does not explicitly state that `gross_rent` is calculated only from **PAID** invoices.
    *   *Risk:* If the system treats an "Open" invoice as income, the agent might pay the landlord rent that the tenant hasn't actually paid yet. This creates a deficit in the Client Account (breach of CMP regulations).
*   **NRL Reporting:** While you calculate the tax, agents must submit a **quarterly return (Form 42)** to HMRC. The data is there, but a specific report view/export for this is missing.

### 7. Recommendations

1.  **Enforce Cash Basis for Statements:** Modify logic to ensure `owner.statement` only includes income where the related Invoice `payment_state == 'paid'` or links directly to reconciled payments.
2.  **Refine Deposit Workflow:** Add a `scheme_type` field (Custodial vs Insured). If Custodial, trigger a Payment Wizard to move funds out of the Client Account.
3.  **Landlord Refund Request:** Add a feature to creating an Invoice *against* the Landlord if their account balance is negative and funds are needed immediately (rather than just carrying the negative balance forward).
4.  **Consolidate Arrears Logic:** You have a model `property_fielder.arrears` (3.3) and a computed field on Tenancy (4.9). Ensure the stored model (3.3) is updated via cron or action, as computed fields on Tenancy won't support historical reporting or easy filtering for large portfolios.

---

### Final Score

**88% - Minor improvements needed**

The PRD is excellent and highly specific to the domain. It is technically sound regarding Odoo's accounting architecture. Addressing the "Cash Basis" logic explicitly and the Deposit Transfer workflow will make this 100% build-ready.

---

## PROPERTY_ANALYTICS

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_PROPERTY_ANALYTICS.md`

Here is the expert review for the **Property Fielder Property Analytics** PRD.

### 1. Data Model Completeness
**Status: Excellent**
*   **Materialized Views:** The decision to use `_auto = False` with `Materialized Views` is technically astute for this use case. Aggregating compliance data across 10+ tables (certs, tenants, defects, invoices) would be too slow for real-time dashboards on large portfolios.
*   **Indexing:** Explicitly creating the `UNIQUE INDEX` on `property_id` in the `init()` method is a critical detail often missed in PRDs; this enables `REFRESH MATERIALIZED VIEW CONCURRENTLY`, preventing table locks during updates.
*   **Snapshot Model:** The `ComplianceHistorySnapshot` is correctly defined to store calculated values (Float/Boolean) rather than attempting to link back to dynamic data, ensuring historical accuracy.

### 2. UK Regulatory Accuracy
**Status: Exceptional**
*   **Document Existence vs. Data Entry:** The SQL logic checking `ir.attachment` existence (`gas_has_document`) distinguishes this as a professional-grade UK compliance tool. In UK court, a date in a database is not a defense; the certificate file is.
*   **Immigration Act 2014 (Right to Rent):** The logic handles the nuanced "No tenants = Compliant" and "All tenants must be valid" rules correctly.
*   **Housing Act 2004:** Covers Mandatory, Additional, and Selective licensing accurately.
*   **Asbestos:** The logic `build_year >= 2000` correctly aligns with the UK ban on asbestos (1999), negating the need for surveys on modern builds.
*   **Awaab’s Law:** Accurately models the proposed 24h/14d/7d timescales.

### 3. Dependency Chain
**Status: Minor Gap**
*   **Tenant Screening Dependency:** The SQL logic heavily relies on `property_fielder_tenant_rtr`.
    *   *Issue:* The `depends` list includes `property_fielder_property_management` but does not explicitly list the module containing the Tenant Screening/RTR logic (unless it is merged into Management). If RTR is a separate module, the SQL View creation will crash on install if the table `property_fielder_tenant_rtr` does not exist.
*   **Odoo Edition:** `spreadsheet_dashboard` usually implies Odoo Enterprise. If this is for Community, a different dashboarding library (like `board` or external BI) is needed.

### 4. Feature Completeness
**Status: High**
*   **Missing "Section 21 Validity" Metric:** While you calculate general compliance, you are missing a specific boolean for **Eviction Validity**.
    *   *Context:* In the UK, a Section 21 notice is invalid if Gas, EPC, and the "How to Rent" guide were not served, OR if the Deposit is not protected.
    *   *Recommendation:* Add a `section_21_valid` boolean field to the view that checks these specific criteria + Deposit Protection status (assuming deposit data exists in the tenancy module).

### 5. Integration Points
**Status: Strong**
*   **Accounting Fix:** The shift from querying `account.payment` to `account.move` (invoices) to calculate rent received is the correct Odoo architectural approach.
*   **Drill-down:** The integration with standard Odoo window actions for drill-downs is well-defined.

### 6. Risks & Gaps
*   **Hardcoded Scoring Weights:** The compliance score weights (e.g., Gas = 20, Asbestos = 5) are hardcoded in the SQL View.
    *   *Risk:* If a client wants to prioritize Damp & Mould (Awaab's Law) over Asbestos, or if legislation changes, you require a developer to redeploy code.
*   **Refresh Frequency:** The cron is set to `1 hour`. For a database with 50,000+ units and extensive history, a full materialized view refresh might take significant resources.
*   **Rent Schedule Logic:** The SQL uses `SUM(rent_schedule)`. Ensure `rent_schedule` handles pro-rated periods correctly, otherwise "Expected Rent" might misalign with "Invoiced Rent" for partial months.

### 7. Recommendations
1.  **Configurable Weights:** Move the compliance score integers (20, 15, 10, etc.) to `ir.config_parameter` or a settings table, and inject them into the SQL view generation string via Python formatting. This allows functional consultants to tune scores without code deployment.
2.  **Safe SQL Dependency:** Wrap the Right to Rent (RTR) SQL block in a conditional check within Python `_get_sql()`. If the RTR module isn't installed, insert `NULL` or `TRUE` placeholders to prevent the View crash.
3.  **Add "Deposit Protected" Check:** Incorporate deposit protection status into the Financial or Compliance view to complete the Section 21 validity check.
4.  **Smart Refresh:** Change the cron to run nightly (off-peak), and add a button on the Dashboard for "Refresh Now" so users can force an update only when needed during the day.

---

### SCORE: 96%
**Build Ready.**
This is a highly professional PRD. The logic demonstrates deep knowledge of both Odoo's SQL capabilities (Materialized Views, JSON attachment checks) and UK Property Law. With the minor fix regarding the dependency safety and scoring configuration, this is ready for development.

---

## PROPERTY_DOCUMENTS

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_PROPERTY_DOCUMENTS.md`

Here is the expert review for the **Property Fielder Property Documents** Addon PRD.

### Review Summary

This is an exceptionally strong PRD regarding **UK Regulatory Compliance**. The specific logic for "How to Rent" guide versioning, Deed witnessing (tenancies >3 years), and GDPR retention rules for Right to Rent demonstrates deep domain knowledge. The technical architecture correctly navigates the Odoo Community vs. Enterprise `documents` module limitation.

However, the **E-Signature workflow** is slightly under-modeled regarding the *process* of signing (tracking status before completion), and the "Field Write-back" mechanism is technically fragile.

---

### 1. Data Model Completeness
**Score: 85%**
*   **Strengths:** Good use of `ir.attachment` for storage while maintaining metadata in `property_fielder.document`. The distinction between `document` and `document.type` is correct.
*   **Gaps:**
    *   **Signature Workflow:** The `property_fielder.e.signature` model stores the *result* (audit log). There is no explicit mechanism to track the *state* of a signature request per person (e.g., "Sent", "Opened", "Signed", "Rejected"). You need a status field or a `signature.request` line item model to handle multi-party signing progress.
    *   **Redundancy:** `file_size` and `mime_type` on `property_fielder.document` are redundant; they exist on the linked `ir.attachment`. Unless specific indexing is required, use computed fields to read from attachment to avoid sync errors.

### 2. UK Regulatory Accuracy
**Score: 98%**
*   **Strengths:**
    *   **How to Rent Guide:** The version check logic based on tenancy start date vs. publication date is legally critical for Section 21 validity. Excellent inclusion.
    *   **Deeds:** Correctly identifies >3-year leases as Deeds requiring witnesses.
    *   **Service:** The `document.service` model handling "Deemed Served Date" (e.g., +2 working days for post) is vital for possession notices.
*   **Minor Note:** For **Deeds** executed electronically, the witness must be *physically present* with the signer to attest the signature. The UI should strictly warn the user of this requirement when the `is_deed` flag is true, as "remote witnessing" is legally contentious in the UK.

### 3. Dependency Chain
**Score: 90%**
*   **Strengths:** Correctly identifies core Odoo modules and the parent property module.
*   **Correction:** The Technical Notes mention a `pdf_viewer` widget. If this requires a third-party module (like `web_widget_pdf_viewer`), it must be listed in `manifest` depends. If it is custom JS included in *this* module, the PRD is fine.

### 4. Feature Completeness
**Score: 85%**
*   **Missing Feature: "Compliance Packs".** In UK lettings, documents are rarely sent alone. You send a "Move-in Packet" (AST + EPC + GSC + How to Rent + Deposit PI). Sending 5 separate emails/notifications is poor UX and risky compliance-wise. A feature to bundle documents into one "Send for Sign/Acceptance" action is highly recommended.
*   **Missing Feature: Deposit Prescribed Information (PI) Merging.** While AST generation is covered, Deposit PI requires merging data from the Tenancy, Landlord, *and* the specific Deposit Scheme Protection Certificate. This is a complex but required document.

### 5. Integration Points
**Score: 80%**
*   **Risks:** The `updates_property_field` (string) in `document.type` is fragile.
    *   *Issue:* If a developer renames `gas_safety_expiry` to `gas_cert_date` in the core module, this addon breaks silently.
    *   *Fix:* Use `fields.Selection` or `ir.model.fields` reference to ensure the field exists at the code/database level.

### 6. Risks & Gaps
*   **Risk (Fragility):** As noted above, the string-based field mapping for compliance updates.
*   **Gap (Signature Status):** If a tenant claims they never received the signing link, the current model tracks the "Send" but not the "View" (tracking pixel/log) before the signature is applied.

### 7. Recommendations

1.  **Harden Field Mapping:** Change `updates_property_field` on `document.type` to use a **Many2one to `ir.model.fields`** (filtered by property model). This ensures the field actually exists and provides a dropdown selection for Admins.
2.  **Enhance Signature Tracking:** Add a `state` field to the `property_fielder.e.signature` model (Draft, Sent, Viewed, Signed) to allow the Property Manager to see *who* is holding up the process in a multi-tenant AST.
3.  **Add "Document Packets":** Create a transient model to select multiple documents and send them in a single envelope/email context.
4.  **Deed Witness Warning:** Add a UI banner for `is_deed` documents: *"Warning: Witness must be physically present. Remote witnessing is not valid for Deeds."*
5.  **Refine Dependencies:** Explicitly state if the PDF viewer is a custom JS asset within this module or an external dependency.

---

### Final Score: 88% (Minor Improvements Needed)

**Verdict:** The regulatory logic is production-grade. The data model needs a slight tweak for robust signature workflow tracking, and the integration mapping needs to be made safer for a build-ready status.

---

## PROPERTY_LEASING

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_PROPERTY_LEASING.md`

Here is the expert review for the `property_fielder_property_leasing` Addon PRD.

### Review Summary
This is a high-quality, technically detailed PRD. It moves beyond high-level requirements into actual implementation logic (Python/XML), significantly reducing development ambiguity. The inclusion of specific UK regulatory logic (Tenant Fees Act, S21 validity, Overcrowding) is excellent.

However, there are minor gaps regarding the *accounting treatment* of deposits (Balance Sheet vs. P&L) and the practical handling of "Periodic" rent schedule extensions.

---

### 1. Data Model Completeness
**Status: Strong, but specific accounting links missing.**
*   **Strengths:** The `Tenancy` model is robust. Using `Monetary` fields correctly, M2M for tenants, and proper document tracking structure.
*   **Gaps:**
    *   **Deposit Accounting:** You track the `deposit_amount`, but not the **Liability Account** where this money sits on the Balance Sheet. When a deposit is received, it is not Income; it is a Liability.
    *   **Meter Readings:** No model for Start/End meter readings (Gas/Elec/Water). This is a critical part of the Leasing lifecycle (Inventory/Check-in).
    *   **Payment Method:** No field to differentiate between Standing Order (Tenant initiated) vs. Direct Debit (System initiated).

### 2. UK Regulatory Accuracy
**Status: Excellent.**
*   **Strengths:**
    *   **Tenant Fees Act:** The 5/6 week cap logic is correctly implemented.
    *   **Section 21:** The blocking logic based on Deregulation Act 2015 requirements (EPC, Gas, How to Rent) is spot on.
    *   **Overcrowding:** Implementing the Housing Act 1985 room standard (Child <10 = 0.5) is a sophisticated touch.
*   **Verification:** The holding deposit deadline (15 days) is accurate.

### 3. Dependency Chain
**Status: Accurate.**
*   `account`: Essential for invoicing.
*   `property_fielder_property_management`: Core parent.
*   `tenant_screening`: Correctly separated.
*   **Note:** Ensure `account` configuration (Tax settings, Fiscal Positions) is handled in the Property Management setup, as this module relies on them for the Cron job.

### 4. Feature Completeness
**Status: Good, with one logic gap in Periodic Tenancies.**
*   **The Periodic Gap:**
    *   The `action_generate_rent_schedule` code limits generation to `end_date` or `+ 1 year`.
    *   **Issue:** If a tenancy goes Periodic (rolling), the system needs to *continuously* generate rent schedules indefinitely. The current logic will stop invoicing after 1 year unless the user manually clicks "Generate Schedule" again.
*   **Missing:**
    *   **Surrender/Early Termination:** Logic to calculate pro-rata rent refunds if a tenant leaves mid-month.
    *   **Inventory Check-in/out:** You have a document attachment, but no structural data for the actual inventory report (Condition ratings). *Acceptable to keep as PDF attachment for Phase A, but worth noting.*

### 5. Integration Points
**Status: Clear.**
*   **Accounting:** Integration is tight via `account.move`.
*   **Documents:** Uses standard `ir.attachment`.
*   **Mail:** Uses `mail.thread` for audit.

### 6. Risks & Gaps
*   **Risk (Cron Failure):** The Cron job performs `invoice.action_post()`. If the Tenant (Partner) lacks a configured address or VAT ID logic fails, the Cron will crash and roll back, potentially halting *all* rent invoices for that day.
    *   *Mitigation:* The Cron loop needs `try/except` blocks to log errors for specific tenancies without stopping the whole batch.
*   **Risk (Deposit Deductions):** The PRD tracks `deductions` as a Monetary amount.
    *   *Gap:* How is this processed in Accounting? If £100 is deducted for cleaning, the system needs to move £100 from the Deposit Liability Account to an Income/Expense account. This mechanism is undefined.

### 7. Recommendations

1.  **Fix Periodic Schedule Logic:** Modify `_cron_generate_rent_invoices`. If the tenancy is `periodic` and no schedule exists for the target date, the Cron should **create** the schedule record on the fly before creating the invoice.
2.  **Add Deposit Accounting Fields:** Add `deposit_liability_account_id` to the Property or Company settings to ensure the deposit is booked correctly on the Balance Sheet.
3.  **Hardening the Cron Job:**
    ```python
    # Pseudo-code recommendation
    for schedule in schedules:
        try:
            # ... creation logic ...
            invoice.action_post()
            self.env.cr.commit() # Commit success per invoice
        except Exception as e:
            self.env.cr.rollback()
            # Log failure to Chatter on the Tenancy
            schedule.tenancy_id.message_post(body=f"Invoice generation failed: {str(e)}")
    ```
4.  **Add Meter Readings Model:** Create a simple `property.meter.reading` model linked to the Tenancy for Check-in/Check-out readings.
5.  **Refine Deposit Deductions:** Add a button on the Deposit record "Process Return" that opens a Wizard to allocate the return: Amount to Tenant (Payment) vs. Amount to Landlord (Income Invoice/Journal).

---

### SCORE: 92% (Build Ready)

**Verdict:** This is an exceptionally well-defined PRD for Phase A. The code snippets provided demonstrate a clear understanding of Odoo mechanics. With the inclusion of the "Safe Error Handling" in the Cron job and the "Deposit Accounting" fix, this is ready for immediate development.

---

## PROPERTY_MAINTENANCE

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_PROPERTY_MAINTENANCE.md`

Here is the expert review of the **Property Fielder Property Maintenance** Addon PRD.

### Review Summary
This is an exceptionally strong PRD that demonstrates a deep understanding of both Odoo architecture and UK housing compliance (specifically Awaab’s Law and CDM 2015). The data models are robust, the compliance logic is baked into the workflow rather than added as an afterthought, and the accounting integration for recharging is well-defined.

The primary gap is the technical mechanism for external Contractor interaction (non-Odoo users) and a missing dependency for the portal features.

---

### 1. Data Model Completeness
**Score: High**
The models are well-structured and leverage standard Odoo inheritance (`mail.thread`) correctly.
*   **Strengths:**
    *   **`work.order` vs `job`:** Separating the commercial container (`work.order`) from the physical visits (`job`) is excellent architectural design. It solves the common problem of "one quote, three visits" (investigation, fix, follow-up).
    *   **`access.attempt`:** This is a critical standalone model required for legal defense under Awaab's Law.
*   **Corrections Needed:**
    *   **`maintenance.request`:** Needs a `source` selection field (Portal, Email, Phone, Walk-in) to track channel shift.
    *   **`property_fielder.asset`:** Ensure this does not conflict with Odoo’s native `account.asset`. I recommend renaming the technical model to `property_fielder.maintenance_asset` to avoid namespace collisions if the Accounting module is fully installed.

### 2. UK Regulatory Accuracy
**Score: Excellent**
This is the strongest section of the PRD.
*   **Awaab’s Law:** The implementation of specific SLA timers (`investigation_date` vs `remedy_target_date`) and the forced logging of access attempts is spot on.
*   **CDM 2015:** The `cdm_risk_info_shared` checkbox as a constraint before the `in_progress` state is a perfect "compliance gatekeeper."
*   **Contractor Vetting:** The computed compliance check based on insurance expiry is vital for property managers to avoid liability.

### 3. Dependency Chain
**Score: Medium**
There is a specific oversight in the dependency list regarding the web features.
*   **Missing Dependencies:**
    *   `portal`: Essential for the Tenant Portal features described in Section 8.
    *   `website`: Often required if using web controllers and public routes.
    *   `product`: Implicitly required for `work.order.line`, usually pulled by `account`, but safer to list if you are defining product relationships.

### 4. Feature Completeness
**Score: High**
*   **Missing Feature: Landlord Approval UX:**
    *   The PRD describes `action_request_landlord_authorization` sending an email.
    *   **Gap:** How does the landlord approve? If they reply to the email, a user must manually click "Approve" in Odoo.
    *   **Recommendation:** Add a feature for "Tokenized Approval." The email should contain a unique link allowing the landlord to approve via a simple web page without logging in.
*   **Missing Feature: Contractor Interaction:**
    *   The PRD mentions `actual_start (mobile sync)` and uploading photos.
    *   **Gap:** Unless Contractors are full Odoo users (expensive), how do they do this?
    *   **Recommendation:** Explicitly define if this requires the Odoo Mobile App (User) or a "Contractor Portal" (Portal User) view similar to the Tenant Portal.

### 5. Integration Points
**Score: Good**
*   **Accounting:** The logic for `action_create_tenant_invoice` is sound.
*   **Tenancy:** correctly links to the *active* tenancy.
*   **Defects:** The PRD notes the integration is optional, which is good design for modularity.

### 6. Risks & Gaps
1.  **Contractor Licensing/UX:** If you expect contractors to log GPS coords and Start/Stop times, they need an interface. If they are not System Users, you need to build a Portal View for `property_fielder.job`. The PRD defines a Tenant Portal but implies a Contractor interface without specifying it.
2.  **Notification Fatigue:** The "Planned Maintenance" cron job generates requests. If a property has 20 assets, the Property Manager might get flooded. *Mitigation:* Grouping logic or a "Review Planned Maintenance" wizard.

### 7. Recommendations

1.  **Update Dependencies:** Add `'portal'` and `'website'` to the manifest.
2.  **Define Contractor Portal:** Add a section in "Portal Specifications" specifically for Contractors to view Jobs, click "Start Job" (for GPS capture), and upload photos.
3.  **Tokenized Landlord Auth:** Update the Landlord Authorization workflow to support "Click to Approve" via email link (using `_generate_access_token`).
4.  **Asset Model Rename:** Rename `property_fielder.asset` to `property_fielder.maintenance_asset` to ensure clear separation from Financial Assets.
5.  **Add `origin` Field:** Add an `origin` or `source` field to `maintenance.request` to track how the request came in.

---

### SCORE: 92% (Build Ready)

**Verdict:** This is a high-quality, professional PRD. The regulatory logic is production-ready. With the addition of `portal` to the dependencies and a clarification on how Contractors interface with the system (Portal vs User), this is ready for immediate development.

---

## PROPERTY_MARKETING

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_PROPERTY_MARKETING.md`

Here is the expert review for the `property_fielder_property_marketing` Addon PRD.

### 1. Data Model Completeness
**Score: High**
The data models are well-structured and leverage standard Odoo inheritance effectively.
*   **Strengths:** Using `crm.lead` for enquiries and `calendar.event` for viewings is the correct architectural choice, avoiding data silos. The `listing.image` model correctly handles ordering and captioning.
*   **Gap:** The `property_fielder.listing` model links to `res.currency`, but `rent_amount` and `deposit_amount` fields in the definition do not explicitly show the `currency_field='currency_id'` attribute in the table (though implied).
*   **Gap:** `property_fielder.listing.portal` tracks the state of the *listing* on the portal, but it lacks a field to store the **raw request/response payload** (e.g., `last_request_body`, `last_response_body`). This is critical for debugging XML/BLM feed errors.

### 2. UK Regulatory Accuracy
**Score: Excellent**
This PRD demonstrates a deep understanding of current UK legislation.
*   **Tenant Fees Act 2019:** The deposit cap logic (5 vs 6 weeks based on £50k rent) is implemented correctly. The fix to exclude sales listings is crucial.
*   **NTSELAT (Trading Standards):** The inclusion of Material Information Parts A, B, and C is impressive and often overlooked.
*   **Advertising Standards:** The "Display Address" vs "Exact Address" logic satisfies privacy needs while meeting portal requirements to locate the property on a map radius.
*   **GDPR:** Not explicitly detailed, but implied via standard Odoo security groups.

### 3. Dependency Chain
**Score: Good**
*   **Internal:** `base`, `mail`, `crm`, `calendar`, `website`, `property_fielder_property_management` are correct.
*   **External:** `paramiko` is listed.
*   **Missing:** The Zoopla integration uses `requests` and `lxml`. While `lxml` is core Odoo, `requests` should be listed in `external_dependencies` to be safe, or confirmed as standard in the Odoo environment (it usually is, but good practice to list).

### 4. Feature Completeness
**Score: High (with specific gaps)**
*   **Missing - Feed Validation:** Before generating the BLM/XML, there should be a `_validate_listing_completeness()` method that runs sanity checks (e.g., "Does it have at least 1 photo?", "Is the description too short?", "Is the summary too long?"). Portals will reject feeds silently or block the account if data is malformed.
*   **Missing - Branch Management:** UK agents often have multiple branches. Rightmove/Zoopla require a specific `branch_id` per feed. The PRD assumes one `company_id.zpg_branch_ref`. If the Odoo instance supports Multi-Branch (via Operating Units or Multi-Company), the settings need to be company-specific.
*   **Missing - Website Frontend:** The PRD mentions `website.published.mixin` but does not define the **Controller** logic (`/properties/<id>`) or the **QWeb Template** structure for the public-facing Odoo website page.

### 5. Integration Points
*   **CRM:** The "Match Leads" feature is excellent.
*   **Property Management:** Strong link.
*   **Compliance:** The system checks `material_info_complete`, but it should arguably verify **Safety Certificates** (Gas/EICR) from the base `property_fielder_property_management` module before allowing the state to move to `active`.

### 6. Risks & Gaps
*   **BLM Format Rigidity:** Rightmove's BLM format is archaic and extremely strict about headers, EOF markers, and date formats. The PRD snippet is pseudo-code; the actual implementation requires a robust `.blm` generator library.
*   **Image Processing Load:** Even with async cron, resizing hundreds of high-res photos (common in initial migration) can choke the Odoo `filestore`. Ensure the `ir.attachment` storage strategy is considered (e.g., S3).
*   **Real-time Removal:** The Cron jobs run periodically. If a property is let, it needs to be removed from portals *immediately* to avoid "Ghost Listing" complaints (Trading Standards issue). A "Force Update/Remove" button is needed on the listing.

### 7. Recommendations
1.  **Add `feed_log` field:** To `listing.portal` to store XML/BLM snippets for debugging.
2.  **Hard Block on Safety Certs:** Add a constraint that prevents `state='active'` if the linked `property_id` has expired Gas Safety or EICR certificates.
3.  **Define Website Controller:** Briefly scope the `/properties` route and list view/detail view templates.
4.  **Refine Branch Config:** Move `zpg_branch_ref` and Rightmove credentials to a `res.config.settings` view that is explicitly Company-dependent.
5.  **Force Removal Action:** Add a button `action_withdraw_from_portals()` that triggers an immediate API call/file generation rather than waiting for Cron.

---

### SCORE: 92%
**Build Ready.**
This is an exceptionally high-quality PRD. The regulatory logic is solid, and the data model is efficient. The recommendations above are primarily regarding operational robustness (debugging feeds and multi-branch setups) rather than core architectural flaws. Proceed to build.

---

## TENANT_PORTAL

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_TENANT_PORTAL.md`

Here is the expert review of the **Property Fielder Tenant Portal** PRD.

### 1. Data Model Completeness
**Status: Generally Good, Minor Clarifications Needed**
*   **Model Extensions:** The extensions to `maintenance.request` and `res.partner` are well defined.
*   **Missing Definition:** The PRD mentions a `property_fielder.document` model in the `upload_document` controller (Section 5.4), but the definition of this model or its extension is not in Section 4 (Data Models). It implies a dependency on `property_fielder_property_documents`, but the link needs to be explicit regarding permissions.
*   **Field Types:** Correct Odoo field types used (`Selection`, `Text`, `Many2many`).

### 2. UK Regulatory Accuracy
**Status: Excellent**
*   **Section 48 (Address for Service):** The logic to default to the Agent's address and fall back to the Company address is legally sound for managing agents in England/Wales.
*   **Awaab’s Law:** Highlighting Damp/Mould as a specific trigger with visible SLAs is a critical, forward-thinking compliance feature.
*   **Document Access:** The distinction between Landlord ID (Hidden/GDPR) and Statutory Docs (Gas, EICR - Visible) is accurate.
*   **Section 21:** Visual indicators for "Documents Served" is a vital compliance check for the tenant (and protects the landlord by proving availability).

### 3. Dependency Chain
**Status: Implementation Logic Gap (JavaScript)**
*   **Python:** `account` and `mail` dependencies are correctly identified.
*   **JavaScript (HEIC):** The PRD lists `heic2any` in `package.json`.
    *   *Critique:* Odoo modules do not automatically install NPM packages from a `package.json` file inside the addon directory unless you are using a specific build pipeline (like Odoo.sh with a root package.json or a custom Dockerfile).
    *   *Fix:* You must either bundle the minified JS library in `/static/src/lib/` or reference a CDN in the XML assets, rather than relying on `npm install`.

### 4. Feature Completeness
**Status: Strong Core, Missing Renewals**
*   **Included:** Maintenance, Docs, Payments, Onboarding, Notices.
*   **Missing:**
    *   **Renewals:** No workflow for tenants to request a renewal or view a renewal offer.
    *   **Deposit Disputes:** While the deposit details are there, there is no mechanism to view end-of-tenancy deductions or dispute them.
    *   **Portal Menu Hook:** The PRD details the controllers (`/my/tenancy`) but misses the XML inheritance for `portal.portal_my_home` to add the "Tenancy" card to the main Odoo portal menu.

### 5. Integration Points
**Status: Solid**
*   **Mail:** Leveraging `mail.thread` prevents data silos.
*   **Accounting:** The read-only logic for `account.move` prevents the need for complex payment gateway logic in Phase A, while still showing arrears.
*   **Maintenance:** The mapping of portal fields (`access_arrangements`) to the backend maintenance request is clear.

### 6. Risks & Gaps
**Major Contradiction Detected (HEIC Handling):**
*   **Section 5.3** describes a **Client-Side** conversion using `heic2any` (JavaScript).
*   **Section 11.3** describes a **Server-Side** conversion using `pillow-heif` (Python).
*   **Risk:** Do not do Server-Side conversion for uploads if possible; it consumes heavy RAM/CPU. Stick to the Client-Side approach in 5.3 and remove 11.3.

**Security Risk (File Upload):**
*   **Section 5.4 (`upload_document`):** The controller uses `.sudo().create()`.
    *   While you check `if user not in tenant_ids`, you must explicitly validate **MIME types** before saving. Relying only on the file extension is unsafe. Prevent execution of scripts (e.g., .exe, .py, .php) masked as documents.

### 7. Recommendations

1.  **Resolve HEIC Conflict:** Remove Section 11.3 (Server-side). Stick to Client-side (Section 5.3) for performance.
2.  **Fix JS Asset Strategy:** Change the `heic2any` implementation to download the library into `static/src/lib/` and load it via `web.assets_frontend`, rather than relying on `package.json`.
3.  **Add Portal Home XML:** Explicitly define the `portal_my_home` template inheritance to generate the menu tile.
4.  **Security Hardening:** Add a `_validate_file` method to the upload controller to whitelist MIME types (PDF, JPG, PNG) before `sudo()` creation.
5.  **Renewal Scope:** Explicitly mark "Lease Renewals" as "Out of Scope" for Phase A to avoid scope creep, or add a simple "Request Renewal" button.

---

### SCORE: 88%
**Status: 76-90% - Minor improvements needed**

**Summary:** This is a high-quality PRD with excellent attention to UK compliance (Section 48, Awaab's Law). The logic is sound. It requires only minor technical adjustments regarding JavaScript asset management and resolving the HEIC handling contradiction before coding begins.

---

## TENANT_SCREENING

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_TENANT_SCREENING.md`

Here is the expert review of the **Property Fielder Tenant Screening** Addon PRD.

### 1. Data Model Completeness
**Status:** ✅ **Strong**
The data models are well-structured and leverage standard Odoo inheritance (`mail.thread`, `portal.mixin`) effectively.
*   **Strengths:** The `address.history` constraint for 3 years is excellent. Storing API payloads (`request_payload`, `response_payload`) is a best practice for debugging third-party credit checks.
*   **Minor Gap:** The `property_fielder.reference` model lacks a `token` or `access_token` field. If you intend to send emails to referees to fill out forms online (without them being portal users), you need a unique, secure token for the URL.

### 2. UK Regulatory Accuracy
**Status:** ⚠️ **Good, but one Critical Gap**
You have nailed the **Tenant Fees Act 2019** (Holding Deposit caps, 15-day deadlines, refund logic) and the **Deregulation Act 2015** (How to Rent guide).
*   **Critical Gap (Right to Rent):** In the UK, Right to Rent checks must be performed on **all adult occupiers**, not just the named tenants.
    *   *Correction:* You need a mechanism to list "Permitted Occupiers" (adults not on the lease) on the Application and perform `property_fielder.right.to.rent` checks on them as well. Currently, the model only links RTR to `tenant_id` (the applicant).
*   **Deposit Cap:** While you check the *Holding* deposit, the Tenant Fees Act also caps the *Security* Deposit (5 weeks' rent if under £50k/yr). The `action_convert_to_tenancy` copies `deposit_amount` from the property, but there should be a validation warning at the Application stage if the agreed rent changes the deposit cap calculation.

### 3. Dependency Chain
**Status:** ✅ **Correct**
*   Dependencies on `account` (for deposits), `website` (for forms), and `mail` are correctly identified.
*   The inheritance from `property_fielder_property_management` is logical.

### 4. Feature Completeness
**Status:** 📝 **Minor Additions Needed**
*   **Referee Interface:** The PRD mentions "Email/portal collection" for references. To be build-ready, you need to define the **Controller** logic. How does a generic landlord (referee) submit the reference? They won't be Odoo users.
    *   *Requirement:* A web controller `route='/reference/submit/<token>'` and a corresponding QWeb view.
*   **Credit Check Provider:** The PRD is provider-agnostic. For a V1, you should define an abstract method in the `credit.check` model (e.g., `_request_credit_score()`) so developers know this is a stub for future integration (Equifax/Experian/Canopy), or specify a mock provider for testing.

### 5. Integration Points
**Status:** ✅ **Solid**
*   **Tenancy Conversion:** The `action_convert_to_tenancy` logic handling Groups vs. Individual applicants is robust.
*   **Accounting:** Linking `holding_deposit_payment_id` provides the necessary audit trail for Client Money Protection (CMP) schemes.

### 6. Risks & Gaps
*   **GDPR / Data Retention:** You have consent fields, but you need a scheduled action to **anonymize or delete** rejected applications after a set period (usually 6-12 months) to comply with GDPR "Right to be Forgotten" and data minimization principles.
*   **Permitted Occupiers:** As noted in section 2, failing to check occupiers puts the landlord at risk of a fine under the Immigration Act 2014.

### 7. Recommendations
1.  **Add `permitted_occupier_ids` One2many** to `tenant.application` (Name, DoB, RTR check link) to handle adults not on the tenancy.
2.  **Add `access_token`** to `property_fielder.reference` for secure external form submission.
3.  **Define a Cron Job for Data Cleanup:** `ir.cron` to delete/anonymize applications >1 year old (GDPR).
4.  **Add Security Deposit Validation:** In `_compute_affordability` or a constraint, ensure `deposit_amount` <= (Rent * 12 / 52 * 5).

---

### SCORE: 88%
**Minor improvements needed.**
The PRD is high quality and clearly written by someone who understands Odoo. It is "Code Ready" for 90% of the features, but the **Right to Rent compliance for Occupiers** is a legal requirement that must be added before build to avoid liability.

**Verdict:** Proceed to build after adding "Permitted Occupiers" logic.

---

## UTILITIES_MANAGEMENT

**Path:** `E:\dev\RoutingScheduling\property_fielder\docs\addons\property_management\PRD_UTILITIES_MANAGEMENT.md`

Here is the expert review for the `property_fielder_utilities_management` Addon PRD.

### 1. Data Model Completeness
**Score: High**
The data models are robust and adhere to Odoo best practices.
*   **Separation of Concerns:** Splitting `meter.reading` (regular events) from `meter.exchange` (hardware changes) is excellent design; it prevents data corruption in usage calculations.
*   **Council Tax Separation:** Moving Council Tax to its own model (Section 3.5/6.1) rather than treating it as a standard utility is the correct architectural choice given it has no "usage" metric.
*   **Linkages:** Correct use of `res.partner` for suppliers and `account.move` for financial transactions.
*   **Discrepancy Note:** You have defined Council Tax twice. Section 3.5 names the model `property_fielder.council.tax` (Class `CouncilTax`), while Section 6.1 names it `property_fielder.council_tax` (Class `CouncilTaxAccount`). **Consolidate these into one definition.**

### 2. UK Regulatory Accuracy
**Score: Excellent**
This PRD demonstrates a deep understanding of UK specificities.
*   **Ofgem Maximum Resale Price:** The inclusion of validation logic (Section 5.1) to ensure the landlord does not profit from utility resale is legally critical.
*   **Gas Conversion:** The explicit formula for converting m³ to kWh using the Volume Correction Factor (1.02264) and Calorific Value is accurate for UK gas billing.
*   **Council Tax:** Handling "Hierarchy of Liability" (HMO Landlord liability) and "Empty Homes Premium" is accurate.
*   **VAT:** Integration with `account.tax` allows for the correct application of the 5% VAT rate for residential fuel (de minimis) vs 20% standard, provided the user configures the taxes correctly.

### 3. Dependency Chain
**Score: Good**
*   `depends = ['base', 'mail', 'property_fielder_property_management', 'account']` is correct.
*   **Suggestion:** Ensure `property_fielder_property_management` exposes the `total_rooms` field on the property model, as the recharge logic depends heavily on property capacity.

### 4. Feature Completeness
**Score: Very Good**
*   **Included:** Recharging, Void Management, Rollover logic, and Bill Variance analysis are all sophisticated features.
*   **Missing - Broadband Handling:** Broadband is listed in `utility_type`, but the `meter.reading` logic assumes a numerical usage counter. Broadband is usually a flat rate. The system needs to suppress "Missing Reading" alerts for Broadband/Internet types.
*   **Missing - Bulk Entry:** For an HMO portfolio, entering readings one by one is slow. A "Mass Entry" wizard or Editable List view for readings across properties would be a high-value Phase 2 feature.

### 5. Integration Points
**Score: Strong**
*   **Accounting:** The flow from `utility.bill` (vendor bill) $\to$ `recharge calculation` $\to$ `account.move` (customer invoice) is logically sound.
*   **Property:** The integration with Tenancies for proration based on move-in/out dates is well logic-checked.

### 6. Risks & Gaps
*   **Data Inconsistency (Council Tax):** As noted in Section 1, the conflicting class definitions in 3.5 and 6.1 will cause a build error.
*   **Negative Usage Validation:** The code sets `units_used = 0` if the calculation is negative (Section 7). This is risky. If a reading is lower than previous (and not a rollover), it is likely a data entry error. It should raise a `ValidationError` rather than silently suppressing it to 0.
*   **Estimated Bills:** The system calculates variance against "Expected Units". If the supplier sends an *Estimated* bill, the system should flag this specifically, as it shouldn't be recharged to tenants without a manual check.

### 7. Recommendations
1.  **Consolidate Council Tax:** Delete Section 6.1 and merge its fields (student exemption, dates) into Section 3.5 to ensure a single model definition.
2.  **Broadband Logic:** In `_compute_expected_units` and validation logic, add `if rec.utility_type == 'broadband': return/skip`.
3.  **Strict Validation:** Change the negative usage logic. If `current < previous` and `!is_rollover`, raise a user error: *"Current reading is lower than previous reading. Please check for data entry error or mark as Rollover."*
4.  **Tax Defaults:** In `utility.account`, add a field `default_tax_id` (Many2one `account.tax`) to auto-populate the VAT rate (5% or 20%) when creating new bills.
5.  **Smart Buttons:** Explicitly add a `action_view_bills` smart button on the `utility.account` form view for better UX.

---

### Final Score

**94% - Build Ready**

*This PRD is exceptionally high quality. The logic provided for UK-specific calculations (Gas conversion and Recharging limits) significantly reduces developer interpretation risk. Once the Council Tax model duplication is resolved, this is ready for immediate development.*

---

