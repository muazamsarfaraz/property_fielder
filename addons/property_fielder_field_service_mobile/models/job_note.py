# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class JobNote(models.Model):
    """Notes and observations during job execution"""
    
    _name = 'property_fielder.job.note'
    _description = 'Job Note'
    _order = 'create_date desc'
    
    # Job Reference
    job_id = fields.Many2one(
        'property_fielder.job',
        string='Job',
        required=True,
        ondelete='cascade',
        help='Job this note belongs to'
    )
    
    inspector_id = fields.Many2one(
        'property_fielder.inspector',
        string='Inspector',
        required=True,
        help='Inspector who created the note'
    )
    
    # Note Content
    title = fields.Char(
        string='Title',
        required=True,
        help='Note title/subject'
    )
    
    content = fields.Text(
        string='Content',
        required=True,
        help='Note content'
    )
    
    # Category
    category = fields.Selection([
        ('observation', 'Observation'),
        ('issue', 'Issue'),
        ('recommendation', 'Recommendation'),
        ('safety', 'Safety Concern'),
        ('customer_request', 'Customer Request'),
        ('follow_up', 'Follow-Up Required'),
        ('general', 'General')
    ], string='Category', default='general', required=True)
    
    # Priority
    priority = fields.Selection([
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], string='Priority', default='normal', required=True)
    
    # Location
    latitude = fields.Float(
        string='Latitude',
        digits=(10, 7),
        help='GPS latitude where note was created'
    )
    
    longitude = fields.Float(
        string='Longitude',
        digits=(10, 7),
        help='GPS longitude where note was created'
    )
    
    # Attachments
    attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Attachments',
        help='Files attached to this note'
    )
    
    # Voice Note
    voice_note = fields.Binary(
        string='Voice Note',
        attachment=True,
        help='Audio recording'
    )
    
    voice_note_duration = fields.Integer(
        string='Voice Note Duration (seconds)',
        help='Duration of voice recording'
    )
    
    # Tags
    tag_ids = fields.Many2many(
        'property_fielder.note.tag',
        string='Tags',
        help='Tags for categorizing notes'
    )
    
    # Follow-up
    requires_follow_up = fields.Boolean(
        string='Requires Follow-Up',
        default=False,
        help='Mark if this note requires follow-up action'
    )
    
    follow_up_date = fields.Date(
        string='Follow-Up Date',
        help='When to follow up on this note'
    )
    
    # Status
    is_resolved = fields.Boolean(
        string='Resolved',
        default=False,
        help='Mark as resolved'
    )
    
    resolved_date = fields.Datetime(
        string='Resolved Date',
        readonly=True,
        help='When this note was resolved'
    )
    
    resolved_by = fields.Many2one(
        'res.users',
        string='Resolved By',
        readonly=True,
        help='User who resolved this note'
    )
    
    def action_mark_resolved(self):
        """Mark note as resolved"""
        self.ensure_one()
        self.write({
            'is_resolved': True,
            'resolved_date': fields.Datetime.now(),
            'resolved_by': self.env.user.id
        })


class NoteTag(models.Model):
    """Tags for categorizing notes"""
    
    _name = 'property_fielder.note.tag'
    _description = 'Note Tag'
    
    name = fields.Char(
        string='Tag Name',
        required=True,
        help='Tag name'
    )
    
    color = fields.Integer(
        string='Color',
        help='Color for UI display'
    )

    # Constraints (Odoo 19 style)
    _check_name_unique = models.Constraint(
        'UNIQUE(name)',
        'Tag name must be unique!',
    )

