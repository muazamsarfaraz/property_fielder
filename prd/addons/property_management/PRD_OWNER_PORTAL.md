# PRD: Property Fielder Owner Portal

**Addon Name:** `property_fielder_owner_portal`  
**Version:** 2.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase C (Growth & Efficiency)  
**Effort:** 60-80 hours  

---

## 1. Overview

Self-service portal for landlords/property owners to manage their portfolio.

### 1.1 Purpose
Provide landlords with visibility into their property portfolio, financial statements, maintenance updates, and compliance status with UK regulatory awareness.

### 1.2 Target Users
- Landlords (UK resident)
- Non-Resident Landlords (NRL scheme)
- Portfolio Investors
- Property Companies

---

## 2. Dependencies

```python
depends = [
    'base',
    'website',
    'portal',
    'mail',
    'property_fielder_property_management',
    'property_fielder_property_accounting',
    'property_fielder_property_maintenance',
    'property_fielder_property_documents',
]
```

---

## 3. Technical Architecture

### 3.1 Portal Controllers (`controllers/main.py`)

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/my/properties` | GET | user | Portfolio dashboard |
| `/my/properties/<int:id>` | GET | user | Property details |
| `/my/statements` | GET | user | Financial statements list |
| `/my/statements/<int:id>` | GET | user | Statement details |
| `/my/statements/<int:id>/download` | GET | user | Download PDF |
| `/my/maintenance` | GET | user | Maintenance requests |
| `/my/maintenance/<int:id>/approve` | POST | user | Approve cost |
| `/my/documents` | GET | user | Document library |

### 3.2 Access Control

**Record Rules:**
```python
# Owner can only see their own properties
domain = [('owner_id', '=', user.partner_id.id)]
```

### 3.3 Model Extensions

#### `res.partner` (Owner Extension)
| Field | Type | Description |
|-------|------|-------------|
| `is_property_owner` | Boolean | Is landlord/owner? |
| `owner_portal_access` | Boolean | Has portal access? |
| `is_non_resident_landlord` | Boolean | NRL scheme applies? |
| `nrl_exemption_number` | Char | HMRC exemption number |
| `maintenance_approval_limit` | Monetary | Auto-approve below this |
| `bank_account_id` | Many2one → res.partner.bank | Payout account |
| `pending_bank_account_id` | Many2one → res.partner.bank | **Pending bank change (48h cooling off)** |
| `bank_change_request_date` | Datetime | **When bank change was requested** |
| `bank_change_token` | Char | **Email verification token** |
| `bank_change_token_expiry` | Datetime | **Token expiration** |
| `terms_signed_date` | Date | Agency agreement signed |
| `tax_reporting_basis` | Selection | **cash/accruals - for Self Assessment** |

---

## 4. Data Models

### 4.1 Owner Statement (`property_fielder.owner.statement`)

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Statement reference |
| `owner_id` | Many2one → res.partner | Owner |
| `ownership_share` | Float | **Ownership percentage (for joint ownership)** |
| `period_start` | Date | Statement period start |
| `period_end` | Date | Statement period end |
| `property_ids` | Many2many → property | Properties included |
| `opening_balance` | Monetary | Opening balance from prior period |
| `gross_rent` | Monetary | Total rent collected |
| `management_fee` | Monetary | Agency fee |
| `maintenance_costs` | Monetary | Repairs charged |
| `nrl_tax_withheld` | Monetary | 20% NRL tax if applicable |
| `retained_amount` | Monetary | Amount retained for future expenses |
| `net_payable` | Monetary | Amount due to owner |
| `closing_balance` | Monetary | Closing balance carried forward |
| `payment_date` | Date | When paid |
| `payment_id` | Many2one → account.payment | **Linked payment record** |
| `line_ids` | One2many → statement.line | Detail lines |
| `state` | Selection | draft/confirmed/paid/locked |
| `attachment_id` | Many2one → ir.attachment | PDF statement |

### 4.2 Statement Line (`property_fielder.owner.statement.line`)

| Field | Type | Description |
|-------|------|-------------|
| `statement_id` | Many2one → statement | Parent statement |
| `property_id` | Many2one → property | Property |
| `line_type` | Selection | rent/fee/maintenance/other |
| `description` | Char | Line description |
| `amount` | Monetary | Line amount |
| `is_tax_deductible` | Boolean | Deductible for NRL tax calculation |
| `move_line_id` | Many2one → account.move.line | Accounting link |
| `amount_allocated` | Monetary | **Amount allocated from move_line (for joint ownership splits)** |
| `dispute_state` | Selection | **none/queried/resolved/released** |
| `dispute_reason` | Text | **Owner's query reason** |
| `dispute_resolution` | Text | **Admin resolution notes** |
| `dispute_date` | Datetime | **When query was raised** |
| `resolved_by` | Many2one → res.users | **Who resolved the query** |

### 4.3 Property Ownership (`property_fielder.property.ownership`)

Joint ownership tracking for percentage splits.

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `owner_id` | Many2one → res.partner | Owner |
| `ownership_percentage` | Float | Ownership share (0-100) |
| `is_primary_contact` | Boolean | Primary contact for property |
| `start_date` | Date | Ownership start date |
| `end_date` | Date | Ownership end date (if sold) |
| `state` | Selection | active/ended |

---

## 5. Portal Features

### 5.1 Dashboard (`/my/properties`)

**Computed Fields on Partner:**
```python
total_portfolio_value = fields.Monetary(compute='_compute_portfolio')
total_properties = fields.Integer(compute='_compute_portfolio')
occupancy_rate = fields.Float(compute='_compute_portfolio')
pending_approvals = fields.Integer(compute='_compute_approvals')
```

### 5.2 Maintenance Approvals

**Approval Workflow:**
```python
if work_order.estimated_cost > owner.maintenance_approval_limit:
    work_order.state = 'awaiting_owner_approval'
else:
    work_order.state = 'approved'  # Auto-approve
```

### 5.3 Property Performance View

| Metric | Description |
|--------|-------------|
| Rental Yield | Annual rent / property value × 100 |
| Occupancy Rate | Days occupied / total days × 100 |
| Maintenance Ratio | Maintenance cost / rent collected × 100 |
| Net Income | Rent - fees - maintenance - tax |

### 5.4 Document Access

| Document Type | Owner Access |
|---------------|--------------|
| Tenancy Agreement | ✅ Full |
| Inventory Report | ✅ Full |
| Gas Certificate | ✅ Full |
| EICR | ✅ Full |
| EPC | ✅ Full |
| Tenant ID | ❌ Redacted (GDPR) |
| Bank Details | ❌ Redacted |

### 5.5 Notification Preferences

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    owner_notify_rent_received = fields.Boolean(default=True)
    owner_notify_maintenance = fields.Boolean(default=True)
    owner_notify_compliance = fields.Boolean(default=True)
    owner_notify_statement = fields.Boolean(default=True)
    owner_notify_method = fields.Selection([
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('both', 'Email + SMS'),
    ], default='email')
```

### 5.6 Compliance Dashboard

**Owner visibility into property compliance status:**

```python
class Property(models.Model):
    _inherit = 'property_fielder.property'

    # Computed for portal display
    compliance_status = fields.Selection([
        ('compliant', 'Compliant'),
        ('expiring', 'Expiring Soon'),
        ('non_compliant', 'Non-Compliant'),
    ], compute='_compute_compliance_status')

    @api.depends('gas_safety_expiry', 'eicr_expiry', 'epc_expiry')
    def _compute_compliance_status(self):
        today = fields.Date.today()
        warning_days = 30
        for rec in self:
            expiries = [
                rec.gas_safety_expiry,
                rec.eicr_expiry,
                rec.epc_expiry,
            ]
            if any(e and e < today for e in expiries):
                rec.compliance_status = 'non_compliant'
            elif any(e and e < today + timedelta(days=warning_days) for e in expiries):
                rec.compliance_status = 'expiring'
            else:
                rec.compliance_status = 'compliant'
```

### 5.7 Annual Tax Summary

**Provide landlords with annual income/expense summary for Self Assessment:**

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_annual_tax_summary(self, tax_year_start, tax_year_end, cash_basis=True):
        """
        Generate summary for UK Self Assessment.
        Tax year: 6 April to 5 April.

        Args:
            cash_basis: If True, filter by payment_date (individual landlords).
                        If False, filter by period dates (corporate landlords).
        """
        if cash_basis:
            # Cash Basis: Use payment_date for individual landlords
            statements = self.env['property_fielder.owner.statement'].search([
                ('owner_id', '=', self.id),
                ('payment_date', '>=', tax_year_start),
                ('payment_date', '<=', tax_year_end),
                ('state', '=', 'paid'),
            ])
        else:
            # Accruals Basis: Use period dates for corporate landlords
            statements = self.env['property_fielder.owner.statement'].search([
                ('owner_id', '=', self.id),
                ('period_start', '>=', tax_year_start),
                ('period_end', '<=', tax_year_end),
                ('state', '=', 'paid'),
            ])
        return {
            'gross_rent': sum(statements.mapped('gross_rent')),
            'management_fees': sum(statements.mapped('management_fee')),
            'maintenance_costs': sum(statements.mapped('maintenance_costs')),
            'nrl_tax_withheld': sum(statements.mapped('nrl_tax_withheld')),
            'net_income': sum(statements.mapped('net_payable')),
        }
```

### 5.8 Statement Generation Workflow

**Wizard to generate owner statements:**

```python
class OwnerStatementWizard(models.TransientModel):
    _name = 'property_fielder.owner.statement.wizard'
    _description = 'Generate Owner Statements'

    owner_ids = fields.Many2many('res.partner', domain=[('is_property_owner', '=', True)])
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)

    def action_generate_statements(self):
        """
        Generate statements by gathering all posted, unreconciled
        account.move.line items for each owner within the period.
        """
        Statement = self.env['property_fielder.owner.statement']
        for owner in self.owner_ids:
            # Get previous statement closing balance
            prev_statement = Statement.search([
                ('owner_id', '=', owner.id),
                ('state', '=', 'paid'),
            ], order='period_end desc', limit=1)
            opening_balance = prev_statement.closing_balance if prev_statement else 0.0

            # Create statement with lines from accounting
            statement = Statement.create({
                'owner_id': owner.id,
                'period_start': self.period_start,
                'period_end': self.period_end,
                'opening_balance': opening_balance,
            })
            statement._populate_lines_from_accounting()
        return {'type': 'ir.actions.act_window_close'}
```

### 5.9 Portal Chatter Integration

**Enable messaging on statements and maintenance records:**

```xml
<!-- Inherit portal chatter for owner statement -->
<template id="owner_statement_portal_chatter" inherit_id="portal.portal_chatter">
    <xpath expr="//div[@id='portal_chatter']" position="attributes">
        <attribute name="t-if">object._name == 'property_fielder.owner.statement'</attribute>
    </xpath>
</template>
```

---

## 6. UK Regulatory Compliance

### 6.1 NRL Scheme (Corrected Formula)

**HMRC NRL Rules:**

- Tax is 20% of **Taxable Income** (Gross Rent - Allowable Expenses), not net_payable
- If landlord has HMRC exemption certificate, no withholding required
- Agent must register with HMRC as NRL agent

**Correct Calculation Order:**
1. `taxable_income` = `gross_rent` - SUM(`line_ids` WHERE `is_tax_deductible` = True)
2. `nrl_tax_withheld` = `taxable_income` × 0.20 (if NRL without exemption)
3. `net_payable` = `taxable_income` - `nrl_tax_withheld` - `retained_amount`

```python
class OwnerStatement(models.Model):
    _inherit = 'property_fielder.owner.statement'

    taxable_income = fields.Monetary(
        compute='_compute_taxable_income',
        store=True,
        help="Gross rent minus deductible expenses"
    )

    @api.depends('gross_rent', 'line_ids.amount', 'line_ids.is_tax_deductible')
    def _compute_taxable_income(self):
        """Calculate taxable income (gross - deductible expenses)."""
        for rec in self:
            deductible = sum(
                line.amount for line in rec.line_ids
                if line.is_tax_deductible and line.amount < 0
            )
            rec.taxable_income = rec.gross_rent + deductible  # deductible is negative

    @api.depends('taxable_income', 'owner_id.is_non_resident_landlord',
                 'owner_id.nrl_exemption_number')
    def _compute_nrl_tax(self):
        """
        NRL tax is 20% of TAXABLE INCOME (gross - deductible expenses).
        NOT based on net_payable (which would create circular dependency).
        """
        for rec in self:
            if rec.owner_id.is_non_resident_landlord:
                if not rec.owner_id.nrl_exemption_number:
                    rec.nrl_tax_withheld = rec.taxable_income * 0.20
                else:
                    rec.nrl_tax_withheld = 0.0
            else:
                rec.nrl_tax_withheld = 0.0

    @api.depends('taxable_income', 'nrl_tax_withheld', 'retained_amount')
    def _compute_net_payable(self):
        """Net payable = taxable income - tax - retained."""
        for rec in self:
            rec.net_payable = rec.taxable_income - rec.nrl_tax_withheld - rec.retained_amount
```

### 6.2 GDPR
- Tenant info redacted (name only, no contact)
- Owner cannot access tenant ID documents
- Audit trail of document access

---

## 7. Security

### 7.1 Bank Details Update Workflow

**Security Requirements:**

- Requires email verification via secure token
- 48-hour cooling off period before activation
- Notification to registered email on request AND activation
- Audit trail of all bank detail changes

**Portal Route:**

```python
@http.route('/my/account/bank/update', type='http', auth='user', methods=['POST'])
def bank_update_request(self, **post):
    """
    Request bank details change with email verification.
    """
    partner = request.env.user.partner_id
    new_bank = request.env['res.partner.bank'].sudo().create({
        'partner_id': partner.id,
        'acc_number': post.get('acc_number'),
        'bank_id': int(post.get('bank_id')),
    })

    # Generate secure token
    token = secrets.token_urlsafe(32)
    partner.sudo().write({
        'pending_bank_account_id': new_bank.id,
        'bank_change_request_date': fields.Datetime.now(),
        'bank_change_token': token,
        'bank_change_token_expiry': fields.Datetime.now() + timedelta(hours=48),
    })

    # Send verification email
    template = request.env.ref('property_fielder_owner_portal.email_bank_change_verify')
    template.sudo().send_mail(partner.id)

    return request.redirect('/my/account?message=bank_change_pending')


@http.route('/my/account/bank/verify/<token>', type='http', auth='public')
def bank_verify(self, token):
    """
    Verify bank change after 48h cooling off period.
    """
    partner = request.env['res.partner'].sudo().search([
        ('bank_change_token', '=', token),
        ('bank_change_token_expiry', '>', fields.Datetime.now()),
    ], limit=1)

    if not partner:
        return request.redirect('/my/account?error=invalid_token')

    # Check 48h cooling off period
    if partner.bank_change_request_date + timedelta(hours=48) > fields.Datetime.now():
        remaining = (partner.bank_change_request_date + timedelta(hours=48)) - fields.Datetime.now()
        return request.redirect(f'/my/account?error=cooling_off&hours={remaining.hours}')

    # Activate new bank account
    partner.write({
        'bank_account_id': partner.pending_bank_account_id.id,
        'pending_bank_account_id': False,
        'bank_change_token': False,
        'bank_change_token_expiry': False,
    })

    # Send confirmation email
    template = request.env.ref('property_fielder_owner_portal.email_bank_change_confirmed')
    template.sudo().send_mail(partner.id)

    return request.redirect('/my/account?message=bank_change_confirmed')
```

### 7.2 Statement Period Continuity

**Constraint to ensure no gaps between statement periods:**

```python
class OwnerStatement(models.Model):
    _inherit = 'property_fielder.owner.statement'

    @api.constrains('period_start', 'period_end', 'owner_id')
    def _check_period_continuity(self):
        """Ensure opening_balance matches previous closing_balance."""
        for rec in self:
            prev = self.search([
                ('owner_id', '=', rec.owner_id.id),
                ('period_end', '<', rec.period_start),
                ('state', '=', 'paid'),
            ], order='period_end desc', limit=1)
            if prev and rec.opening_balance != prev.closing_balance:
                raise ValidationError(
                    f"Opening balance ({rec.opening_balance}) must match "
                    f"previous closing balance ({prev.closing_balance})"
                )
```

### 7.3 Statement Locking on Payment

**Lock statement when payment is reconciled:**

```python
class OwnerStatement(models.Model):
    _inherit = 'property_fielder.owner.statement'

    def action_mark_paid(self):
        """
        Mark statement as paid by creating an account.payment record.
        This ensures proper accounting integration.
        """
        self.ensure_one()
        if self.state != 'confirmed':
            raise UserError("Only confirmed statements can be marked as paid.")

        if not self.owner_id.bank_account_id:
            raise UserError("Owner has no bank account configured for payout.")

        # Create outgoing payment to owner
        payment = self.env['account.payment'].create({
            'payment_type': 'outbound',
            'partner_type': 'supplier',  # Paying the owner
            'partner_id': self.owner_id.id,
            'amount': self.net_payable,
            'currency_id': self.currency_id.id,
            'journal_id': self.env.company.client_money_journal_id.id,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
            'ref': f'Owner Statement: {self.name}',
            'partner_bank_id': self.owner_id.bank_account_id.id,
        })
        payment.action_post()

        self.write({
            'state': 'locked',
            'payment_id': payment.id,
            'payment_date': fields.Date.today(),
        })

        # Lock all line items and mark move lines as statemented
        self.line_ids.write({'locked': True})
        for line in self.line_ids.filtered(lambda l: l.move_line_id):
            line.move_line_id.is_included_in_statement = True

    @api.constrains('state')
    def _check_locked_modifications(self):
        """Prevent modifications to locked statements."""
        for rec in self:
            if rec.state == 'locked':
                # Only allow state changes by admin
                if not self.env.user.has_group('property_fielder.group_property_admin'):
                    raise ValidationError(
                        "Locked statements cannot be modified. Contact admin."
                    )
```

### 7.4 Admin Override for Bank Change Cooling Off

**Admin can bypass 48h cooling off period:**

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_admin_approve_bank_change(self):
        """Admin override to immediately activate pending bank change."""
        self.ensure_one()
        if not self.env.user.has_group('property_fielder.group_property_admin'):
            raise AccessError("Only admins can override cooling off period.")

        if not self.pending_bank_account_id:
            raise UserError("No pending bank change to approve.")

        # Log the override
        self.message_post(
            body=f"Bank change cooling off period overridden by {self.env.user.name}",
            message_type='notification',
        )

        # Activate immediately
        self.write({
            'bank_account_id': self.pending_bank_account_id.id,
            'pending_bank_account_id': False,
            'bank_change_token': False,
            'bank_change_token_expiry': False,
        })

        # Send confirmation email
        template = self.env.ref('property_fielder_owner_portal.email_bank_change_confirmed')
        template.send_mail(self.id)
```

### 7.5 Resend Bank Verification Email

**Portal route to resend verification email:**

```python
@http.route('/my/account/bank/resend', type='http', auth='user', methods=['POST'])
def bank_resend_verification(self, **post):
    """Resend bank change verification email."""
    partner = request.env.user.partner_id

    if not partner.pending_bank_account_id:
        return request.redirect('/my/account?error=no_pending_change')

    # Generate new token (extends expiry)
    token = secrets.token_urlsafe(32)
    partner.sudo().write({
        'bank_change_token': token,
        'bank_change_token_expiry': fields.Datetime.now() + timedelta(hours=48),
    })

    # Resend verification email
    template = request.env.ref('property_fielder_owner_portal.email_bank_change_verify')
    template.sudo().send_mail(partner.id)

    return request.redirect('/my/account?message=verification_resent')
```

---

## 8. Joint Ownership Statement Generation

### 8.1 Statement Wizard with Percentage Splits

```python
class OwnerStatementWizard(models.TransientModel):
    _inherit = 'property_fielder.owner.statement.wizard'

    def action_generate_statements(self):
        """
        Generate statements for all owners, splitting by ownership percentage.
        """
        Statement = self.env['property_fielder.owner.statement']
        Ownership = self.env['property_fielder.property.ownership']

        for owner in self.owner_ids:
            # Get all properties where this owner has active ownership
            ownerships = Ownership.search([
                ('owner_id', '=', owner.id),
                ('state', '=', 'active'),
            ])

            if not ownerships:
                continue

            # Get previous statement closing balance
            prev_statement = Statement.search([
                ('owner_id', '=', owner.id),
                ('state', 'in', ['paid', 'locked']),
            ], order='period_end desc', limit=1)
            opening_balance = prev_statement.closing_balance if prev_statement else 0.0

            # Create statement
            statement = Statement.create({
                'owner_id': owner.id,
                'period_start': self.period_start,
                'period_end': self.period_end,
                'opening_balance': opening_balance,
            })

            # Populate lines with percentage splits
            for ownership in ownerships:
                property_id = ownership.property_id
                share = ownership.ownership_percentage / 100.0

                # Get rent for this property in period
                rent_lines = self._get_rent_lines(property_id, self.period_start, self.period_end)
                for line in rent_lines:
                    self.env['property_fielder.owner.statement.line'].create({
                        'statement_id': statement.id,
                        'property_id': property_id.id,
                        'line_type': 'rent',
                        'description': f"Rent ({ownership.ownership_percentage}% share)",
                        'amount': line.amount * share,
                        'move_line_id': line.id,
                    })

                # Get maintenance costs for this property
                maintenance_lines = self._get_maintenance_lines(property_id, self.period_start, self.period_end)
                for line in maintenance_lines:
                    self.env['property_fielder.owner.statement.line'].create({
                        'statement_id': statement.id,
                        'property_id': property_id.id,
                        'line_type': 'maintenance',
                        'description': f"Maintenance ({ownership.ownership_percentage}% share)",
                        'amount': -line.amount * share,  # Negative for expense
                        'is_tax_deductible': True,
                        'move_line_id': line.id,
                    })

            # Calculate totals
            statement._compute_totals()

        return {'type': 'ir.actions.act_window_close'}
```

### 8.2 Ownership Percentage Validation

```python
class PropertyOwnership(models.Model):
    _name = 'property_fielder.property.ownership'
    _inherit = ['mail.thread']

    @api.constrains('property_id', 'ownership_percentage')
    def _check_total_ownership(self):
        """Ensure total ownership for a property doesn't exceed 100%."""
        for rec in self:
            total = sum(
                self.search([
                    ('property_id', '=', rec.property_id.id),
                    ('state', '=', 'active'),
                ]).mapped('ownership_percentage')
            )
            if total > 100:
                raise ValidationError(
                    f"Total ownership for {rec.property_id.name} exceeds 100% ({total}%)"
                )
```

### 8.3 Account Move Line Extension (Double-Payout Prevention)

**CRITICAL:** Prevent the same accounting line from being included in multiple statements.

```python
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_included_in_statement = fields.Boolean(
        default=False,
        help="True if this line has been included in an owner statement. "
             "Prevents double-payout."
    )
    statement_line_ids = fields.One2many(
        'property_fielder.owner.statement.line',
        'move_line_id',
        string='Statement Lines'
    )
    amount_statemented = fields.Monetary(
        compute='_compute_amount_statemented',
        store=True,
        help="Total amount allocated to statements (for joint ownership)"
    )
    amount_residual_statement = fields.Monetary(
        compute='_compute_amount_statemented',
        store=True,
        help="Amount remaining to be allocated to statements"
    )

    @api.depends('statement_line_ids.amount_allocated')
    def _compute_amount_statemented(self):
        for rec in self:
            rec.amount_statemented = sum(rec.statement_line_ids.mapped('amount_allocated'))
            rec.amount_residual_statement = abs(rec.balance) - abs(rec.amount_statemented)
```

### 8.4 Statement Line Allocation Logic

```python
class OwnerStatementLine(models.Model):
    _inherit = 'property_fielder.owner.statement.line'

    @api.constrains('move_line_id', 'amount_allocated')
    def _check_allocation(self):
        """Ensure we don't over-allocate from a move line."""
        for rec in self:
            if rec.move_line_id:
                total_allocated = sum(
                    rec.move_line_id.statement_line_ids.mapped('amount_allocated')
                )
                if abs(total_allocated) > abs(rec.move_line_id.balance):
                    raise ValidationError(
                        f"Cannot allocate more than the move line balance. "
                        f"Available: {rec.move_line_id.amount_residual_statement}"
                    )
```

---

## 9. QWeb Report Templates

### 9.1 Owner Statement PDF Report

**Template: `property_fielder_owner_portal.report_owner_statement`**

```xml
<template id="report_owner_statement_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <!-- Header with CMP Footer -->
                    <div class="header">
                        <h2>Owner Statement</h2>
                        <p>Statement Reference: <t t-esc="doc.name"/></p>
                        <p>Period: <t t-esc="doc.period_start"/> to <t t-esc="doc.period_end"/></p>
                    </div>

                    <!-- Owner Details -->
                    <div class="owner-details">
                        <strong><t t-esc="doc.owner_id.name"/></strong>
                        <t t-if="doc.owner_id.is_non_resident_landlord">
                            <span class="badge">NRL</span>
                        </t>
                    </div>

                    <!-- Statement Lines Table -->
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Property</th>
                                <th>Description</th>
                                <th class="text-right">Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            <t t-foreach="doc.line_ids" t-as="line">
                                <tr>
                                    <td><t t-esc="line.property_id.name"/></td>
                                    <td><t t-esc="line.description"/></td>
                                    <td class="text-right">
                                        <t t-esc="line.amount" t-options="{'widget': 'monetary'}"/>
                                    </td>
                                </tr>
                            </t>
                        </tbody>
                    </table>

                    <!-- NRL Tax Deduction Display -->
                    <t t-if="doc.owner_id.is_non_resident_landlord and doc.nrl_tax_withheld > 0">
                        <div class="nrl-section">
                            <p><strong>NRL Tax Withheld (20%):</strong>
                                <t t-esc="doc.nrl_tax_withheld" t-options="{'widget': 'monetary'}"/>
                            </p>
                            <p class="small">Tax calculated on taxable income of
                                <t t-esc="doc.taxable_income" t-options="{'widget': 'monetary'}"/>
                            </p>
                        </div>
                    </t>

                    <!-- Totals -->
                    <div class="totals">
                        <p>Opening Balance: <t t-esc="doc.opening_balance" t-options="{'widget': 'monetary'}"/></p>
                        <p>Gross Rent: <t t-esc="doc.gross_rent" t-options="{'widget': 'monetary'}"/></p>
                        <p>Management Fee: <t t-esc="doc.management_fee" t-options="{'widget': 'monetary'}"/></p>
                        <p>Maintenance: <t t-esc="doc.maintenance_costs" t-options="{'widget': 'monetary'}"/></p>
                        <p><strong>Net Payable: <t t-esc="doc.net_payable" t-options="{'widget': 'monetary'}"/></strong></p>
                        <p>Closing Balance: <t t-esc="doc.closing_balance" t-options="{'widget': 'monetary'}"/></p>
                    </div>

                    <!-- CMP Footer (Required by UK Trading Standards) -->
                    <div class="cmp-footer">
                        <p class="small">
                            Client Money Protection provided by:
                            <t t-esc="doc.company_id.cmp_provider_name"/>
                            (Certificate: <t t-esc="doc.company_id.cmp_certificate_number"/>)
                        </p>
                        <p class="small">
                            Member of: <t t-esc="doc.company_id.redress_scheme_name"/>
                        </p>
                    </div>
                </div>
            </t>
        </t>
    </t>
</template>
```

### 9.2 Company CMP Fields

```python
class ResCompany(models.Model):
    _inherit = 'res.company'

    cmp_provider_name = fields.Char(string='CMP Provider')
    cmp_certificate_number = fields.Char(string='CMP Certificate Number')
    cmp_certificate_url = fields.Char(string='CMP Certificate URL')
    redress_scheme_name = fields.Char(string='Redress Scheme')
    client_money_journal_id = fields.Many2one(
        'account.journal',
        string='Client Money Journal',
        help="Journal for client money transactions (CMP compliance)"
    )
```

---

## 10. Line Item Dispute Workflow

### 10.1 Portal Route for Querying Line Items

```python
@http.route('/my/statements/<int:statement_id>/line/<int:line_id>/query',
            type='http', auth='user', methods=['POST'])
def query_statement_line(self, statement_id, line_id, **post):
    """Owner queries a statement line item."""
    statement = request.env['property_fielder.owner.statement'].sudo().browse(statement_id)

    # Security check
    if statement.owner_id != request.env.user.partner_id:
        return request.redirect('/my/statements?error=access_denied')

    if statement.state == 'locked':
        return request.redirect(f'/my/statements/{statement_id}?error=statement_locked')

    line = statement.line_ids.filtered(lambda l: l.id == line_id)
    if not line:
        return request.redirect(f'/my/statements/{statement_id}?error=line_not_found')

    line.sudo().write({
        'dispute_state': 'queried',
        'dispute_reason': post.get('reason'),
        'dispute_date': fields.Datetime.now(),
    })

    # Notify property manager
    template = request.env.ref('property_fielder_owner_portal.email_line_item_query')
    template.sudo().send_mail(line.id)

    return request.redirect(f'/my/statements/{statement_id}?message=query_submitted')
```

### 10.2 Admin Resolution

```python
class OwnerStatementLine(models.Model):
    _inherit = 'property_fielder.owner.statement.line'

    def action_resolve_dispute(self, resolution_notes):
        """Admin resolves a line item dispute."""
        self.ensure_one()
        if self.dispute_state != 'queried':
            raise UserError("Only queried items can be resolved.")

        self.write({
            'dispute_state': 'resolved',
            'dispute_resolution': resolution_notes,
            'resolved_by': self.env.user.id,
        })

        # Notify owner
        template = self.env.ref('property_fielder_owner_portal.email_dispute_resolved')
        template.send_mail(self.id)
```

### 10.3 Dispute Release Mechanism

**Release disputed amounts back to the ledger for re-allocation:**

```python
class OwnerStatementLine(models.Model):
    _inherit = 'property_fielder.owner.statement.line'

    def action_release_disputed_amount(self):
        """
        Release a disputed line item back to the ledger.
        This allows the amount to be re-allocated in a future statement.
        """
        self.ensure_one()
        if self.dispute_state not in ['queried', 'resolved']:
            raise UserError("Only disputed items can be released.")

        if self.move_line_id:
            # Reduce the allocated amount on the move line
            self.move_line_id.is_included_in_statement = False

        # Mark as released and zero out the amount
        original_amount = self.amount
        self.write({
            'dispute_state': 'released',
            'amount': 0,
            'dispute_resolution': f'Released {original_amount} back to ledger',
            'resolved_by': self.env.user.id,
        })

        # Recalculate statement totals
        self.statement_id._compute_totals()

        # Log the release
        self.statement_id.message_post(
            body=f"Line item released: {self.description} ({original_amount})"
        )
```

### 10.4 Retained Amount Ledger Logic

**Track retained amounts for future expenses:**

```python
class OwnerStatement(models.Model):
    _inherit = 'property_fielder.owner.statement'

    retained_reason = fields.Text(
        string='Retention Reason',
        help="Reason for retaining funds (e.g., upcoming repairs)"
    )
    retained_released_date = fields.Date(
        string='Retention Released',
        help="Date when retained amount was released to owner"
    )

    def action_release_retained(self):
        """Release retained amount to owner in next statement."""
        self.ensure_one()
        if self.retained_amount <= 0:
            raise UserError("No retained amount to release.")

        # Create a credit line in the next statement
        next_statement = self.env['property_fielder.owner.statement'].search([
            ('owner_id', '=', self.owner_id.id),
            ('state', '=', 'draft'),
        ], limit=1)

        if next_statement:
            self.env['property_fielder.owner.statement.line'].create({
                'statement_id': next_statement.id,
                'line_type': 'other',
                'description': f'Released retention from {self.name}',
                'amount': self.retained_amount,
            })

        self.retained_released_date = fields.Date.today()
        self.message_post(body=f"Retained amount of {self.retained_amount} released")
```

---

## 11. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models defined | ✅ Complete |
| **Joint ownership model (property.ownership)** | ✅ Added |
| **Ownership percentage validation** | ✅ Added |
| **Statement wizard with percentage splits** | ✅ Added |
| **payment_id on statement** | ✅ Added |
| **Statement locking on payment** | ✅ Added |
| **Line item dispute workflow** | ✅ Added |
| **Dispute portal route** | ✅ Added |
| **Admin dispute resolution** | ✅ Added |
| **Dispute release mechanism** | ✅ Added |
| **Admin override for bank cooling off** | ✅ Added |
| **Resend verification email route** | ✅ Added |
| **Compliance dashboard** | ✅ Added |
| **Annual tax summary with Cash Basis** | ✅ Added |
| **Opening/closing balance on statements** | ✅ Added |
| **Retained amount field** | ✅ Added |
| **Retained amount release logic** | ✅ Added |
| **NRL tax on TAXABLE INCOME (corrected)** | ✅ Fixed |
| **is_tax_deductible on statement lines** | ✅ Added |
| **Statement generation wizard** | ✅ Added |
| **Property performance metrics** | ✅ Added |
| **Document access matrix** | ✅ Added |
| **Notification preferences** | ✅ Added |
| **Bank security fields (pending/token)** | ✅ Added |
| **Bank update route with verification** | ✅ Added |
| **Statement period continuity constraint** | ✅ Added |
| **Portal Chatter integration** | ✅ Added |
| **QWeb report template with CMP footer** | ✅ Added |
| **NRL deduction display in report** | ✅ Added |
| **Company CMP fields** | ✅ Added |
| **action_mark_paid → account.payment** | ✅ Added |
| **amount_residual_statement on move.line** | ✅ Added |
| **is_included_in_statement flag** | ✅ Added |
| **amount_allocated on statement.line** | ✅ Added |
| **Allocation constraint (no over-allocate)** | ✅ Added |
| Portal routes specified | ✅ Complete |
| NRL compliance | ✅ Complete |
| Approval workflow | ✅ Complete |
| **Overall** | ✅ Build Ready (90%+) |

