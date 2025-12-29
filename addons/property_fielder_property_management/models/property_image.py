# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PropertyImage(models.Model):
    _name = 'property_fielder.property.image'
    _description = 'Property Photo'
    _order = 'sequence, id'

    name = fields.Char(string='Description')
    property_id = fields.Many2one(
        'property_fielder.property',
        string='Property',
        required=True,
        ondelete='cascade'
    )
    image = fields.Image(
        string='Image',
        required=True,
        max_width=1920,
        max_height=1920
    )
    image_medium = fields.Image(
        string='Medium Image',
        max_width=512,
        max_height=512,
        related='image',
        store=True
    )
    image_small = fields.Image(
        string='Thumbnail',
        max_width=128,
        max_height=128,
        related='image',
        store=True
    )
    sequence = fields.Integer(string='Sequence', default=10)
    category = fields.Selection([
        ('exterior', 'Exterior'),
        ('interior', 'Interior'),
        ('floor_plan', 'Floor Plan'),
        ('document', 'Document'),
        ('other', 'Other')
    ], string='Category', default='exterior')
    is_main = fields.Boolean(
        string='Main Image',
        default=False,
        help='Set as the main property image'
    )
    taken_date = fields.Date(string='Date Taken')
    notes = fields.Text(string='Notes')

    @api.model_create_multi
    def create(self, vals_list):
        """When creating a main image, update the property's main image field."""
        records = super().create(vals_list)
        for record in records:
            if record.is_main and record.property_id:
                record.property_id.write({'image': record.image})
                # Unset other main images for this property
                record.property_id.image_ids.filtered(
                    lambda r: r.is_main and r.id != record.id
                ).write({'is_main': False})
        return records

    def write(self, vals):
        """When setting as main, update property and unset other main images."""
        res = super().write(vals)
        if vals.get('is_main'):
            for record in self:
                if record.property_id:
                    record.property_id.write({'image': record.image})
                    # Unset other main images
                    record.property_id.image_ids.filtered(
                        lambda r: r.is_main and r.id != record.id
                    ).write({'is_main': False})
        return res

