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
    full_address = fields.Char(
        string='Full Address',
        compute='_compute_full_address',
        store=True,
        help='Complete formatted address'
    )
    
    # GPS Coordinates
    latitude = fields.Float(string='Latitude', digits=(10, 7))
    longitude = fields.Float(string='Longitude', digits=(10, 7))

    # Block/Unit Hierarchy
    parent_id = fields.Many2one(
        'property_fielder.property',
        string='Parent Property/Block',
        ondelete='restrict',
        help='Parent building or block that this unit belongs to',
        index=True
    )
    child_ids = fields.One2many(
        'property_fielder.property',
        'parent_id',
        string='Units/Flats'
    )
    is_block = fields.Boolean(
        string='Is Block/Building',
        compute='_compute_hierarchy_info',
        store=True,
        help='True if this property has child units'
    )
    unit_count = fields.Integer(
        string='Number of Units',
        compute='_compute_hierarchy_info',
        store=True
    )
    unit_number = fields.Char(
        string='Unit/Flat Number',
        help='Unit or flat number within the parent block (e.g., "Flat 2A", "Unit 101")'
    )
    floor_level = fields.Integer(
        string='Floor Level',
        help='Floor number (0 = Ground, -1 = Basement, 1 = First floor, etc.)'
    )

    # UK Property Identification
    uprn = fields.Char(
        string='UPRN',
        help='Unique Property Reference Number - 12 digit UK property identifier',
        tracking=True,
        copy=False
    )

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
    reception_rooms = fields.Integer(string='Reception Rooms', default=1)
    floor_area = fields.Float(string='Floor Area (sqm)')
    year_built = fields.Integer(string='Year Built')
    number_of_floors = fields.Integer(
        string='Number of Floors',
        default=1,
        help='Total number of floors in the property/building'
    )

    # Construction & Building Details
    construction_type = fields.Selection([
        ('brick', 'Brick/Masonry'),
        ('timber_frame', 'Timber Frame'),
        ('concrete', 'Concrete'),
        ('steel_frame', 'Steel Frame'),
        ('stone', 'Stone'),
        ('prefab', 'Prefabricated'),
        ('mixed', 'Mixed Construction'),
        ('other', 'Other')
    ], string='Construction Type',
       help='Primary construction material/method of the building')

    # Heating System
    heating_type = fields.Selection([
        ('gas_central', 'Gas Central Heating'),
        ('electric', 'Electric Heating'),
        ('oil', 'Oil Central Heating'),
        ('lpg', 'LPG Central Heating'),
        ('storage_heaters', 'Storage Heaters'),
        ('heat_pump', 'Heat Pump'),
        ('underfloor', 'Underfloor Heating'),
        ('communal', 'Communal/District Heating'),
        ('solid_fuel', 'Solid Fuel (Coal/Wood)'),
        ('none', 'No Central Heating'),
        ('other', 'Other')
    ], string='Heating Type',
       help='Primary heating system in the property')

    # Exterior Features
    has_garden = fields.Boolean(
        string='Has Garden',
        default=False,
        help='Property has a private garden or outdoor space'
    )
    garden_type = fields.Selection([
        ('private', 'Private Garden'),
        ('shared', 'Shared Garden'),
        ('communal', 'Communal Gardens'),
        ('balcony', 'Balcony Only'),
        ('terrace', 'Roof Terrace'),
        ('patio', 'Patio/Courtyard')
    ], string='Garden Type')

    has_parking = fields.Boolean(
        string='Has Parking',
        default=False,
        help='Property has dedicated parking'
    )
    parking_type = fields.Selection([
        ('garage', 'Garage'),
        ('driveway', 'Driveway'),
        ('allocated', 'Allocated Space'),
        ('street', 'Street Permit'),
        ('underground', 'Underground Parking'),
        ('car_port', 'Car Port')
    ], string='Parking Type')
    parking_spaces = fields.Integer(
        string='Parking Spaces',
        default=0,
        help='Number of parking spaces available'
    )

    # Tenure & Ownership Details
    tenure = fields.Selection([
        ('freehold', 'Freehold'),
        ('leasehold', 'Leasehold'),
        ('share_of_freehold', 'Share of Freehold'),
        ('commonhold', 'Commonhold'),
        ('rental', 'Rental Only')
    ], string='Tenure', tracking=True)

    council_tax_band = fields.Selection([
        ('a', 'Band A'),
        ('b', 'Band B'),
        ('c', 'Band C'),
        ('d', 'Band D'),
        ('e', 'Band E'),
        ('f', 'Band F'),
        ('g', 'Band G'),
        ('h', 'Band H')
    ], string='Council Tax Band')
    council_tax_account = fields.Char(string='Council Tax Account')

    furnishing_state = fields.Selection([
        ('unfurnished', 'Unfurnished'),
        ('part_furnished', 'Part Furnished'),
        ('furnished', 'Furnished')
    ], string='Furnishing State', default='unfurnished')

    # EPC (Energy Performance Certificate)
    epc_rating = fields.Selection([
        ('a', 'A (92-100)'),
        ('b', 'B (81-91)'),
        ('c', 'C (69-80)'),
        ('d', 'D (55-68)'),
        ('e', 'E (39-54)'),
        ('f', 'F (21-38)'),
        ('g', 'G (1-20)')
    ], string='EPC Rating', tracking=True)
    epc_score = fields.Integer(
        string='EPC Score',
        help='Energy efficiency score from 1 to 100'
    )
    epc_certificate_number = fields.Char(string='EPC Certificate Number')
    epc_valid_until = fields.Date(string='EPC Valid Until', tracking=True)
    epc_exempt = fields.Boolean(string='EPC Exempt', default=False)
    epc_exempt_reason = fields.Text(string='EPC Exemption Reason')
    mees_compliant = fields.Boolean(
        string='MEES Compliant',
        compute='_compute_mees_compliant',
        store=True,
        help='Minimum Energy Efficiency Standards - requires EPC rating E or above for rentals'
    )

    # HMO (House in Multiple Occupation)
    hmo_status = fields.Selection([
        ('not_hmo', 'Not an HMO'),
        ('small_hmo', 'Small HMO (3-4 tenants)'),
        ('licensable_hmo', 'Licensable HMO (5+ tenants)'),
        ('mandatory_hmo', 'Mandatory HMO'),
        ('additional_hmo', 'Additional Licensing HMO')
    ], string='HMO Status', default='not_hmo', tracking=True)
    hmo_license_number = fields.Char(string='HMO License Number')
    hmo_license_expiry = fields.Date(string='HMO License Expiry', tracking=True)
    hmo_max_occupancy = fields.Integer(
        string='HMO Max Occupancy',
        help='Maximum number of permitted occupants under HMO license'
    )
    hmo_license_holder_id = fields.Many2one(
        'res.partner',
        string='HMO License Holder',
        help='Person or company named on the HMO license'
    )

    # Selective Licensing
    selective_license_required = fields.Boolean(
        string='Selective License Required',
        help='Property is in a selective licensing area'
    )
    selective_license_number = fields.Char(string='Selective License Number')
    selective_license_expiry = fields.Date(string='Selective License Expiry')

    # Section 21 Status
    section_21_banned = fields.Boolean(
        string='Section 21 Banned',
        compute='_compute_section_21_banned',
        store=True,
        help='Section 21 notices cannot be served if property lacks valid EPC, Gas Safety, or required licenses'
    )
    
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

    # Documents
    document_ids = fields.One2many(
        'property_fielder.property.document',
        'property_id',
        string='Documents'
    )
    document_count = fields.Integer(compute='_compute_document_count', string='Documents')

    # Key Sets
    key_set_ids = fields.One2many(
        'property_fielder.key.set',
        'property_id',
        string='Key Sets'
    )
    key_set_count = fields.Integer(compute='_compute_key_set_count', string='Key Sets')

    # Utility Meters
    utility_meter_ids = fields.One2many(
        'property_fielder.utility.meter',
        'property_id',
        string='Utility Meters'
    )
    utility_meter_count = fields.Integer(compute='_compute_utility_meter_count', string='Meters')

    # Insurance
    insurance_ids = fields.One2many(
        'property_fielder.building.insurance',
        'property_id',
        string='Insurance Policies'
    )
    insurance_count = fields.Integer(compute='_compute_insurance_count', string='Insurance')

    # EWS1 Assessments (for high-rise buildings)
    ews1_ids = fields.One2many(
        'property_fielder.ews1.assessment',
        'property_id',
        string='EWS1 Assessments'
    )

    # Property Assets
    asset_ids = fields.One2many(
        'property_fielder.property.asset',
        'property_id',
        string='Assets/Appliances'
    )
    asset_count = fields.Integer(compute='_compute_asset_count', string='Assets')

    # HMO Rooms
    hmo_room_ids = fields.One2many(
        'property_fielder.hmo.room',
        'property_id',
        string='HMO Rooms'
    )
    hmo_room_count = fields.Integer(compute='_compute_hmo_room_count', string='Rooms')

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
    ], string='Fire Safety', compute='_compute_flage_status', store=True,
       help='Fire Safety Certificate status. Required for HMOs and buildings with common areas. '
            'Covers fire risk assessment, fire alarms, extinguishers, and escape routes.')

    flage_legionella_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Legionella', compute='_compute_flage_status', store=True,
       help='Legionella Risk Assessment status. Required for all rental properties. '
            'Assesses risk of Legionella bacteria in water systems (tanks, pipes, showers).')

    flage_asbestos_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Asbestos', compute='_compute_flage_status', store=True,
       help='Asbestos Survey status. Required for properties built before 2000. '
            'Identifies presence and condition of asbestos-containing materials.')

    flage_gas_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Gas Safety', compute='_compute_flage_status', store=True,
       help='Gas Safety Certificate (CP12) status. Legally required annually for all rental properties with gas. '
            'Must be issued by a Gas Safe registered engineer.')

    flage_electrical_status = fields.Selection([
        ('valid', 'Valid'),
        ('expiring', 'Expiring Soon'),
        ('expired', 'Expired'),
        ('missing', 'Missing')
    ], string='Electrical Safety', compute='_compute_flage_status', store=True,
       help='EICR (Electrical Installation Condition Report) status. Required every 5 years for rental properties. '
            'Must be issued by a qualified electrician (Part P registered).')

    # FLAGE+ Expiry Dates (computed from latest certificate of each type)
    flage_fire_expiry = fields.Date(
        string='Fire Safety Expiry',
        compute='_compute_flage_status',
        store=True
    )
    flage_legionella_expiry = fields.Date(
        string='Legionella Expiry',
        compute='_compute_flage_status',
        store=True
    )
    flage_asbestos_expiry = fields.Date(
        string='Asbestos Expiry',
        compute='_compute_flage_status',
        store=True
    )
    flage_gas_expiry = fields.Date(
        string='Gas Safety Expiry',
        compute='_compute_flage_status',
        store=True
    )
    flage_electrical_expiry = fields.Date(
        string='Electrical Safety Expiry',
        compute='_compute_flage_status',
        store=True
    )

    # Counts
    certification_count = fields.Integer(compute='_compute_counts')
    inspection_count = fields.Integer(compute='_compute_counts')
    expired_certification_count = fields.Integer(compute='_compute_counts')

    # Next Inspection (for kanban cards)
    next_inspection_date = fields.Date(
        string='Next Inspection',
        compute='_compute_next_inspection',
        store=True,
        help='Date of the next scheduled inspection'
    )
    next_inspection_type = fields.Char(
        string='Next Inspection Type',
        compute='_compute_next_inspection',
        store=True,
        help='Type of the next scheduled inspection'
    )

    # Notes
    notes = fields.Text(string='Notes')

    # Access Information (for inspectors)
    key_safe_location = fields.Char(
        string='Key Safe Location',
        help='Location of the key safe (e.g., "Left side of front door", "Behind plant pot")'
    )
    key_safe_code = fields.Char(
        string='Key Safe Code',
        help='Code for the key safe (keep confidential)',
        groups='property_fielder_property_management.group_property_manager'
    )
    entry_instructions = fields.Text(
        string='Entry Instructions',
        help='Special instructions for entering the property'
    )
    parking_instructions = fields.Text(
        string='Parking Instructions',
        help='Where to park when visiting the property'
    )
    access_contact_id = fields.Many2one(
        'res.partner',
        string='Access Contact',
        help='Person to contact for access (e.g., resident, neighbor, concierge)'
    )
    access_contact_phone = fields.Char(
        related='access_contact_id.phone',
        string='Access Contact Phone',
        readonly=True
    )
    access_hours = fields.Char(
        string='Access Hours',
        help='Preferred access times (e.g., "9am-5pm weekdays", "After 6pm")'
    )
    access_notes = fields.Text(
        string='Access Notes',
        help='Additional notes about property access (dogs, alarms, etc.)'
    )

    # Constraints (Odoo 19 style)
    _check_property_number_unique = models.Constraint(
        'UNIQUE(property_number)',
        'Property number must be unique!',
    )
    _check_uprn_unique = models.Constraint(
        'UNIQUE(uprn)',
        'UPRN must be unique - this property reference is already in use!',
    )

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

    @api.depends('certification_ids', 'certification_ids.certification_type_id', 'certification_ids.status', 'certification_ids.expiry_date')
    def _compute_flage_status(self):
        for property in self:
            # Get certifications by type
            fire_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'FIRE')
            legionella_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'LEGIONELLA')
            asbestos_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'ASBESTOS')
            gas_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'GAS')
            electrical_cert = property.certification_ids.filtered(lambda c: c.certification_type_id.code == 'ELECTRICAL')

            # Set status and expiry for each FLAGE+ category
            property.flage_fire_status, property.flage_fire_expiry = self._get_cert_status_and_expiry(fire_cert)
            property.flage_legionella_status, property.flage_legionella_expiry = self._get_cert_status_and_expiry(legionella_cert)
            property.flage_asbestos_status, property.flage_asbestos_expiry = self._get_cert_status_and_expiry(asbestos_cert)
            property.flage_gas_status, property.flage_gas_expiry = self._get_cert_status_and_expiry(gas_cert)
            property.flage_electrical_status, property.flage_electrical_expiry = self._get_cert_status_and_expiry(electrical_cert)

    def _get_cert_status_and_expiry(self, certification):
        """Returns (status, expiry_date) tuple for a certification."""
        if not certification:
            return ('missing', False)
        latest = certification.sorted(key=lambda c: c.issue_date, reverse=True)[0]
        return (latest.status, latest.expiry_date)

    @api.depends('child_ids')
    def _compute_hierarchy_info(self):
        for prop in self:
            prop.unit_count = len(prop.child_ids)
            prop.is_block = prop.unit_count > 0

    @api.depends('street', 'street2', 'city', 'state', 'zip')
    def _compute_full_address(self):
        """Compute full formatted address."""
        for prop in self:
            parts = []
            if prop.street:
                parts.append(prop.street)
            if prop.street2:
                parts.append(prop.street2)
            if prop.city:
                parts.append(prop.city)
            if prop.state:
                parts.append(prop.state)
            if prop.zip:
                parts.append(prop.zip)
            prop.full_address = ', '.join(parts) if parts else prop.name

    @api.depends('certification_ids', 'inspection_ids')
    def _compute_counts(self):
        for property in self:
            property.certification_count = len(property.certification_ids)
            property.inspection_count = len(property.inspection_ids)
            property.expired_certification_count = len(
                property.certification_ids.filtered(lambda c: c.status == 'expired')
            )

    @api.depends('inspection_ids', 'inspection_ids.scheduled_date', 'inspection_ids.state')
    def _compute_next_inspection(self):
        """Compute the next scheduled inspection date and type for kanban display"""
        today = fields.Date.today()
        for prop in self:
            # Get upcoming scheduled/draft inspections
            upcoming = prop.inspection_ids.filtered(
                lambda i: i.state in ('draft', 'scheduled') and i.scheduled_date and i.scheduled_date >= today
            ).sorted(key=lambda i: i.scheduled_date)

            if upcoming:
                prop.next_inspection_date = upcoming[0].scheduled_date
                prop.next_inspection_type = upcoming[0].certification_type_id.name or 'Inspection'
            else:
                prop.next_inspection_date = False
                prop.next_inspection_type = False

    @api.depends('image_ids')
    def _compute_image_count(self):
        for property in self:
            property.image_count = len(property.image_ids)

    @api.depends('document_ids')
    def _compute_document_count(self):
        for property in self:
            property.document_count = len(property.document_ids)

    @api.depends('key_set_ids')
    def _compute_key_set_count(self):
        for property in self:
            property.key_set_count = len(property.key_set_ids)

    @api.depends('utility_meter_ids')
    def _compute_utility_meter_count(self):
        for property in self:
            property.utility_meter_count = len(property.utility_meter_ids)

    @api.depends('insurance_ids')
    def _compute_insurance_count(self):
        for property in self:
            property.insurance_count = len(property.insurance_ids)

    @api.depends('asset_ids')
    def _compute_asset_count(self):
        for property in self:
            property.asset_count = len(property.asset_ids)

    @api.depends('hmo_room_ids')
    def _compute_hmo_room_count(self):
        for property in self:
            property.hmo_room_count = len(property.hmo_room_ids)

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

    def action_view_documents(self):
        """Action to view property documents in a separate view"""
        self.ensure_one()
        return {
            'name': _('Property Documents'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.property.document',
            'view_mode': 'kanban,list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_view_key_sets(self):
        """Action to view property key sets"""
        self.ensure_one()
        return {
            'name': _('Key Sets'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.key.set',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_view_utility_meters(self):
        """Action to view property utility meters"""
        self.ensure_one()
        return {
            'name': _('Utility Meters'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.utility.meter',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_view_insurance(self):
        """Action to view property insurance policies"""
        self.ensure_one()
        return {
            'name': _('Insurance Policies'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.building.insurance',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_view_assets(self):
        """Action to view property assets"""
        self.ensure_one()
        return {
            'name': _('Property Assets'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.property.asset',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    def action_view_hmo_rooms(self):
        """Action to view HMO rooms"""
        self.ensure_one()
        return {
            'name': _('HMO Rooms'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.hmo.room',
            'view_mode': 'list,form',
            'domain': [('property_id', '=', self.id)],
            'context': {'default_property_id': self.id},
        }

    # ==================== UK Compliance Computed Fields ====================

    @api.depends('epc_rating', 'epc_exempt', 'tenure')
    def _compute_mees_compliant(self):
        """Compute MEES compliance status.

        MEES requires EPC rating of E or above for rental properties.
        Properties are compliant if:
        - EPC exempt, or
        - Not a rental property, or
        - EPC rating is A, B, C, D, or E
        """
        for prop in self:
            if prop.epc_exempt:
                prop.mees_compliant = True
            elif prop.tenure != 'rental':
                prop.mees_compliant = True
            elif prop.epc_rating in ('a', 'b', 'c', 'd', 'e'):
                prop.mees_compliant = True
            elif not prop.epc_rating:
                # No rating - assume non-compliant for rentals
                prop.mees_compliant = False
            else:
                # Rating is F or G
                prop.mees_compliant = False

    @api.depends('epc_rating', 'flage_gas_status', 'hmo_status', 'hmo_license_expiry',
                 'selective_license_required', 'selective_license_expiry')
    def _compute_section_21_banned(self):
        """Compute whether Section 21 notices are banned.

        Section 21 cannot be served if:
        - Property lacks valid EPC
        - Property lacks valid Gas Safety Certificate
        - HMO requires license but license is expired/missing
        - Selective license required but expired/missing
        """
        from datetime import date
        today = date.today()

        for prop in self:
            banned = False

            # Check EPC
            if not prop.epc_rating and not prop.epc_exempt:
                banned = True

            # Check Gas Safety
            if prop.flage_gas_status in ('missing', 'expired'):
                banned = True

            # Check HMO License
            if prop.hmo_status in ('licensable_hmo', 'mandatory_hmo', 'additional_hmo'):
                if not prop.hmo_license_number or not prop.hmo_license_expiry:
                    banned = True
                elif prop.hmo_license_expiry < today:
                    banned = True

            # Check Selective License
            if prop.selective_license_required:
                if not prop.selective_license_number or not prop.selective_license_expiry:
                    banned = True
                elif prop.selective_license_expiry < today:
                    banned = True

            prop.section_21_banned = banned

    @api.constrains('uprn')
    def _check_uprn(self):
        """Validate UPRN format (12 digits)"""
        import re
        for prop in self:
            if prop.uprn:
                # Remove any spaces or dashes
                clean_uprn = re.sub(r'[\s\-]', '', prop.uprn)
                if not re.match(r'^\d{1,12}$', clean_uprn):
                    raise ValidationError(
                        _('UPRN must be a numeric value of up to 12 digits. Got: %s') % prop.uprn
                    )

    @api.constrains('epc_score')
    def _check_epc_score(self):
        """Validate EPC score is between 1 and 100"""
        for prop in self:
            if prop.epc_score and (prop.epc_score < 1 or prop.epc_score > 100):
                raise ValidationError(
                    _('EPC Score must be between 1 and 100. Got: %s') % prop.epc_score
                )

    @api.constrains('year_built')
    def _check_year_built(self):
        """Validate Year Built is reasonable (1600 to current year)"""
        import datetime
        current_year = datetime.date.today().year
        for prop in self:
            if prop.year_built:
                if prop.year_built < 1600:
                    raise ValidationError(
                        _('Year Built cannot be before 1600. Got: %s') % prop.year_built
                    )
                if prop.year_built > current_year:
                    raise ValidationError(
                        _('Year Built cannot be in the future. Got: %s') % prop.year_built
                    )

    @api.constrains('floor_area')
    def _check_floor_area(self):
        """Validate Floor Area is positive and reasonable"""
        for prop in self:
            if prop.floor_area:
                if prop.floor_area <= 0:
                    raise ValidationError(
                        _('Floor Area must be greater than zero. Got: %s') % prop.floor_area
                    )
                if prop.floor_area > 100000:  # 100,000 sqm is very large
                    raise ValidationError(
                        _('Floor Area seems unreasonably large (>100,000 sqm). Got: %s') % prop.floor_area
                    )

    @api.constrains('bedrooms', 'bathrooms', 'reception_rooms', 'number_of_floors')
    def _check_room_counts(self):
        """Validate room counts are non-negative"""
        for prop in self:
            if prop.bedrooms and prop.bedrooms < 0:
                raise ValidationError(_('Bedrooms cannot be negative.'))
            if prop.bathrooms and prop.bathrooms < 0:
                raise ValidationError(_('Bathrooms cannot be negative.'))
            if prop.reception_rooms and prop.reception_rooms < 0:
                raise ValidationError(_('Reception Rooms cannot be negative.'))
            if prop.number_of_floors and prop.number_of_floors < 1:
                raise ValidationError(_('Number of Floors must be at least 1.'))

    @api.onchange('epc_score')
    def _onchange_epc_score(self):
        """Auto-set EPC rating based on score"""
        if self.epc_score:
            if self.epc_score >= 92:
                self.epc_rating = 'a'
            elif self.epc_score >= 81:
                self.epc_rating = 'b'
            elif self.epc_score >= 69:
                self.epc_rating = 'c'
            elif self.epc_score >= 55:
                self.epc_rating = 'd'
            elif self.epc_score >= 39:
                self.epc_rating = 'e'
            elif self.epc_score >= 21:
                self.epc_rating = 'f'
            else:
                self.epc_rating = 'g'
