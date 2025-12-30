# PRD: Property Fielder HHSRS

**Addon Name:** `property_fielder_hhsrs`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Domain (Layer 3)  
**Phase:** Phase 4 (HHSRS, DHS & Awaab's Law)  
**Effort:** 25 days  

---

## 1. Overview

HHSRS (Housing Health and Safety Rating System), Decent Homes Standard, and Awaab's Law compliance for UK social housing.

### 1.1 Purpose
Enable assessment and tracking of all 29 HHSRS hazard categories with proper scoring, categorization, and legally mandated response deadlines.

### 1.2 Target Users
- Housing Officers
- Compliance Managers
- Environmental Health Officers
- Social Housing Providers

### 1.3 Business Value
- Legal compliance with Housing Act 2004
- Awaab's Law deadline enforcement
- Decent Homes Standard tracking
- HHSRS category scoring

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for audit trail (critical for Awaab's Law)
    'web',  # For PDF report generation
    'property_fielder_defects',
    'property_fielder_templates',
    'property_fielder_property_management',  # For property_id
    'property_fielder_maintenance',  # For maintenance.request linkage
]
```

---

## 3. Data Models

### 3.1 `property_fielder.hhsrs.hazard.type`
29 HHSRS hazard categories (reference data).

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Hazard name |
| `code` | Char | Hazard code (A1-D4) |
| `group` | Selection | physiological/psychological/protection/infection |
| `description` | Text | Full description |
| `assessment_guide` | Text | How to assess |
| `typical_remedies` | Text | Common remedies |
| `is_awaab_covered` | Boolean | Covered by Awaab's Law |

### 3.2 HHSRS Hazard Categories (29)

| Group | Hazards |
|-------|---------|
| **A. Physiological (11)** | Damp & Mould, Excess Cold, Excess Heat, Asbestos, CO/Fuel Combustion, Lead, Radiation, Uncombusted Fuel Gas, VOCs, Crowding, Entry by Intruders |
| **B. Psychological (2)** | Lighting, Noise |
| **C. Protection (9)** | Falls: Baths, Falls: Level, Falls: Stairs, Falls: Between Levels, Electrical, Fire, Hot Surfaces, Collision/Entrapment, Explosions |
| **D. Infection (7)** | Domestic Hygiene, Food Safety, Personal Hygiene, Water Supply, Refuse, Pests, Sanitation |

### 3.3 `property_fielder.hhsrs.likelihood.band`
Official 16 HHSRS Likelihood Bands with Representative Scale Points (RSP).

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Band name (e.g., "1 in 18") |
| `code` | Char | Band code (L1-L16) |
| `ratio` | Char | Ratio description |
| `rsp` | Float | Representative Scale Point (for calculation) |
| `sequence` | Integer | Display order |

#### Official 16 Likelihood Bands (Reference Data)

| Band | Ratio | RSP | Description |
|------|-------|-----|-------------|
| L1 | 1 in 1 | 1.0 | Certain |
| L2 | 1 in 2 | 0.5 | Very high |
| L3 | 1 in 3 | 0.33 | High |
| L4 | 1 in 6 | 0.167 | Moderately high |
| L5 | 1 in 10 | 0.1 | Moderate |
| L6 | 1 in 18 | 0.056 | Moderately low |
| L7 | 1 in 32 | 0.031 | Low |
| L8 | 1 in 56 | 0.018 | Very low |
| L9 | 1 in 100 | 0.01 | Remote |
| L10 | 1 in 180 | 0.0056 | Very remote |
| L11 | 1 in 320 | 0.0031 | Extremely remote |
| L12 | 1 in 560 | 0.0018 | Negligible |
| L13 | 1 in 1,000 | 0.001 | Very negligible |
| L14 | 1 in 1,800 | 0.00056 | Almost negligible |
| L15 | 1 in 3,200 | 0.00031 | Practically negligible |
| L16 | < 1 in 32,000 | 0.00003 | Infinitesimal |

### 3.4 `property_fielder.hhsrs.assessment`
HHSRS Assessment record (snapshot in time, linked to defect).

| Field | Type | Description |
|-------|------|-------------|
| `defect_id` | Many2one → defect | Related defect |
| `assessment_date` | Date | Date of assessment |
| `assessor_id` | Many2one → res.users | Assessor |
| `hhsrs_hazard_type_id` | Many2one → hazard.type | Hazard category |
| `likelihood_band_id` | Many2one → likelihood.band | **16-band likelihood** |
| `outcome_prob_class_1` | Float | % probability of Class I outcome |
| `outcome_prob_class_2` | Float | % probability of Class II outcome |
| `outcome_prob_class_3` | Float | % probability of Class III outcome |
| `outcome_prob_class_4` | Float | % probability of Class IV outcome |
| `hhsrs_score` | Float | Computed: Hazard score |
| `hhsrs_band` | Selection | Computed: A/B/C/D/E/F/G/H/I/J |
| `hhsrs_category` | Selection | Computed: 1 (Cat 1) / 2 (Cat 2) |
| `likelihood_justification` | Text | Why this likelihood was chosen (tracking=True) |
| `outcome_justification` | Text | Why this outcome was chosen (tracking=True) |
| `vulnerable_occupant` | Boolean | Vulnerable person present |
| `vulnerable_type` | Selection | elderly/child/disabled/pregnant |
| `is_emergency` | Boolean | Emergency response required |
| `state` | Selection | draft/confirmed/superseded |
| `notes` | Text | Assessment notes |

### 3.5 Defect Model Extension

Extends `property_fielder.defect` with HHSRS fields.

| Field | Type | Description |
|-------|------|-------------|
| `hhsrs_assessment_ids` | One2many → hhsrs.assessment | **Assessment history** |
| `current_hhsrs_band` | Selection | Computed: Current band from latest assessment |
| `current_hhsrs_category` | Selection | Computed: Current category |
| `current_hhsrs_score` | Float | Computed: Current score |
| `awaab_deadline_id` | Many2one → awaab.deadline | Awaab's Law deadline |

### 3.6 `property_fielder.damp.mould`
Damp and mould tracking (Awaab's Law focus).

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `reported_date` | Date | First reported |
| `reported_by` | Many2one → res.partner | Who reported |
| `location` | Char | Location (room, wall) |
| `severity` | Selection | minor/moderate/severe |
| `cause` | Selection | condensation/penetrating/rising |
| `cause_identified` | Boolean | Root cause found |
| `cause_date` | Date | When identified |
| `state` | Selection | reported/investigating/repairs_started/resolved |
| `is_uninhabitable` | Boolean | Property uninhabitable (decanting required) |
| `decant_required` | Boolean | Tenant needs temporary accommodation |
| `decant_arranged` | Boolean | Decant accommodation arranged |
| `decant_property_id` | Many2one → property | Temporary accommodation |
| `decant_date_start` | Date | **Decant start date (for rent adjustments)** |
| `decant_date_end` | Date | **Decant end date** |
| `defect_id` | Many2one → defect | Linked defect |
| `maintenance_request_id` | Many2one → maintenance.request | **Linked maintenance request** |
| `awaab_compliant` | Boolean | Meeting Awaab deadlines |
| `photo_ids` | Many2many → ir.attachment | **Evidence photos (standard Odoo)** |
| `timeline_ids` | One2many → damp.mould.timeline | Event timeline |

### 3.7 `property_fielder.damp.mould.timeline`
Timeline events for damp/mould cases.

| Field | Type | Description |
|-------|------|-------------|
| `damp_mould_id` | Many2one → damp.mould | Parent record |
| `date` | Datetime | Event date/time |
| `event_type` | Selection | reported/investigated/repairs_started/completed/tenant_contact |
| `description` | Text | Event description |
| `user_id` | Many2one → res.users | User who logged event |
| `photo_ids` | Many2many → ir.attachment | Photos for this event |

### 3.5 `property_fielder.awaab.deadline`
Awaab's Law deadline tracking.

| Field | Type | Description |
|-------|------|-------------|
| `defect_id` | Many2one → defect | Related defect |
| `hazard_type` | Selection | emergency/non_emergency/damp_mould |
| `investigation_deadline` | Date | Investigation must start |
| `investigation_met` | Boolean | Met deadline |
| `repairs_start_deadline` | Date | Repairs must start |
| `repairs_start_met` | Boolean | Met deadline |
| `completion_deadline` | Date | Must complete |
| `completion_met` | Boolean | Met deadline |
| `state` | Selection | pending/in_progress/overdue/completed |
| `breach_count` | Integer | Number of deadline breaches |
| `tenant_notified_investigation` | Boolean | **Tenant notified of investigation** |
| `tenant_notified_schedule` | Boolean | **Tenant notified of repair schedule** |
| `access_refused_dates` | Text | **Dates access was refused (stops clock)** |

### 3.6 Awaab's Law Deadlines

| Hazard Type | Investigation | Start Repairs | Complete |
|-------------|---------------|---------------|----------|
| **Emergency** | 24 hours | 24 hours | 24 hours |
| **Non-Emergency** | 14 days | 7 days | Reasonable |
| **Damp & Mould** | 14 days | 7 days | As specified |

### 3.9 `property_fielder.awaab.access.refusal`
Access refusal tracking (stops the clock on Awaab deadlines).

| Field | Type | Description |
|-------|------|-------------|
| `deadline_id` | Many2one → awaab.deadline | Parent deadline |
| `refusal_date` | Date | Date access was refused |
| `reason` | Text | Reason given by tenant |
| `evidence_ids` | Many2many → ir.attachment | Evidence (letters, emails) |
| `days_stopped` | Integer | Days clock was stopped |
| `user_id` | Many2one → res.users | Logged by |

### 3.10 `property_fielder.dhs.assessment`
Decent Homes Standard **4-criteria** assessment (per government guidance).

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `assessment_date` | Date | Assessment date |
| `assessor_id` | Many2one → res.users | Assessor |
| `criterion_a_met` | Boolean | **A: Statutory Minimum (Free from Cat 1 hazards)** |
| `criterion_a_auto` | Boolean | **Computed: Auto-check from HHSRS defects** |
| `criterion_b_met` | Boolean | **B: Reasonable State of Repair** |
| `criterion_c_met` | Boolean | **C: Modern Facilities & Services** |
| `criterion_d_met` | Boolean | **D: Thermal Comfort** |
| `is_decent` | Boolean | Computed: all 4 criteria met |
| `remediation_plan` | Text | Plan to achieve decent |
| `target_date` | Date | Target for decent status |
| `notes` | Text | Notes |

### 3.8 `property_fielder.building.component`
Building component condition tracking.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `component_type` | Selection | roof/windows/heating/kitchen/bathroom |
| `age_years` | Integer | Age in years |
| `expected_life` | Integer | Expected lifespan |
| `condition` | Selection | good/fair/poor/critical |
| `replacement_cost` | Monetary | **Estimated replacement cost** |
| `currency_id` | Many2one → res.currency | Currency |
| `last_renewed` | Date | Last renewal/replacement |
| `next_renewal` | Date | Planned renewal |
| `notes` | Text | Condition notes |

---

## 4. Key Features

### 4.1 HHSRS Scoring Formula

The HHSRS score is calculated using the **Likelihood × Outcome** matrix from the Housing Act 2004.

#### Likelihood Classes (Probability of Harm in 12 Months)

| Class | Probability | Example |
|-------|-------------|---------|
| 1 | 1 in 5 (20%) | Almost certain to occur |
| 2 | 1 in 50 (2%) | Probable |
| 3 | 1 in 500 (0.2%) | Possible |
| 4 | 1 in 5000 (0.02%) | Unlikely |

#### Outcome Classes (Severity of Harm)

| Class | Description | Weighting |
|-------|-------------|-----------|
| I | Extreme | 10,000 (death, permanent paralysis) |
| II | Severe | 1,000 (serious fractures, asthma) |
| III | Serious | 300 (broken limb, eye injury) |
| IV | Moderate | 10 (bruising, minor cuts) |

#### Score Calculation

```python
def calculate_hhsrs_score(likelihood_class, outcome_weights):
    """
    HHSRS Score = Σ (Likelihood × Outcome Weight × Outcome Probability)

    Example for Excess Cold:
    - Likelihood Class 2 (1 in 50)
    - Outcome spread: 10% Class I, 30% Class II, 40% Class III, 20% Class IV
    - Score = 0.02 × (0.1×10000 + 0.3×1000 + 0.4×300 + 0.2×10)
    - Score = 0.02 × 1420.2 = 28.4
    """
    probability = {1: 0.2, 2: 0.02, 3: 0.002, 4: 0.0002}[likelihood_class]
    weighted_outcomes = sum(w * p for w, p in outcome_weights)
    return probability * weighted_outcomes
```

#### Band Assignment

| Band | Score Range | Category |
|------|-------------|----------|
| A | 5000+ | Category 1 |
| B | 2000-4999 | Category 1 |
| C | 1000-1999 | Category 1 |
| D | 500-999 | Category 2 |
| E | 200-499 | Category 2 |
| F | 100-199 | Category 2 |
| G | 50-99 | Category 2 |
| H | 20-49 | Category 2 |
| I | 10-19 | Category 2 |
| J | 1-9 | Category 2 |

### 4.2 Awaab's Law Compliance

- Automatic deadline calculation
- Email alerts before deadlines
- Escalation on overdue
- Breach tracking and reporting

### 4.3 Damp & Mould Workflow
- Report → Investigate → Repair → Verify
- Photo documentation timeline
- Cause identification tracking
- Tenant communication log

### 4.4 Decent Homes Assessment
- **4-criteria** checklist (A, B, C, D per UK legislation)
- Component condition tracking
- Remediation planning
- Target date tracking

### 4.5 Inspection Templates
- Full HHSRS 29-hazard template
- Damp & Mould specific template
- Decent Homes assessment template

---

## 5. UK Regulatory Compliance

| Regulation | Implementation |
|------------|----------------|
| **Housing Act 2004** | Full 29-hazard HHSRS implementation |
| **Awaab's Law (2023)** | Deadline tracking with escalation |
| **Decent Homes Standard** | **4-criteria** assessment (A, B, C, D) |
| **Social Housing (Regulation) Act 2023** | Proactive safety approach |

---

## 6. DHS Criterion A Automation

```python
class DHSAssessment(models.Model):
    _name = 'property_fielder.dhs.assessment'
    _inherit = ['mail.thread']

    @api.depends('property_id.defect_ids.current_hhsrs_band')
    def _compute_criterion_a_auto(self):
        """
        Criterion A: Free from Category 1 Hazards.
        Auto-check based on active HHSRS defects with Band A, B, or C.
        """
        for rec in self:
            cat1_defects = rec.property_id.defect_ids.filtered(
                lambda d: d.state == 'open' and d.current_hhsrs_band in ['A', 'B', 'C']
            )
            rec.criterion_a_auto = len(cat1_defects) == 0

    @api.depends('property_id.component_ids.condition', 'property_id.component_ids.age_years',
                 'property_id.component_ids.expected_life')
    def _compute_criterion_b(self):
        """
        Criterion B: Reasonable State of Repair.
        Component is failing if: condition == 'critical' OR age > expected_life.
        """
        for rec in self:
            failing_components = rec.property_id.component_ids.filtered(
                lambda c: c.condition == 'critical' or (c.age_years > c.expected_life)
            )
            rec.criterion_b_met = len(failing_components) == 0
```

---

## 7. HHSRS Score Calculation (16-Band)

```python
class HHSRSAssessment(models.Model):
    _name = 'property_fielder.hhsrs.assessment'
    _inherit = ['mail.thread']

    @api.depends('likelihood_band_id', 'outcome_prob_class_1', 'outcome_prob_class_2',
                 'outcome_prob_class_3', 'outcome_prob_class_4')
    def _compute_hhsrs_score(self):
        """
        HHSRS Score = RSP × Σ (Outcome Weight × Outcome Probability)

        Outcome Weights (Housing Act 2004):
        - Class I (Extreme): 10,000
        - Class II (Severe): 1,000
        - Class III (Serious): 300
        - Class IV (Moderate): 10
        """
        OUTCOME_WEIGHTS = {1: 10000, 2: 1000, 3: 300, 4: 10}

        for rec in self:
            if not rec.likelihood_band_id:
                rec.hhsrs_score = 0
                rec.hhsrs_band = 'J'
                rec.hhsrs_category = '2'
                continue

            rsp = rec.likelihood_band_id.rsp
            weighted_outcome = (
                (rec.outcome_prob_class_1 / 100) * OUTCOME_WEIGHTS[1] +
                (rec.outcome_prob_class_2 / 100) * OUTCOME_WEIGHTS[2] +
                (rec.outcome_prob_class_3 / 100) * OUTCOME_WEIGHTS[3] +
                (rec.outcome_prob_class_4 / 100) * OUTCOME_WEIGHTS[4]
            )
            rec.hhsrs_score = rsp * weighted_outcome

            # Assign band based on score
            score = rec.hhsrs_score
            if score >= 5000:
                rec.hhsrs_band, rec.hhsrs_category = 'A', '1'
            elif score >= 2000:
                rec.hhsrs_band, rec.hhsrs_category = 'B', '1'
            elif score >= 1000:
                rec.hhsrs_band, rec.hhsrs_category = 'C', '1'
            elif score >= 500:
                rec.hhsrs_band, rec.hhsrs_category = 'D', '2'
            elif score >= 200:
                rec.hhsrs_band, rec.hhsrs_category = 'E', '2'
            elif score >= 100:
                rec.hhsrs_band, rec.hhsrs_category = 'F', '2'
            elif score >= 50:
                rec.hhsrs_band, rec.hhsrs_category = 'G', '2'
            elif score >= 20:
                rec.hhsrs_band, rec.hhsrs_category = 'H', '2'
            elif score >= 10:
                rec.hhsrs_band, rec.hhsrs_category = 'I', '2'
            else:
                rec.hhsrs_band, rec.hhsrs_category = 'J', '2'

    @api.constrains('outcome_prob_class_1', 'outcome_prob_class_2',
                    'outcome_prob_class_3', 'outcome_prob_class_4')
    def _check_outcome_probabilities(self):
        """Outcome probabilities must sum to 100%."""
        for rec in self:
            total = (rec.outcome_prob_class_1 + rec.outcome_prob_class_2 +
                     rec.outcome_prob_class_3 + rec.outcome_prob_class_4)
            if abs(total - 100) > 0.01:
                raise ValidationError(
                    f"Outcome probabilities must sum to 100%. Current total: {total}%"
                )
```

---

## 7.1 DHS Criterion D - Thermal Comfort (EPC Integration)

```python
class DHSAssessment(models.Model):
    _inherit = 'property_fielder.dhs.assessment'

    @api.depends('property_id.epc_rating')
    def _compute_criterion_d(self):
        """
        Criterion D: Thermal Comfort.
        Property must have EPC rating of E or better (A-E).
        Requires EPC data from property_fielder_property_management.
        """
        PASSING_RATINGS = ['A', 'B', 'C', 'D', 'E']
        for rec in self:
            if rec.property_id.epc_rating:
                rec.criterion_d_met = rec.property_id.epc_rating in PASSING_RATINGS
            else:
                # No EPC on record - cannot assess
                rec.criterion_d_met = False
                rec.criterion_d_note = "EPC rating required for Criterion D assessment"

    criterion_d_note = fields.Char(string='Criterion D Note')
```

**Note:** This requires `property_fielder_property_management` to expose `epc_rating` field on `property_fielder.property`.

---

## 7.2 Awaab's Law "Reasonable Time" System Parameter

For non-emergency hazards, Awaab's Law specifies "reasonable time" for completion. This is configurable:

```xml
<!-- data/ir_config_parameter.xml -->
<record id="awaab_reasonable_time_days" model="ir.config_parameter">
    <field name="key">property_fielder_hhsrs.awaab_reasonable_time_days</field>
    <field name="value">28</field>
</record>
```

```python
class AwaabDeadline(models.Model):
    _inherit = 'property_fielder.awaab.deadline'

    @api.depends('hazard_type', 'investigation_date')
    def _compute_completion_deadline(self):
        """Calculate completion deadline based on hazard type."""
        reasonable_days = int(self.env['ir.config_parameter'].sudo().get_param(
            'property_fielder_hhsrs.awaab_reasonable_time_days', '28'
        ))

        for rec in self:
            if rec.hazard_type == 'emergency':
                # Emergency: 24 hours from report
                rec.completion_deadline = rec.report_date + timedelta(hours=24)
            elif rec.hazard_type == 'damp_mould':
                # Damp & Mould: As specified in regulations
                rec.completion_deadline = rec.repairs_start_deadline + timedelta(days=reasonable_days)
            else:
                # Non-emergency: "Reasonable time" (configurable)
                rec.completion_deadline = rec.repairs_start_deadline + timedelta(days=reasonable_days)
```

---

## 7.3 Awaab's Law Cron Job (Daily Alerts)

```xml
<!-- data/ir_cron.xml -->
<record id="ir_cron_awaab_deadline_check" model="ir.cron">
    <field name="name">Property Fielder: Awaab's Law Deadline Check</field>
    <field name="model_id" ref="model_property_fielder_awaab_deadline"/>
    <field name="state">code</field>
    <field name="code">model._cron_check_awaab_deadlines()</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="numbercall">-1</field>
    <field name="active">True</field>
</record>
```

```python
class AwaabDeadline(models.Model):
    _inherit = 'property_fielder.awaab.deadline'

    def _cron_check_awaab_deadlines(self):
        """Daily cron to check Awaab deadlines and send alerts."""
        today = fields.Date.today()
        warning_days = 2  # Alert 2 days before deadline

        # Find active deadlines
        deadlines = self.search([
            ('state', 'not in', ['completed', 'cancelled']),
        ])

        for deadline in deadlines:
            # Check investigation deadline
            if deadline.investigation_deadline:
                days_until = (deadline.investigation_deadline - today).days
                if days_until <= 0 and not deadline.investigation_met:
                    deadline._send_breach_alert('investigation')
                elif days_until <= warning_days and not deadline.investigation_met:
                    deadline._send_warning_alert('investigation', days_until)

            # Check repairs start deadline
            if deadline.repairs_start_deadline:
                days_until = (deadline.repairs_start_deadline - today).days
                if days_until <= 0 and not deadline.repairs_start_met:
                    deadline._send_breach_alert('repairs_start')
                elif days_until <= warning_days and not deadline.repairs_start_met:
                    deadline._send_warning_alert('repairs_start', days_until)

            # Check completion deadline
            if deadline.completion_deadline:
                days_until = (deadline.completion_deadline - today).days
                if days_until <= 0 and not deadline.completion_met:
                    deadline._send_breach_alert('completion')
                elif days_until <= warning_days and not deadline.completion_met:
                    deadline._send_warning_alert('completion', days_until)

    def _send_breach_alert(self, deadline_type):
        """Send breach notification email."""
        template = self.env.ref(
            f'property_fielder_hhsrs.mail_template_awaab_breach_{deadline_type}',
            raise_if_not_found=False
        )
        if template:
            template.send_mail(self.id, force_send=True)

        # Create urgent activity
        self.defect_id.activity_schedule(
            'mail.mail_activity_data_todo',
            date_deadline=fields.Date.today(),
            summary=f"URGENT: Awaab's Law {deadline_type.replace('_', ' ').title()} Deadline BREACHED",
            user_id=self.defect_id.property_id.managing_agent_id.user_id.id,
        )

    def _send_warning_alert(self, deadline_type, days_remaining):
        """Send warning notification email."""
        template = self.env.ref(
            f'property_fielder_hhsrs.mail_template_awaab_warning_{deadline_type}',
            raise_if_not_found=False
        )
        if template:
            template.with_context(days_remaining=days_remaining).send_mail(self.id, force_send=False)
```

---

## 8. Awaab Deadline Integration with Maintenance

```python
class AwaabDeadline(models.Model):
    _name = 'property_fielder.awaab.deadline'
    _inherit = ['mail.thread']

    access_refusal_ids = fields.One2many(
        'property_fielder.awaab.access.refusal', 'deadline_id',
        string='Access Refusals'
    )
    total_days_stopped = fields.Integer(
        compute='_compute_total_days_stopped',
        string='Total Days Clock Stopped'
    )
    maintenance_request_id = fields.Many2one(
        'property_fielder.maintenance.request',
        string='Linked Maintenance Request'
    )

    @api.depends('access_refusal_ids.days_stopped')
    def _compute_total_days_stopped(self):
        for rec in self:
            rec.total_days_stopped = sum(rec.access_refusal_ids.mapped('days_stopped'))

    @api.depends('maintenance_request_id.state')
    def _compute_repairs_status(self):
        """Auto-update Awaab status based on maintenance request state."""
        for rec in self:
            if rec.maintenance_request_id:
                if rec.maintenance_request_id.state == 'in_progress':
                    rec.repairs_start_met = True
                if rec.maintenance_request_id.state == 'done':
                    rec.completion_met = True
```

---

## 9. HHSRS Assessment Report (QWeb PDF)

```xml
<template id="report_hhsrs_assessment">
    <t t-call="web.html_container">
        <t t-call="web.external_layout">
            <div class="page">
                <h2>HHSRS Assessment Report</h2>
                <table class="table table-bordered">
                    <tr>
                        <th>Property</th>
                        <td><t t-esc="doc.defect_id.property_id.name"/></td>
                    </tr>
                    <tr>
                        <th>Hazard Type</th>
                        <td><t t-esc="doc.hhsrs_hazard_type_id.name"/></td>
                    </tr>
                    <tr>
                        <th>Likelihood Band</th>
                        <td><t t-esc="doc.likelihood_band_id.name"/></td>
                    </tr>
                    <tr>
                        <th>HHSRS Score</th>
                        <td><t t-esc="doc.hhsrs_score"/></td>
                    </tr>
                    <tr>
                        <th>Band</th>
                        <td><t t-esc="doc.hhsrs_band"/></td>
                    </tr>
                    <tr>
                        <th>Category</th>
                        <td><t t-esc="doc.hhsrs_category"/></td>
                    </tr>
                </table>
            </div>
        </t>
    </t>
</template>
```

---

## 10. HHSRS Remediation Job Creation

### 10.1 Overview
When an HHSRS assessment is confirmed, the system should automatically create a remediation job with appropriate priority and Awaab's Law deadline integration.

### 10.2 Data Model Extensions

#### `property_fielder.hhsrs.assessment` Extensions

| Field | Type | Description |
|-------|------|-------------|
| `remediation_job_id` | Many2one → job | Linked remediation job |
| `remediation_required` | Boolean | Whether remediation is needed |
| `remediation_type` | Selection | repair/replacement/removal/monitoring |
| `estimated_cost` | Monetary | Estimated remediation cost |

### 10.3 Remediation Job Creation Logic

```python
def action_confirm(self):
    """Confirm the assessment and create remediation job if needed."""
    self.ensure_one()
    self.write({'state': 'confirmed'})

    # Create remediation job for Cat 1 hazards (emergency)
    if self.hhsrs_category == '1':
        self._create_remediation_job(priority='3', is_emergency=True)
    # Create remediation job for Cat 2 hazards (scheduled)
    elif self.hhsrs_category == '2' and self.hhsrs_band in ['D', 'E', 'F']:
        self._create_remediation_job(priority='2', is_emergency=False)

def _create_remediation_job(self, priority='1', is_emergency=False):
    """Create a field service job for hazard remediation."""
    job_vals = {
        'name': f'HHSRS Remediation: {self.hhsrs_hazard_type_id.name}',
        'property_id': self.property_id.id,
        'partner_id': self.property_id.partner_id.id,
        'job_type': 'remediation',
        'priority': priority,
        'is_hhsrs_remediation': True,
        'hhsrs_assessment_id': self.id,
        'scheduled_date': self._get_remediation_deadline(is_emergency),
        'notes': self._build_remediation_notes(),
    }
    job = self.env['property_fielder.job'].create(job_vals)
    self.remediation_job_id = job.id

    # Link to Awaab deadline if applicable
    if self.hhsrs_hazard_type_id.is_awaab_covered:
        self._create_awaab_deadline(job, is_emergency)

def _get_remediation_deadline(self, is_emergency):
    """Calculate deadline based on hazard category."""
    if is_emergency:
        return fields.Date.today()  # Same day for Cat 1
    else:
        # Reasonable time from config parameter
        days = int(self.env['ir.config_parameter'].sudo().get_param(
            'property_fielder_hhsrs.awaab_reasonable_time_days', '28'
        ))
        return fields.Date.today() + timedelta(days=days)
```

### 10.4 Job Model Extensions

| Field | Type | Description |
|-------|------|-------------|
| `job_type` | Selection | inspection/remediation/maintenance/void_check |
| `is_hhsrs_remediation` | Boolean | Is this an HHSRS remediation job |
| `hhsrs_assessment_id` | Many2one → assessment | Source HHSRS assessment |
| `awaab_deadline_id` | Many2one → awaab.deadline | Linked Awaab deadline |

### 10.5 Awaab Deadline Integration

When a remediation job is created for an Awaab-covered hazard:
1. Create Awaab deadline record linked to job
2. Set deadlines based on hazard type (emergency/non-emergency/damp_mould)
3. Update Awaab deadline status when job state changes:
   - Job started → `repairs_start_met = True`
   - Job completed → `completion_met = True`

### 10.6 Priority Mapping

| HHSRS Category | Band | Job Priority | Response Time |
|----------------|------|--------------|---------------|
| Category 1 | A, B, C | Urgent (3) | 24 hours |
| Category 2 | D, E | High (2) | 7 days |
| Category 2 | F, G | Normal (1) | 28 days |
| Category 2 | H, I, J | Low (0) | Monitoring only |

---

## 11. Gemini Review Status

| Criteria | Status |
|----------|--------|
| 29 hazards defined | ✅ Complete |
| **16 HHSRS Likelihood Bands (RSP)** | ✅ Added |
| **hhsrs.assessment model (history)** | ✅ Added |
| Full HHSRS scoring formula | ✅ Complete |
| **Outcome probability validation** | ✅ Added |
| Likelihood/Outcome justification | ✅ Complete |
| Vulnerable occupant tracking | ✅ Complete |
| Awaab deadlines clear | ✅ Complete |
| **Access refusal model (One2many)** | ✅ Added |
| **Maintenance request linkage** | ✅ Added |
| **Decant start/end dates** | ✅ Added |
| **damp.mould.timeline model** | ✅ Added |
| **DHS 4-criteria (not 5)** | ✅ Fixed |
| **DHS Criterion A automation** | ✅ Added |
| **DHS Criterion B automation** | ✅ Added |
| **DHS Criterion D (EPC integration)** | ✅ Added |
| **Awaab "reasonable time" system param** | ✅ Added |
| **Awaab deadline cron job (daily)** | ✅ Added |
| **Breach/warning email alerts** | ✅ Added |
| **HHSRS Assessment PDF Report** | ✅ Added |
| **web dependency for reports** | ✅ Added |
| **property_fielder_maintenance dependency** | ✅ Added |
| **tracking=True on justification fields** | ✅ Added |
| **ir.attachment for photos** | ✅ Fixed |
| **Overall** | ✅ Ready for Review |

