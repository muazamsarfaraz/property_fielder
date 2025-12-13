# Odoo 19 Migration Guide & Best Practices

**Document Version:** 1.0  
**Date:** 2025-12-09  
**Project:** Property Fielder  
**Odoo Version:** 19.0 (December 2024 Release)

---

## Table of Contents

1. [Breaking Changes Summary](#breaking-changes-summary)
2. [View Syntax Changes](#view-syntax-changes)
3. [Security Groups Changes](#security-groups-changes)
4. [Controller Changes](#controller-changes)
5. [Conversion Patterns](#conversion-patterns)
6. [Best Practices](#best-practices)
7. [Common Pitfalls](#common-pitfalls)
8. [Resources](#resources)

---

## Breaking Changes Summary

### Critical Changes (Will Break Installation)

| Change | Odoo Version | Impact | Fix Required |
|--------|--------------|--------|--------------|
| `attrs` attribute deprecated | v17+ (removed v19) | HIGH | Convert to `invisible`/`readonly`/`required` |
| `states` attribute deprecated | v17+ (removed v19) | HIGH | Convert to `invisible` |
| Security groups structure | v19 | HIGH | Change `ir.module.category` → `res.groups.privilege` |
| View type `tree` renamed | v19 | HIGH | Change `<tree>` → `<list>` |
| Search view `<group>` syntax | v19 | MEDIUM | Remove `expand` and `string` attributes |
| Controller route type | v17+ | LOW | Change `type='json'` → `type='jsonrpc'` |
| Context variable validation | v19 | MEDIUM | Replace `active_id` with `id` |
| **`create()` method signature** | **v19** | **HIGH** | **Use `@api.model_create_multi` and `vals_list`** |
| **Kanban template name** | **v19** | **HIGH** | **Change `t-name="kanban-box"` → `t-name="card"`** |
| **Action `view_mode` field** | **v19** | **HIGH** | **Change `tree` → `list` in action definitions** |

---

## View Syntax Changes

### 1. attrs Attribute Removal (CRITICAL)

**Old Syntax (Odoo ≤16):**
```xml
<button name="action_renew" 
        attrs="{'invisible': [('status', 'not in', ['expiring_soon', 'expired'])]}"/>

<field name="expiry_date" 
       attrs="{'readonly': [('state', '=', 'done')], 
               'required': [('type', '=', 'mandatory')]}"/>
```

**New Syntax (Odoo 19):**
```xml
<button name="action_renew" 
        invisible="status not in ['expiring_soon', 'expired']"/>

<field name="expiry_date" 
       readonly="state == 'done'" 
       required="type == 'mandatory'"/>
```

**Conversion Rules:**

| Old Domain Operator | New Expression Operator |
|---------------------|-------------------------|
| `('field', '=', value)` | `field == value` |
| `('field', '!=', value)` | `field != value` |
| `('field', '<', value)` | `field < value` |
| `('field', '>', value)` | `field > value` |
| `('field', '<=', value)` | `field <= value` |
| `('field', '>=', value)` | `field >= value` |
| `('field', 'in', [values])` | `field in [values]` |
| `('field', 'not in', [values])` | `field not in [values]` |
| `'|'` (OR operator) | `or` |
| `'&'` (AND operator) | `and` (or implicit) |
| `'!'` (NOT operator) | `not` |

**Complex Examples:**

```xml
<!-- OLD: OR condition -->
<field name="name" attrs="{'invisible': ['|', ('state', '=', 'draft'), ('active', '=', False)]}"/>

<!-- NEW: OR condition -->
<field name="name" invisible="state == 'draft' or not active"/>

<!-- OLD: AND condition -->
<field name="name" attrs="{'readonly': [('state', '=', 'done'), ('locked', '=', True)]}"/>

<!-- NEW: AND condition (implicit AND) -->
<field name="name" readonly="state == 'done' and locked"/>

<!-- OLD: NOT IN with OR -->
<h2 attrs="{'invisible': ['|', '|', ('module_a', '=', True), ('module_b', '=', True), ('module_c', '=', True)]}">
    Title
</h2>

<!-- NEW: NOT IN with OR -->
<h2 invisible="module_a or module_b or module_c">
    Title
</h2>
```

### 2. states Attribute Removal

**Old Syntax:**
```xml
<button name="action_confirm" states="draft,sent"/>
```

**New Syntax:**
```xml
<button name="action_confirm" invisible="state not in ['draft', 'sent']"/>
```

### 3. Tree View → List View

**Old Syntax:**
```xml
<tree string="Properties">
    <field name="name"/>
</tree>
```

**New Syntax:**
```xml
<list string="Properties">
    <field name="name"/>
</list>
```

**Batch Conversion (PowerShell):**
```powershell
Get-ChildItem -Path ".\addons" -Filter "*.xml" -Recurse | ForEach-Object {
    (Get-Content $_.FullName -Raw) -replace '<tree>', '<list>' -replace '<tree ', '<list ' -replace '</tree>', '</list>' | 
    Set-Content $_.FullName -NoNewline
}
```

### 4. Search View Group Syntax

**Old Syntax:**
```xml
<search>
    <group expand="0" string="Group By">
        <filter name="group_by_status" string="Status" context="{'group_by': 'status'}"/>
    </group>
</search>
```

**New Syntax:**
```xml
<search>
    <filter name="group_by_status" string="Status" context="{'group_by': 'status'}"/>
</search>
```

**Batch Conversion (PowerShell):**
```powershell
Get-ChildItem -Path ".\addons\*\views" -Filter "*.xml" -Recurse | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content -replace '<group string="Group By">\s*', ''
    $content = $content -replace '\s*</group>\s*</search>', '</search>'
    Set-Content $_.FullName -Value $content -NoNewline
}
```

### 5. Model `create()` Method Signature Change (CRITICAL)

**Old Syntax (Odoo ≤18):**
```python
@api.model
def create(self, vals):
    if vals.get('property_number', _('New')) == _('New'):
        vals['property_number'] = self.env['ir.sequence'].next_by_code('property_fielder.property') or _('New')
    return super(Property, self).create(vals)
```

**New Syntax (Odoo 19):**
```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        if vals.get('property_number', _('New')) == _('New'):
            vals['property_number'] = self.env['ir.sequence'].next_by_code('property_fielder.property') or _('New')
    return super(Property, self).create(vals_list)
```

**Key Changes:**
- Decorator changed from `@api.model` to `@api.model_create_multi`
- Parameter changed from `vals` (single dict) to `vals_list` (list of dicts)
- Must iterate over `vals_list` to process each record
- Return value is now a recordset (can contain multiple records)

**Why This Matters:**
- Odoo 19 optimizes batch record creation
- XML-RPC API calls `create([{...}])` with a list
- Old signature causes `AttributeError: 'list' object has no attribute 'get'`

---

## Security Groups Changes

### Old Structure (Odoo ≤18)

```xml
<record id="module_category_field_service" model="ir.module.category">
    <field name="name">Field Service</field>
    <field name="sequence">10</field>
</record>

<record id="group_field_service_user" model="res.groups">
    <field name="name">User</field>
    <field name="category_id" ref="module_category_field_service"/>
</record>
```

### New Structure (Odoo 19)

```xml
<record id="res_groups_privilege_field_service" model="res.groups.privilege">
    <field name="name">Field Service</field>
    <field name="sequence">10</field>
    <field name="category_id" ref="base.module_category_services"/>
</record>

<record id="group_field_service_user" model="res.groups">
    <field name="name">User</field>
    <field name="privilege_id" ref="res_groups_privilege_field_service"/>
</record>
```

**Key Changes:**
- `ir.module.category` → `res.groups.privilege`
- `category_id` (in res.groups) → `privilege_id`
- Must reference existing `base.module_category_*` for the privilege's `category_id`

---

## Controller Changes

### Route Type Deprecation

**Old Syntax:**
```python
@http.route('/api/jobs', type='json', auth='user', methods=['GET'])
def get_jobs(self):
    pass
```

**New Syntax:**
```python
@http.route('/api/jobs', type='jsonrpc', auth='user', methods=['GET'])
def get_jobs(self):
    pass
```

---

## Conversion Patterns

### Pattern 1: Simple Invisible Condition

```xml
<!-- OLD -->
attrs="{'invisible': [('field', '=', 'value')]}"

<!-- NEW -->
invisible="field == 'value'"
```

### Pattern 2: Multiple Conditions (AND)

```xml
<!-- OLD -->
attrs="{'invisible': [('field1', '=', 'value1'), ('field2', '=', 'value2')]}"

<!-- NEW -->
invisible="field1 == 'value1' and field2 == 'value2'"
```

### Pattern 3: Multiple Conditions (OR)

```xml
<!-- OLD -->
attrs="{'invisible': ['|', ('field1', '=', 'value1'), ('field2', '=', 'value2')]}"

<!-- NEW -->
invisible="field1 == 'value1' or field2 == 'value2'"
```

### Pattern 4: Multiple Attributes

```xml
<!-- OLD -->
attrs="{'invisible': [('state', '=', 'done')], 'readonly': [('locked', '=', True)]}"

<!-- NEW -->
invisible="state == 'done'" readonly="locked"
```

### Pattern 5: Boolean Fields

```xml
<!-- OLD -->
attrs="{'invisible': [('active', '=', False)]}"

<!-- NEW -->
invisible="not active"
```

---

## Best Practices

### 1. View Development

✅ **DO:**
- Use `<list>` instead of `<tree>` for all new views
- Use direct attributes (`invisible`, `readonly`, `required`) instead of `attrs`
- Test views in Odoo 19 before deploying
- Use `column_invisible` for hiding entire columns in list views
- Keep view files under 500 lines (split into multiple files if needed)

❌ **DON'T:**
- Use `attrs` or `states` attributes (removed in v19)
- Use `<tree>` tag (renamed to `<list>`)
- Use `expand` or `string` attributes in search view `<group>` elements
- Mix old and new syntax in the same addon

### 2. Security Configuration

✅ **DO:**
- Use `res.groups.privilege` for new privilege definitions
- Reference existing `base.module_category_*` categories
- Use `privilege_id` instead of `category_id` in res.groups
- Test security rules after migration

❌ **DON'T:**
- Create new `ir.module.category` records (deprecated)
- Use `category_id` in res.groups (use `privilege_id`)

### 3. Controller Development

✅ **DO:**
- Use `type='jsonrpc'` for JSON-RPC endpoints
- Use `type='http'` for regular HTTP endpoints
- Test all API endpoints after migration

❌ **DON'T:**
- Use `type='json'` (deprecated in v17)

### 4. Migration Strategy

✅ **DO:**
1. Create a backup before migration
2. Test in development environment first
3. Fix breaking changes in order of severity (HIGH → MEDIUM → LOW)
4. Run installation with `--log-level=info` to catch all errors
5. Document all changes made

❌ **DON'T:**
- Migrate directly to production
- Skip testing after each fix
- Ignore deprecation warnings

---

## Common Pitfalls

### Pitfall 1: Column vs Cell Invisibility

**Problem:** In Odoo 17+, `invisible` on list view fields hides the cell, not the column.

**Solution:** Use `column_invisible` to hide entire columns:

```xml
<!-- Hide entire column -->
<field name="internal_notes" column_invisible="1"/>

<!-- Hide cell conditionally -->
<field name="status" invisible="state == 'draft'"/>
```

### Pitfall 2: Context Variable Changes

**Problem:** `active_id` no longer works in some contexts.

**Solution:** Use `id` instead:

```xml
<!-- OLD -->
<field name="property_id" context="{'default_property_id': active_id}"/>

<!-- NEW -->
<field name="property_id" context="{'default_property_id': id}"/>
```

### Pitfall 3: View Loading Order

**Problem:** Views reference actions that haven't been loaded yet.

**Solution:** Load actions before views that reference them:

```python
'data': [
    'views/certification_views.xml',  # Contains action definitions
    'views/property_views.xml',       # References certification actions
]
```

Or move action definitions to the beginning of the view file.

---

## Resources

### Official Documentation

- [Odoo 19 View Architectures](https://www.odoo.com/documentation/19.0/developer/reference/user_interface/view_architectures.html)
- [Odoo 19 ORM API](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Odoo 19 Coding Guidelines](https://www.odoo.com/documentation/19.0/contributing/development/coding_guidelines.html)

### Community Resources

- [Odoo Forum: attrs Deprecation](https://www.odoo.com/forum/help-1/since-170-the-attrs-and-states-attributes-are-no-longer-used-246061)
- [GitHub: odoo-attrs-replace Tool](https://github.com/pierrelocus/odoo-attrs-replace) - Automated conversion script

### Conversion Tools

**Python Script for Automated Conversion:**
```bash
# Clone the conversion tool
git clone https://github.com/pierrelocus/odoo-attrs-replace.git
cd odoo-attrs-replace

# Install dependencies
pip install -r requirements.txt

# Run conversion
python3 replace_attrs.py /path/to/your/addon
```

**Note:** Always review automated conversions manually before committing.

---

## Migration Checklist

- [ ] Backup all code and database
- [ ] Update all `<tree>` tags to `<list>`
- [ ] Remove `expand` and `string` from search view `<group>` elements
- [ ] Convert all `attrs` attributes to direct attributes
- [ ] Convert all `states` attributes to `invisible`
- [ ] Update security groups structure
- [ ] Update controller route types
- [ ] Replace `active_id` with `id` in contexts
- [ ] Test installation in development environment
- [ ] Run all unit tests
- [ ] Test all views and workflows manually
- [ ] Document all changes made
- [ ] Deploy to staging environment
- [ ] Final testing before production

---

**End of Document**

