# -*- coding: utf-8 -*-

from odoo import models, fields, api


class FieldServiceSkill(models.Model):
    """Skills required for jobs and possessed by inspectors/technicians"""
    
    _name = 'property_fielder.skill'
    _description = 'Field Service Skill'
    _order = 'name'
    
    name = fields.Char(
        string='Skill Name',
        required=True,
        translate=True,
        help='Name of the skill (e.g., "Electrical", "Plumbing", "HVAC")'
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Short code for the skill (e.g., "ELEC", "PLUMB")'
    )
    
    description = fields.Text(
        string='Description',
        translate=True,
        help='Detailed description of the skill'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive the skill'
    )
    
    color = fields.Integer(
        string='Color',
        help='Color for UI display'
    )
    
    # Statistics
    job_count = fields.Integer(
        string='Jobs Requiring This Skill',
        compute='_compute_job_count',
        store=False
    )
    
    inspector_count = fields.Integer(
        string='Inspectors With This Skill',
        compute='_compute_inspector_count',
        store=False
    )

    # Constraints (Odoo 19 style)
    _check_code_unique = models.Constraint(
        'UNIQUE(code)',
        'Skill code must be unique!',
    )
    
    @api.depends('name')
    def _compute_job_count(self):
        """Count jobs requiring this skill"""
        for skill in self:
            skill.job_count = self.env['property_fielder.job'].search_count([
                ('skill_ids', 'in', skill.id)
            ])
    
    @api.depends('name')
    def _compute_inspector_count(self):
        """Count inspectors with this skill"""
        for skill in self:
            skill.inspector_count = self.env['property_fielder.inspector'].search_count([
                ('skill_ids', 'in', skill.id)
            ])
    
    def name_get(self):
        """Display name with code"""
        result = []
        for skill in self:
            name = f"[{skill.code}] {skill.name}"
            result.append((skill.id, name))
        return result

