# PRD: Property Fielder Tenant Access

**Addon Name:** `property_fielder_tenant_access`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Domain (Layer 3)  
**Phase:** Phase 5 (Tenant Communication)  
**Effort:** 16 days  

---

## 1. Overview

Access booking, confirmation, and proof of service tracking for tenant/occupier coordination.

### 1.1 Purpose
Manage appointment scheduling with tenants, track access attempts, handle no-access escalation, and document proof of service for certificate delivery.

### 1.2 Target Users
- Dispatch Managers
- Field Inspectors
- Tenants (notification recipients)
- Compliance Managers (escalation)

### 1.3 Business Value
- Reduces no-access wasted visits
- Documents access attempts for legal compliance
- Tracks certificate delivery (proof of service)
- Automates escalation workflow

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',
    'sms',  # SMS notifications for access reminders
    'calendar',  # For appointment scheduling
    'portal',  # Self-service booking portal
    'website',  # Portal frontend
    'property_fielder_property_management',
    'property_fielder_field_service',
]
```

---

## 3. Data Models

### 3.1 `property_fielder.access.booking`

Appointment booking with tenant.

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | Many2one → job | Related job |
| `property_id` | Many2one → property | Property |
| `contact_id` | Many2one → res.partner | Tenant/occupier |
| `contact_type` | Selection | tenant/owner_occupier/agent |
| `proposed_date` | Datetime | Proposed appointment |
| `proposed_time_start` | Float | Proposed window start (0-24) |
| `proposed_time_end` | Float | Proposed window end (0-24) |
| `confirmed_date` | Datetime | Confirmed appointment |
| `state` | Selection | pending/confirmed/declined/no_response/rescheduled |
| `notification_sent` | Datetime | When notification sent |
| `notification_method` | Selection | email/sms/letter/both |
| `response_received` | Datetime | When response received |
| `decline_reason` | Text | Reason for decline |
| `alternative_dates` | Text | Alternative dates suggested |
| `reminder_sent` | Boolean | 24h reminder sent |
| `access_token` | Char | **Secure token for self-service portal** |
| `token_expiry` | Datetime | **Token expiration** |
| `expected_duration_minutes` | Integer | **Expected visit duration** |
| `calendar_event_id` | Many2one → calendar.event | **Odoo Calendar integration** |

### 3.2 `property_fielder.access.attempt`
Individual access attempt.

| Field | Type | Description |
|-------|------|-------------|
| `job_id` | Many2one → job | Related job |
| `booking_id` | Many2one → booking | Related booking |
| `inspector_id` | Many2one → inspector | Inspector |
| `attempt_date` | Datetime | Attempt date/time |
| `device_timestamp` | Datetime | **Device timestamp (for offline sync)** |
| `result` | Selection | access_granted/no_answer/refused/rescheduled |
| `door_knocked` | Boolean | Door was knocked |
| `card_left` | Boolean | Calling card left |
| `photo_id` | Many2one → job.photo | Evidence photo |
| `notes` | Text | Notes |
| `attempt_number` | Integer | 1st, 2nd, 3rd attempt |
| `latitude` | Float | GPS latitude |
| `longitude` | Float | GPS longitude |
| `gps_accuracy` | Float | **GPS accuracy in meters** |
| `gps_verified` | Boolean | **Computed: within 50m of property** |

**Note:** `device_timestamp` captures the actual time on the mobile device when the attempt was recorded, separate from `create_date` which is when the record was synced to the server. This is critical for offline scenarios where sync may be delayed.

### 3.3 `property_fielder.access.escalation`
No-access escalation workflow.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `job_id` | Many2one → job | Original job |
| `attempt_ids` | Many2many → access.attempt | Failed attempts |
| `escalation_level` | Selection | warning/notice/legal |
| `state` | Selection | pending/letter_sent/legal_action/resolved |
| `warning_date` | Date | Warning letter sent |
| `notice_date` | Date | Formal notice sent |
| `legal_application_date` | Date | Injunction application |
| `resolution_date` | Date | Resolved date |
| `resolution_notes` | Text | How resolved |
| `evidence_bundle_id` | Many2one → ir.attachment | **Generated evidence bundle PDF** |

### 3.3.1 Evidence Bundle Generation

**Critical for legal proceedings:** Generate a court-ready evidence bundle PDF.

```python
class AccessEscalation(models.Model):
    _inherit = 'property_fielder.access.escalation'

    evidence_bundle_id = fields.Many2one('ir.attachment', string='Evidence Bundle')

    def action_generate_evidence_bundle(self):
        """
        Generate court-ready evidence bundle PDF containing:
        - Property details and tenancy information
        - Chronological list of all access attempts
        - GPS verification for each attempt
        - Photos of calling cards left
        - Copies of all notification letters sent
        - Proof of service for each notification
        """
        self.ensure_one()
        report = self.env.ref('property_fielder_tenant_access.report_evidence_bundle')
        pdf_content, _ = report._render_qweb_pdf(self.ids)

        attachment = self.env['ir.attachment'].create({
            'name': f'Evidence_Bundle_{self.property_id.name}_{fields.Date.today()}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })
        self.evidence_bundle_id = attachment.id
        return attachment

# QWeb Report Template includes:
# 1. Cover page with case summary
# 2. Property details (address, UPRN, landlord)
# 3. Tenant details (name, contact info)
# 4. Chronological attempt log with:
#    - Date/time (device_timestamp)
#    - GPS coordinates and verification status
#    - Result (no_answer, refused, etc.)
#    - Photo evidence
#    - Inspector signature
# 5. Copies of all letters sent (warning, notice)
# 6. Proof of service records
# 7. Statement of facts
```

### 3.4 `property_fielder.proof.of.service`
Certificate delivery confirmation.

| Field | Type | Description |
|-------|------|-------------|
| `certification_id` | Many2one → certification | Certificate delivered |
| `property_id` | Many2one → property | Property |
| `recipient_id` | Many2one → res.partner | Recipient |
| `delivery_method` | Selection | hand/post/email |
| `delivered_date` | Datetime | Delivery date |
| `signature_id` | Many2one → job.signature | Recipient signature |
| `witness_name` | Char | Witness name (if applicable) |
| `photo_id` | Many2one → job.photo | Delivery photo |
| `notes` | Text | Notes |

### 3.5 `property_fielder.how.to.rent`
How to Rent guide tracking.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `tenant_id` | Many2one → res.partner | Tenant |
| `tenancy_start_date` | Date | Tenancy start |
| `guide_version` | Char | Guide version (date) |
| `delivery_date` | Date | When delivered |
| `delivery_method` | Selection | email/hand/post |
| `acknowledgment_received` | Boolean | Tenant acknowledged |
| `acknowledgment_date` | Date | Acknowledgment date |
| `signature_id` | Many2one → job.signature | Acknowledgment signature |

---

## 4. Key Features

### 4.1 Appointment Notifications
- Email notification with date/time
- SMS notification (optional)
- 24-hour reminder
- Reschedule link in notification

### 4.2 Confirmation Tracking
- `pending` → `confirmed` → `rescheduled`
- Track decline reasons
- Alternative date suggestions
- Auto-escalation on no response

### 4.3 No-Access Escalation (3-Strike)
1. **1st attempt** - Leave calling card
2. **2nd attempt** - Send warning letter
3. **3rd attempt** - Formal notice
4. **Escalation** - Legal injunction application

### 4.4 Court-Ordered Entry Workflow

**Note:** "Forced Entry" terminology avoided - use "Court-Ordered Entry" for legal accuracy.

- Document all access attempts with GPS verification
- Generate court application pack (County Court injunction)
- Track injunction process and hearing dates
- Record court-ordered entry with witnesses and police presence
- Photograph property condition before/after entry

### 4.5 Proof of Service
- Tenant signature for certificate receipt
- Photo evidence of delivery
- Track How to Rent guide delivery
- Version tracking (new guides each year)

### 4.6 Owner-Occupier vs Tenant Logic
- Different notification templates
- Owner-occupiers don't need How to Rent
- Different escalation paths

---

## 5. Notification Templates

| Template | Trigger | Recipients |
|----------|---------|------------|
| `access_booking_request` | Job created | Tenant |
| `access_booking_confirmed` | Tenant confirms | Inspector |
| `access_booking_reminder` | 24h before | Tenant |
| `access_no_response` | 48h no response | Manager |
| `access_escalation_warning` | 2 failed attempts | Tenant |
| `access_escalation_notice` | 3 failed attempts | Tenant + Landlord |

---

## 6. Self-Service Portal

### 6.1 Tenant Booking Portal

| Feature | Description |
|---------|-------------|
| **Access via Token** | Secure link with expiring token |
| **View Appointment** | See proposed date/time |
| **Confirm** | Accept proposed appointment |
| **Decline** | Decline with reason |
| **Suggest Alternatives** | Propose different dates |
| **Calendar Integration** | Add to calendar (iCal) |

### 6.2 Portal Routes

```python
@http.route('/access/booking/<token>', type='http', auth='public')
def booking_portal(self, token):
    """Public portal for tenant to manage booking."""
    booking = self._validate_token(token)
    return request.render('property_fielder_tenant_access.booking_portal', {
        'booking': booking
    })
```

### 6.3 Portal/Calendar Conflict Resolution

**Critical:** When tenant proposes alternative dates via portal, handle conflicts with existing calendar events.

```python
class AccessBooking(models.Model):
    _inherit = 'property_fielder.access.booking'

    proposed_status = fields.Selection([
        ('pending', 'Pending Dispatcher Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected - Conflict'),
    ], default='pending')
    conflict_reason = fields.Text()

    def action_tenant_propose_alternative(self, proposed_datetime):
        """
        Tenant proposes alternative via portal.
        Does NOT write directly to calendar.event - creates proposal for review.
        """
        self.ensure_one()
        # Check for conflicts with inspector's calendar
        inspector = self.job_id.inspector_id
        conflicts = self.env['calendar.event'].search([
            ('partner_ids', 'in', inspector.partner_id.id),
            ('start', '<=', proposed_datetime + timedelta(hours=2)),
            ('stop', '>=', proposed_datetime),
        ])

        if conflicts:
            self.proposed_status = 'rejected'
            self.conflict_reason = f"Inspector has {len(conflicts)} conflicting appointments"
            # Notify tenant of conflict
            self._send_conflict_notification()
        else:
            # Create PROPOSED booking for dispatcher approval
            self.proposed_date = proposed_datetime
            self.proposed_status = 'pending'
            # Create mail.activity for dispatcher
            self.env['mail.activity'].create({
                'res_model': self._name,
                'res_id': self.id,
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'summary': f'Review proposed booking: {self.property_id.name}',
                'user_id': self.job_id.dispatcher_id.id,
            })

    def action_dispatcher_approve(self):
        """Dispatcher approves proposed booking - creates calendar event."""
        self.ensure_one()
        self.confirmed_date = self.proposed_date
        self.proposed_status = 'approved'
        self.state = 'confirmed'
        # NOW create calendar event
        self._create_calendar_event()
```

---

## 7. UK Regulatory Compliance

| Regulation | Implementation |
|------------|----------------|
| **Section 11 L&T Act 1985** | 24h written notice for repairs |
| **Section 48 L&T Act 1987** | Landlord address for service |
| **Gas Safety (I&U) Regs** | 14-day access letter if no response |
| **Data Protection Act 2018** | Token-based secure access |

---

## 8. GPS Verification Logic

```python
from math import radians, sin, cos, sqrt, atan2

class AccessAttempt(models.Model):
    _inherit = 'property_fielder.access.attempt'

    gps_accuracy = fields.Float('GPS Accuracy (m)')
    gps_verified = fields.Boolean(
        compute='_compute_gps_verified',
        store=True,
        help="True if attempt location within 50m of property"
    )

    @api.depends('latitude', 'longitude', 'job_id.property_id')
    def _compute_gps_verified(self):
        for rec in self:
            if not rec.latitude or not rec.longitude:
                rec.gps_verified = False
                continue
            prop = rec.job_id.property_id
            if not prop.latitude or not prop.longitude:
                rec.gps_verified = False
                continue
            # Haversine formula
            distance = self._haversine(
                rec.latitude, rec.longitude,
                prop.latitude, prop.longitude
            )
            rec.gps_verified = distance <= 50  # 50 meters

    def _haversine(self, lat1, lon1, lat2, lon2):
        """Calculate distance in meters between two GPS points."""
        R = 6371000  # Earth radius in meters
        phi1, phi2 = radians(lat1), radians(lat2)
        dphi = radians(lat2 - lat1)
        dlambda = radians(lon2 - lon1)
        a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
        return R * 2 * atan2(sqrt(a), sqrt(1-a))
```

---

## 9. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **sms/portal/website dependencies** | ✅ Added |
| **GPS verification logic** | ✅ Added |
| **Court-Ordered Entry (not Forced)** | ✅ Fixed |
| Access token for portal | ✅ Complete |
| Expected duration field | ✅ Complete |
| Calendar integration | ✅ Complete |
| Escalation workflow defined | ✅ Complete |
| Notifications specified | ✅ Complete |
| Proof of service clear | ✅ Complete |
| **Evidence Bundle generation** | ✅ Added |
| **Portal/Calendar conflict logic** | ✅ Added |
| **device_timestamp for offline sync** | ✅ Added |
| **Dispatcher approval workflow** | ✅ Added |
| **Overall** | ✅ Ready for Review |

