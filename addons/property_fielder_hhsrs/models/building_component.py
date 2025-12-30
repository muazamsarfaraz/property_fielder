# -*- coding: utf-8 -*-
from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class BuildingComponent(models.Model):
    """Building component condition tracking for DHS Criterion B."""
    _name = 'property_fielder.building.component'
    _description = 'Building Component'
    _order = 'property_id, component_type'

    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade'
    )
    
    component_type = fields.Selection([
        ('roof', 'Roof'),
        ('external_walls', 'External Walls'),
        ('windows', 'Windows'),
        ('external_doors', 'External Doors'),
        ('chimneys', 'Chimneys'),
        ('central_heating', 'Central Heating'),
        ('gas_fires', 'Gas Fires'),
        ('storage_heaters', 'Storage Heaters'),
        ('plumbing', 'Plumbing'),
        ('electrics', 'Electrical Installation'),
        ('kitchen', 'Kitchen'),
        ('bathroom', 'Bathroom'),
        ('internal_doors', 'Internal Doors'),
        ('floors', 'Floors'),
        ('ceilings', 'Ceilings'),
        ('internal_walls', 'Internal Walls'),
        ('drainage', 'Drainage'),
        ('other', 'Other'),
    ], string='Component Type', required=True)
    
    name = fields.Char(
        string='Component Name',
        compute='_compute_name',
        store=True
    )
    
    # Age & Lifespan
    installation_date = fields.Date(string='Installation Date')
    age_years = fields.Integer(
        string='Age (Years)',
        compute='_compute_age',
        store=True
    )
    expected_life = fields.Integer(
        string='Expected Lifespan (Years)',
        help='Expected lifespan of this component type'
    )
    is_beyond_life = fields.Boolean(
        string='Beyond Expected Life',
        compute='_compute_is_beyond_life',
        store=True
    )
    
    # Condition
    condition = fields.Selection([
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('critical', 'Critical'),
    ], string='Condition', default='good', required=True)
    
    # Renewal
    last_renewed = fields.Date(string='Last Renewal/Repair')
    next_renewal = fields.Date(string='Next Planned Renewal')
    
    # Cost
    replacement_cost = fields.Monetary(
        string='Estimated Replacement Cost',
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )
    
    notes = fields.Text(string='Condition Notes')
    
    # Photos
    photo_ids = fields.Many2many(
        'ir.attachment',
        string='Photos'
    )

    @api.depends('component_type', 'property_id')
    def _compute_name(self):
        for rec in self:
            comp_name = dict(self._fields['component_type'].selection).get(rec.component_type, '')
            prop_name = rec.property_id.name or ''
            rec.name = f"{prop_name} - {comp_name}"

    @api.depends('installation_date')
    def _compute_age(self):
        today = fields.Date.today()
        for rec in self:
            if rec.installation_date:
                delta = relativedelta(today, rec.installation_date)
                rec.age_years = delta.years
            else:
                rec.age_years = 0

    @api.depends('age_years', 'expected_life')
    def _compute_is_beyond_life(self):
        for rec in self:
            if rec.expected_life and rec.age_years:
                rec.is_beyond_life = rec.age_years > rec.expected_life
            else:
                rec.is_beyond_life = False

    @api.onchange('component_type')
    def _onchange_component_type(self):
        """Set default expected lifespan based on component type."""
        lifespans = {
            'roof': 50,
            'external_walls': 60,
            'windows': 30,
            'external_doors': 30,
            'chimneys': 50,
            'central_heating': 15,
            'gas_fires': 15,
            'storage_heaters': 20,
            'plumbing': 40,
            'electrics': 30,
            'kitchen': 20,
            'bathroom': 30,
            'internal_doors': 40,
            'floors': 50,
            'ceilings': 50,
            'internal_walls': 60,
            'drainage': 40,
        }
        self.expected_life = lifespans.get(self.component_type, 25)
