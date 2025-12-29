# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import requests

_logger = logging.getLogger(__name__)

# Module-level cache for geocoding (persists during Odoo process lifetime)
_geocoding_cache = {}


class Property(models.Model):
    _name = 'property_fielder.property'
    _description = 'Property'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Basic Information
    name = fields.Char(string='Property Name', required=True, tracking=True)
    property_number = fields.Char(
        string='Property Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True
    )

    # Property Images
    image = fields.Image(string='Main Image', max_width=1920, max_height=1920)
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
    
    # Address
    street = fields.Char(string='Street', tracking=True)
    street2 = fields.Char(string='Street 2')
    city = fields.Char(string='City', tracking=True)
    state = fields.Char(string='County')
    zip = fields.Char(string='Postcode', tracking=True)
    country_id = fields.Many2one('res.country', string='Country', default=lambda self: self.env.ref('base.uk'))
    
    # GPS Coordinates
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))
    
    # Property Details
    property_type = fields.Selection([
        ('house', 'House'),
        ('flat', 'Flat/Apartment'),
        ('bungalow', 'Bungalow'),
        ('maisonette', 'Maisonette'),
        ('commercial', 'Commercial'),
        ('other', 'Other')
    ], string='Property Type', required=True, default='flat', tracking=True)
    
    bedrooms = fields.Integer(string='Bedrooms', default=1)
    bathrooms = fields.Integer(string='Bathrooms', default=1)
    floor_area = fields.Float(string='Floor Area (sqm)')
    year_built = fields.Integer(string='Year Built')
    
    # Ownership
    partner_id = fields.Many2one('res.partner', string='Owner/Landlord', tracking=True)
    tenant_id = fields.Many2one('res.partner', string='Current Tenant', tracking=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('vacant', 'Vacant'),
        ('maintenance', 'Under Maintenance'),
        ('inactive', 'Inactive')
    ], string='Status', default='draft', required=True, tracking=True)
    
    # Certifications
    certification_ids = fields.One2many(
        'property_fielder.property.certification',
        'property_id',
        string='Certifications'
    )
    
    # Inspections
    inspection_ids = fields.One2many(
        'property_fielder.property.inspection',
        'property_id',
        string='Inspections'
    )

    # Photo Gallery
    image_ids = fields.One2many(
        'property_fielder.property.image',
        'property_id',
        string='Photo Gallery'
    )
    image_count = fields.Integer(compute='_compute_image_count', string='Photos')
    
    # Compliance Status
    compliance_status = fields.Selection([
        ('compliant', 'Fully Compliant'),
        ('expiring_soon', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('non_compliant', 'Non-Compliant')
    ], string='Compliance Status', compute='_compute_compliance_status', store=True)
    
    flage_fire_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Fire Safety', compute='_compute_flage_status', store=True)
    
    flage_legionella_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Legionella', compute='_compute_flage_status', store=True)
    
    flage_asbestos_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Asbestos', compute='_compute_flage_status', store=True)
    
    flage_gas_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Gas Safety', compute='_compute_flage_status', store=True)
    
    flage_electrical_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Electrical Safety', compute='_compute_flage_status', store=True)
    
    # Counts
    certification_count = fields.Integer(compute='_compute_counts')
    inspection_count = fields.Integer(compute='_compute_counts')
    expired_certification_count = fields.Integer(compute='_compute_counts')
    
    # Notes
    notes = fields.Text(string='Notes')
    
    _sql_constraints = [
        ('property_number_unique', 'UNIQUE(property_number)', 'Property number must be unique!'),
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('property_number', _('New')) == _('New'):
                vals['property_number'] = self.env['ir.sequence'].next_by_code('property_fielder.property') or _('New')
        return super(Property, self).create(vals_list)

    @api.depends('certification_ids', 'certification_ids.status')
    def _compute_compliance_status(self):
        for property in self:
            certifications = property.certification_ids
            if not certifications:
                property.compliance_status = 'non_compliant'
            elif any(cert.status == 'expired' for cert in certifications):
                property.compliance_status = 'expired'
            elif any(cert.status == 'expiring_soon' for cert in certifications):
                property.compliance_status = 'expiring_soon'
            else:
                property.compliance_status = 'compliant'

    @api.depends('certification_ids', 'certification_ids.certification_type_id', 'certification_ids.status')
    def _compute_flage_status(self):
        for property in self:
            # Get certifications by type
            fire_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'FIRE')
            legionella_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'LEGIONELLA')
            asbestos_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'ASBESTOS')
            gas_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'GAS')
            electrical_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'ELECTRICAL')
            
            property.flage_fire_status = self._get_cert_status(fire_cert)
            property.flage_legionella_status = self._get_cert_status(legionella_cert)
            property.flage_asbestos_status = self._get_cert_status(asbestos_cert)
            property.flage_gas_status = self._get_cert_status(gas_cert)
            property.flage_electrical_status = self._get_cert_status(electrical_cert)
    
    def _get_cert_status(self, certification):
        if not certification:
            return 'missing'
        latest = certification.sorted(key=lambda c: c.issue_date, reverse=True)[0]
        return latest.status

    @api.depends('certification_ids', 'inspection_ids')
    def _compute_counts(self):
        for property in self:
            property.certification_count = len(property.certification_ids)
            property.inspection_count = len(property.inspection_ids)
            property.expired_certification_count = len(
                property.certification_ids.filtered(lambda c: c.status == 'expired')
            )

    @api.depends('image_ids')
    def _compute_image_count(self):
        for property in self:
            property.image_count = len(property.image_ids)

    @api.model
    def reverse_geocode(self, lat, lng, use_cache=True):
        """Reverse geocode coordinates to get address.

        Uses in-memory cache to avoid repeated API calls for same coordinates.
        Coordinates are rounded to 3 decimal places (~100m precision) for caching.

        Args:
            lat: Latitude coordinate
            lng: Longitude coordinate
            use_cache: Whether to use/update the cache (default True)

        Returns:
            dict with street, city, zip, full_address keys
        """
        global _geocoding_cache

        # Round to 3 decimal places for cache key (~100m precision)
        cache_key = (round(lat, 3), round(lng, 3))

        # Check cache first
        if use_cache and cache_key in _geocoding_cache:
            _logger.debug(f"Geocoding cache HIT for {cache_key}")
            return _geocoding_cache[cache_key]

        _logger.debug(f"Geocoding cache MISS for {cache_key} - calling Mapbox API")

        # Fetch from Mapbox API
        address = self._fetch_address_from_mapbox(lat, lng)

        # Store in cache
        if use_cache:
            _geocoding_cache[cache_key] = address

        return address

    def _fetch_address_from_mapbox(self, lat, lng):
        """Fetch address from Mapbox reverse geocoding API"""
        try:
            mapbox_token = self.env['ir.config_parameter'].sudo().get_param(
                'property_fielder.mapbox.token',
                'pk.eyJ1IjoibXVhemFtc2FyZmFyYXoiLCJhIjoiY205b2dzdnVlMTVuZDJqczcwbnBseW1tYiJ9.-MvfX63GtzUQceap1g6iJQ'
            )

            url = f"https://api.mapbox.com/search/geocode/v6/reverse?longitude={lng}&latitude={lat}&access_token={mapbox_token}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get('features') and len(data['features']) > 0:
                    props = data['features'][0].get('properties', {})
                    context = props.get('context', {})

                    street = props.get('name', props.get('full_address', '').split(',')[0])
                    postcode = context.get('postcode', {}).get('name', '')
                    locality = context.get('locality', {}).get('name', '')
                    place = context.get('place', {}).get('name', 'London')

                    return {
                        'street': street,
                        'city': locality or place or 'London',
                        'zip': postcode,
                        'full_address': props.get('full_address', street)
                    }
        except Exception as e:
            _logger.warning(f"Mapbox reverse geocoding failed for ({lat}, {lng}): {e}")

        # Fallback to coordinate-based address
        return {
            'street': f'Location {lat:.4f}, {lng:.4f}',
            'city': 'London',
            'zip': '',
            'full_address': f'{lat:.4f}, {lng:.4f}'
        }

    def action_geocode_address(self):
        """Action to geocode address from coordinates"""
        self.ensure_one()
        if self.latitude and self.longitude:
            address = self.reverse_geocode(self.latitude, self.longitude)
            self.write({
                'street': address['street'],
                'city': address['city'],
                'zip': address['zip'],
            })
            return {'type': 'ir.actions.client', 'tag': 'reload'}
        return False

    def action_view_images(self):
        """Action to view property images in a separate view"""
        self.ensure_one()
        return {
            'name': _('Property Photos'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.property.image',
            'view_mode': 'kanban,list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }
