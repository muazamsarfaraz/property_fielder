# PRD: Property Fielder Inventory Management

**Addon Name:** `property_fielder_inventory_management`  
**Version:** 1.0.0  
**Status:** 🔜 Planned  
**Layer:** Business (Layer 4)  
**Phase:** Phase D (Advanced Features)  
**Effort:** 20-30 hours  

---

## 1. Overview

Property inventory and condition reports for check-in/check-out.

### 1.1 Purpose
Create and manage detailed property inventories with condition reports at check-in and check-out for deposit dispute resolution.

### 1.2 Target Users
- Inventory Clerks
- Property Managers
- Tenants (acknowledgment)

---

## 2. Dependencies

```python
depends = [
    'base',
    'mail',  # Chatter for inventory tracking
    'account',  # For deposit deduction journal entries
    'portal',  # Tenant review portal
    'property_fielder_property_leasing',
    'property_fielder_property_maintenance',  # For work order creation
]
```

---

## 3. Data Models

### 3.1 `property_fielder.inventory`

**Inherits mail.thread for audit trail.**

```python
class Inventory(models.Model):
    _name = 'property_fielder.inventory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
```

| Field | Type | Description |
|-------|------|-------------|
| `property_id` | Many2one → property | Property |
| `template_id` | Many2one → inventory.template | **Master template** |
| `inventory_type` | Selection | check_in/interim/check_out |
| `tenancy_id` | Many2one → tenancy | Related tenancy |
| `report_date` | Datetime | Report date |
| `clerk_id` | Many2one → res.partner | Inventory clerk |
| `state` | Selection | **draft/completed/tenant_review/signed** |
| `tenant_review_sent` | Datetime | **When sent to tenant for review** |
| `tenant_review_deadline` | Date | **Deadline for tenant response (7 days)** |
| `tenant_comments` | Text | **Tenant's comments/disputes** |
| `tenant_present` | Boolean | Tenant was present |
| `tenant_signature` | Binary | **Tenant signature (PNG image)** |
| `tenant_signed_date` | Datetime | **When tenant signed** |
| `tenant_signature_ip` | Char | **IP address when tenant signed** |
| `tenant_signature_device` | Char | **Device info when tenant signed** |
| `tenant_signature_lat` | Float | **GPS latitude when tenant signed** |
| `tenant_signature_lng` | Float | **GPS longitude when tenant signed** |
| `clerk_signature` | Binary | **Clerk signature (PNG image)** |
| `clerk_signed_date` | Datetime | **When clerk signed** |
| `clerk_signature_ip` | Char | **IP address when clerk signed** |
| `clerk_signature_device` | Char | **Device info when clerk signed** |
| `room_ids` | One2many → inventory.room | Rooms |
| `notes` | Text | General notes |
| `meter_gas_reading` | Char | Gas meter reading |
| `meter_gas_serial` | Char | **Gas meter serial number** |
| `meter_gas_photo_id` | Many2one → ir.attachment | **Gas meter photo** |
| `meter_electric_reading` | Char | Electric meter reading |
| `meter_electric_serial` | Char | **Electric meter serial number** |
| `meter_electric_photo_id` | Many2one → ir.attachment | **Electric meter photo** |
| `meter_water_reading` | Char | Water meter reading |
| `meter_water_serial` | Char | **Water meter serial number** |
| `meter_water_photo_id` | Many2one → ir.attachment | **Water meter photo** |
| `pdf_report_id` | Many2one → ir.attachment | **Generated PDF report** |
| `smoke_alarms_tested` | Boolean | Smoke alarms tested |
| `co_alarms_tested` | Boolean | CO alarms tested |
| `habitable_condition` | Boolean | **FFHH: Property fit for human habitation** |
| `keys_count` | Integer | Keys provided |
| `fobs_count` | Integer | Fobs provided |

**FFHH (Fitness for Human Habitation) - Homes (Fitness for Human Habitation) Act 2018:**
- Landlord must ensure property is fit for human habitation at start and throughout tenancy
- Inventory check-in is the ideal time to document this
- If `habitable_condition = False`, creates compliance alert

### 3.2 `property_fielder.inventory.room`

Room in inventory.

| Field | Type | Description |
|-------|------|-------------|
| `inventory_id` | Many2one → inventory | Parent inventory |
| `origin_room_id` | Many2one → self | **Link to check-in room (for check-out)** |
| `room_type_id` | Many2one → room.type | **Dynamic room type** |
| `room_name` | Char | Room name |
| `sequence` | Integer | Display order |
| `item_ids` | One2many → inventory.item | Items in room |
| `overall_condition` | Selection | **excellent/good/fair/poor** |
| `overall_cleanliness` | Selection | **clean/acceptable/dirty** |
| `notes` | Text | Room notes |
| `photo_ids` | Many2many → ir.attachment | Room photos |

### 3.3 `property_fielder.room.type`

Dynamic room types (configurable).

| Field | Type | Description |
|-------|------|-------------|
| `name` | Char | Room type name |
| `code` | Char | Code (bedroom, bathroom, etc.) |
| `default_items` | Text | Default items (JSON) |

### 3.4 `property_fielder.inventory.item`

Inventory item.

| Field | Type | Description |
|-------|------|-------------|
| `room_id` | Many2one → room | Parent room |
| `origin_item_id` | Many2one → inventory.item | **Link to check-in item (for check-out comparison)** |
| `item_name` | Char | Item name |
| `quantity` | Integer | Quantity |
| `condition` | Selection | new/good/fair/poor/damaged |
| `cleanliness` | Selection | **clean/acceptable/dirty** |
| `description` | Text | Condition description |
| `photo_ids` | Many2many → ir.attachment | **Item photos (standardized to ir.attachment)** |
| `is_fixture` | Boolean | Permanent fixture |
| `checkout_condition` | Selection | same/improved/damaged/missing |
| `checkout_notes` | Text | Check-out notes |
| `replacement_cost` | Monetary | **Cost to replace item (for betterment calc)** |
| `deposit_deduction` | Monetary | **Deduction amount (Monetary)** |
| `currency_id` | Many2one → res.currency | **Related to inventory_id.property_id.currency_id** |
| `create_maintenance` | Boolean | **Flag to create maintenance work order** |

```python
class InventoryItem(models.Model):
    _name = 'property_fielder.inventory.item'

    currency_id = fields.Many2one(
        'res.currency',
        related='room_id.inventory_id.property_id.currency_id',
        readonly=True,
        store=True,
        help="Inherited from property to avoid redundancy"
    )
```

---

## 4. Key Features

### 4.1 Check-In Inventory
- Room-by-room walkthrough
- Item listing with condition
- Photo evidence
- Meter readings
- Tenant acknowledgment

### 4.2 Check-Out Comparison
- Side-by-side comparison
- Condition change flagging
- Damage assessment
- Deduction calculation

### 4.3 Deposit Resolution
- Itemized deductions
- Photo evidence
- Dispute support
- TDS/DPS report format

### 4.4 Templates
- Property-specific templates
- Item library
- Default room layouts

### 4.5 Mobile Capture & Offline Strategy

**Mobile Workflow:**

- Room-by-room mobile workflow
- Photo capture per item
- Offline support
- Signature capture

**Offline Strategy:**

```dart
// Flutter mobile app - Inventory offline handling
class InventoryOfflineManager {
  final HiveBox<InventoryDraft> _draftsBox;

  /// Save inventory draft locally when offline
  Future<void> saveDraft(InventoryDraft draft) async {
    await _draftsBox.put(draft.localId, draft);
  }

  /// Sync all pending drafts when online
  Future<void> syncPendingDrafts() async {
    final pending = _draftsBox.values.where((d) => !d.synced);
    for (final draft in pending) {
      try {
        // Upload photos first (get attachment IDs)
        final photoIds = await _uploadPhotos(draft.photos);

        // Create inventory record via Odoo API
        final inventoryId = await _odooApi.createInventory({
          'property_id': draft.propertyId,
          'inventory_type': draft.type,
          'room_ids': draft.rooms.map((r) => r.toOdooFormat(photoIds)).toList(),
        });

        draft.synced = true;
        draft.odooId = inventoryId;
        await _draftsBox.put(draft.localId, draft);
      } catch (e) {
        // Keep in queue for retry
        _logger.error('Sync failed for ${draft.localId}: $e');
      }
    }
  }

  /// Compress photos before upload (max 1024px, 80% quality)
  Future<List<int>> _compressPhoto(File photo) async {
    final image = await FlutterImageCompress.compressWithFile(
      photo.path,
      minWidth: 1024,
      minHeight: 1024,
      quality: 80,
    );
    return image ?? [];
  }
}
```

**Offline Data Storage:**
- SQLite/Hive for structured data
- Local file storage for photos (compressed)
- Queue-based sync on reconnection
- Conflict resolution: Server wins (with local backup)

### 4.6 Fair Wear and Tear (Editable)

**IMPORTANT: Fair wear allowance should be EDITABLE, not strictly computed.**

UK deposit adjudicators (TDS, DPS, MyDeposits) don't use rigid formulas - they consider:
- Item age and expected lifespan
- Quality of original item
- Tenant's care and usage
- Landlord's maintenance history

```python
class InventoryItem(models.Model):
    _inherit = 'property_fielder.inventory.item'

    tenancy_length_months = fields.Integer(
        related='room_id.inventory_id.tenancy_id.length_months'
    )
    fair_wear_allowance = fields.Float(
        string='Fair Wear Allowance %',
        help="Percentage reduction for fair wear and tear (editable)"
    )
    fair_wear_suggested = fields.Float(
        compute='_compute_fair_wear_suggested',
        help="Suggested allowance based on tenancy length"
    )

    @api.depends('tenancy_length_months', 'is_fixture')
    def _compute_fair_wear_suggested(self):
        """
        SUGGESTED fair wear allowance based on tenancy length.
        Clerk can override with actual fair_wear_allowance field.
        """
        for rec in self:
            years = rec.tenancy_length_months / 12
            if rec.is_fixture:
                rec.fair_wear_suggested = min(years * 5, 25)  # 5% per year, max 25%
            else:
                rec.fair_wear_suggested = min(years * 10, 50)  # 10% per year, max 50%

    @api.onchange('fair_wear_suggested')
    def _onchange_fair_wear_suggested(self):
        """Pre-populate editable field with suggested value."""
        if not self.fair_wear_allowance:
            self.fair_wear_allowance = self.fair_wear_suggested
```

### 4.7 Betterment Calculation

| Scenario | Calculation |
|----------|-------------|
| Item damaged, 3 years old | Replacement cost - fair wear (30%) |
| Carpet stained, 5 years old | Replacement cost - fair wear (50%) |
| Fixture broken, 2 years old | Replacement cost - fair wear (10%) |

---

## 5. Deposit Scheme Integration

### 5.1 TDS/DPS Report Format (Using origin_item_id)

**IMPORTANT: Use `origin_item_id` for reliable item linking, NOT string matching.**

String matching is fragile - items may be renamed or have similar names.

```python
class Inventory(models.Model):
    _inherit = 'property_fielder.inventory'

    def generate_deposit_dispute_report(self):
        """Generate report for TDS/DPS dispute using origin_item_id linking."""
        deductions = []
        for room in self.room_ids:
            for item in room.item_ids:
                if item.checkout_condition in ['damaged', 'missing']:
                    # Use origin_item_id for reliable linking
                    checkin_item = item.origin_item_id
                    if not checkin_item:
                        # Fallback: log warning, item may have been added at checkout
                        _logger.warning(f"No origin_item_id for {item.item_name}")
                        continue

                    deductions.append({
                        'item': item.item_name,
                        'checkin_condition': checkin_item.condition,
                        'checkin_photos': checkin_item.photo_ids.ids,
                        'checkout_condition': item.checkout_condition,
                        'checkout_photos': item.photo_ids.ids,
                        'deduction': item.deposit_deduction,
                        'fair_wear_allowance': item.fair_wear_allowance,
                        'net_deduction': item.deposit_deduction * (1 - item.fair_wear_allowance / 100),
                    })
        return deductions

    def action_create_checkout_from_checkin(self):
        """
        Create check-out inventory by copying check-in items
        with origin_item_id and origin_room_id links for comparison.

        IMPORTANT: Uses ID-based linking, NOT string matching.
        """
        self.ensure_one()
        if self.inventory_type != 'check_in':
            raise UserError("Can only create check-out from check-in inventory")

        checkout = self.create({
            'property_id': self.property_id.id,
            'tenancy_id': self.tenancy_id.id,
            'inventory_type': 'check_out',
            'report_date': fields.Datetime.now(),
            'state': 'draft',
            'template_id': self.template_id.id,
        })

        # Create rooms with origin_room_id linking (NOT string matching)
        for checkin_room in self.room_ids:
            checkout_room = self.env['property_fielder.inventory.room'].create({
                'inventory_id': checkout.id,
                'room_type_id': checkin_room.room_type_id.id,
                'room_name': checkin_room.room_name,
                'sequence': checkin_room.sequence,
                'origin_room_id': checkin_room.id,  # ID-based link
            })

            # Create items with origin_item_id linking
            for checkin_item in checkin_room.item_ids:
                self.env['property_fielder.inventory.item'].create({
                    'room_id': checkout_room.id,
                    'item_name': checkin_item.item_name,
                    'quantity': checkin_item.quantity,
                    'is_fixture': checkin_item.is_fixture,
                    'origin_item_id': checkin_item.id,  # ID-based link
                    # Copy check-in condition for reference
                    'condition': checkin_item.condition,
                    'cleanliness': checkin_item.cleanliness,
                })

        return checkout
```

### 5.2 Accounting Integration for Deposit Deductions

```python
class Inventory(models.Model):
    _inherit = 'property_fielder.inventory'

    total_deductions = fields.Monetary(
        compute='_compute_total_deductions',
        store=True,
        string='Total Deductions'
    )
    deduction_invoice_id = fields.Many2one(
        'account.move',
        string='Deduction Invoice'
    )

    @api.depends('room_ids.item_ids.deposit_deduction', 'room_ids.item_ids.fair_wear_allowance')
    def _compute_total_deductions(self):
        for rec in self:
            total = 0.0
            for room in rec.room_ids:
                for item in room.item_ids:
                    if item.deposit_deduction:
                        net = item.deposit_deduction * (1 - (item.fair_wear_allowance or 0) / 100)
                        total += net
            rec.total_deductions = total

    def action_post_deductions(self):
        """
        Post deposit deductions to accounting.
        Creates journal entry to transfer from deposit liability to income.
        """
        self.ensure_one()
        if self.inventory_type != 'check_out':
            raise UserError("Can only post deductions from check-out inventory")
        if not self.total_deductions:
            raise UserError("No deductions to post")

        # Get deposit account from tenancy
        deposit_account = self.tenancy_id.deposit_account_id
        income_account = self.env['ir.config_parameter'].sudo().get_param(
            'property_fielder.deposit_deduction_income_account'
        )

        move = self.env['account.move'].create({
            'move_type': 'entry',
            'ref': f'Deposit deductions: {self.property_id.name}',
            'line_ids': [
                (0, 0, {
                    'account_id': deposit_account.id,
                    'debit': self.total_deductions,
                    'credit': 0,
                    'name': 'Deposit deduction - damage/cleaning',
                }),
                (0, 0, {
                    'account_id': int(income_account),
                    'debit': 0,
                    'credit': self.total_deductions,
                    'name': 'Deposit deduction income',
                }),
            ]
        })
        move.action_post()
        self.deduction_invoice_id = move.id
        return move
```

### 5.3 Maintenance Trigger for Damaged Items

```python
class InventoryItem(models.Model):
    _inherit = 'property_fielder.inventory.item'

    maintenance_work_order_id = fields.Many2one(
        'property_fielder.work.order',
        string='Maintenance Work Order'
    )

    def action_create_maintenance(self):
        """Create maintenance work order for damaged item."""
        self.ensure_one()
        if self.checkout_condition not in ['damaged', 'missing']:
            raise UserError("Can only create maintenance for damaged/missing items")

        work_order = self.env['property_fielder.work.order'].create({
            'property_id': self.room_id.inventory_id.property_id.id,
            'title': f'Repair/Replace: {self.item_name}',
            'description': f'Damage noted at check-out: {self.checkout_notes}',
            'priority': 'medium',
            'source': 'inventory_checkout',
        })
        self.maintenance_work_order_id = work_order.id
        self.create_maintenance = False
        return work_order
```

---

## 6. Master Inventory Template

### 6.1 Template Model

```python
class InventoryTemplate(models.Model):
    _name = 'property_fielder.inventory.template'
    _description = 'Master Inventory Template'

    name = fields.Char(required=True)
    property_type = fields.Selection([
        ('flat', 'Flat'),
        ('house', 'House'),
        ('hmo', 'HMO'),
        ('studio', 'Studio'),
    ])
    room_template_ids = fields.One2many(
        'property_fielder.inventory.room.template',
        'template_id'
    )

    def apply_to_inventory(self, inventory):
        """Copy template rooms/items to inventory."""
        for room_tmpl in self.room_template_ids:
            room = self.env['property_fielder.inventory.room'].create({
                'inventory_id': inventory.id,
                'room_type': room_tmpl.room_type,
                'room_name': room_tmpl.room_name,
                'sequence': room_tmpl.sequence,
            })
            for item_tmpl in room_tmpl.item_template_ids:
                self.env['property_fielder.inventory.item'].create({
                    'room_id': room.id,
                    'item_name': item_tmpl.item_name,
                    'is_fixture': item_tmpl.is_fixture,
                })
```

---

## 7. Mobile App API Endpoints

**Required for Flutter mobile app synchronization:**

```python
from odoo import http
from odoo.http import request

class InventoryController(http.Controller):

    @http.route('/api/inventory/get_template', type='json', auth='user')
    def get_template(self, property_id):
        """Get inventory template for property type."""
        property_rec = request.env['property_fielder.property'].browse(property_id)
        template = request.env['property_fielder.inventory.template'].search([
            ('property_type', '=', property_rec.property_type)
        ], limit=1)
        return template.read(['name', 'room_template_ids'])

    @http.route('/api/inventory/sync', type='json', auth='user')
    def sync_inventory(self, inventory_data):
        """Sync inventory data from mobile (offline support)."""
        inventory_id = inventory_data.get('id')
        if inventory_id:
            inventory = request.env['property_fielder.inventory'].browse(inventory_id)
            inventory.write(inventory_data)
        else:
            inventory = request.env['property_fielder.inventory'].create(inventory_data)
        return {'id': inventory.id, 'state': inventory.state}

    @http.route('/api/inventory/upload_image', type='http', auth='user', methods=['POST'])
    def upload_image(self, inventory_id, room_id=None, item_id=None, **kwargs):
        """Upload image to inventory room or item."""
        file = kwargs.get('file')
        if not file:
            return {'error': 'No file provided'}

        attachment = request.env['ir.attachment'].create({
            'name': file.filename,
            'datas': base64.b64encode(file.read()),
            'res_model': 'property_fielder.inventory.item' if item_id else 'property_fielder.inventory.room',
            'res_id': item_id or room_id,
        })
        return {'attachment_id': attachment.id}
```

---

## 8. Gemini Review Status

| Criteria | Status |
|----------|--------|
| Data models complete | ✅ Complete |
| **account dependency added** | ✅ Added |
| **portal dependency added** | ✅ Added |
| **property_fielder_maintenance dependency** | ✅ Added |
| **Meter serial number fields** | ✅ Added |
| **Meter photo fields** | ✅ Added |
| **Tenant review state in workflow** | ✅ Added |
| **Tenant review deadline (7 days)** | ✅ Added |
| **Tenant comments field** | ✅ Added |
| **PDF report field (ir.attachment)** | ✅ Added |
| **origin_room_id for room linking** | ✅ Added |
| **ID-based linking (not string matching)** | ✅ Fixed |
| **Signature as Binary field (not separate model)** | ✅ Fixed |
| **origin_item_id for check-out linking** | ✅ Added |
| **ir.attachment for ALL photos (standardized)** | ✅ Fixed |
| **Fair wear allowance EDITABLE (not computed)** | ✅ Fixed |
| **Maintenance trigger for damaged items** | ✅ Added |
| **Dynamic room_type_id** | ✅ Added |
| **Room overall condition/cleanliness** | ✅ Added |
| **mail.thread inheritance** | ✅ Added |
| **Master inventory template** | ✅ Added |
| **Cleanliness field** | ✅ Added |
| **Monetary field for deductions** | ✅ Fixed |
| **Fair wear suggested vs actual** | ✅ Added |
| **Betterment calculation** | ✅ Added |
| **action_create_checkout_from_checkin** | ✅ Added |
| **replacement_cost field** | ✅ Added |
| **action_post_deductions() accounting** | ✅ Added |
| **FFHH habitable_condition field** | ✅ Added |
| **Mobile/Offline strategy defined** | ✅ Added |
| **Signature metadata (IP, device, GPS)** | ✅ Added |
| **currency_id as related field (optimization)** | ✅ Added |
| **Mobile API endpoints defined** | ✅ Added |
| Check-in workflow clear | ✅ Complete |
| Check-out comparison | ✅ Complete |
| TDS/DPS report format | ✅ Complete |
| Deposit integration | ✅ Complete |
| **Overall** | ✅ Build Ready (90%+) |
