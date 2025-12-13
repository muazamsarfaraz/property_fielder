# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import base64
import logging

_logger = logging.getLogger(__name__)


class MobileAPIController(http.Controller):
    """REST API for mobile app"""
    
    # ========== Authentication ==========
    
    @http.route('/mobile/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def mobile_login(self, username, password):
        """Mobile app login"""
        try:
            uid = request.session.authenticate(request.session.db, username, password)
            if uid:
                # Get inspector for this user
                inspector = request.env['property_fielder.inspector'].sudo().search([
                    ('user_id', '=', uid)
                ], limit=1)
                
                if not inspector:
                    return {
                        'success': False,
                        'error': 'No inspector profile found for this user'
                    }
                
                return {
                    'success': True,
                    'user_id': uid,
                    'inspector_id': inspector.id,
                    'inspector_name': inspector.name,
                    'session_id': request.session.sid
                }
            else:
                return {
                    'success': False,
                    'error': 'Invalid credentials'
                }
        except Exception as e:
            _logger.error(f'Mobile login failed: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    # ========== Jobs ==========
    
    @http.route('/mobile/api/jobs/my', type='json', auth='user', methods=['GET'])
    def get_my_jobs(self, date=None, status=None):
        """Get jobs assigned to current inspector"""
        try:
            # Get inspector for current user
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)
            
            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}
            
            # Build domain
            domain = [('inspector_id', '=', inspector.id)]
            
            if date:
                domain.append(('scheduled_date', '=', date))
            
            if status:
                domain.append(('state', '=', status))
            
            # Get jobs
            jobs = request.env['property_fielder.job'].search(domain)
            
            return {
                'success': True,
                'jobs': [{
                    'id': job.id,
                    'job_number': job.job_number,
                    'name': job.name,
                    'customer_name': job.partner_id.name,
                    'customer_phone': job.partner_id.phone,
                    'address': job.street,
                    'city': job.city,
                    'latitude': job.latitude,
                    'longitude': job.longitude,
                    'scheduled_date': job.scheduled_date.isoformat() if job.scheduled_date else None,
                    'earliest_start': job.earliest_start.isoformat() if job.earliest_start else None,
                    'latest_end': job.latest_end.isoformat() if job.latest_end else None,
                    'duration_minutes': job.duration_minutes,
                    'priority': job.priority,
                    'state': job.state,
                    'skills': [skill.name for skill in job.skill_ids],
                    'notes': job.notes,
                } for job in jobs]
            }
        except Exception as e:
            _logger.error(f'Get my jobs failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}
    
    @http.route('/mobile/api/jobs/<int:job_id>', type='json', auth='user', methods=['GET'])
    def get_job_detail(self, job_id):
        """Get detailed job information"""
        try:
            job = request.env['property_fielder.job'].browse(job_id)
            
            if not job.exists():
                return {'success': False, 'error': 'Job not found'}
            
            # Get related data
            checkins = request.env['property_fielder.job.checkin'].search([
                ('job_id', '=', job_id)
            ])
            
            photos = request.env['property_fielder.job.photo'].search([
                ('job_id', '=', job_id)
            ])
            
            signatures = request.env['property_fielder.job.signature'].search([
                ('job_id', '=', job_id)
            ])
            
            notes = request.env['property_fielder.job.note'].search([
                ('job_id', '=', job_id)
            ])
            
            return {
                'success': True,
                'job': {
                    'id': job.id,
                    'job_number': job.job_number,
                    'name': job.name,
                    'customer': {
                        'name': job.partner_id.name,
                        'phone': job.partner_id.phone,
                        'email': job.partner_id.email,
                    },
                    'address': {
                        'street': job.street,
                        'city': job.city,
                        'state': job.state_id.name if job.state_id else None,
                        'zip': job.zip,
                        'latitude': job.latitude,
                        'longitude': job.longitude,
                    },
                    'schedule': {
                        'date': job.scheduled_date.isoformat() if job.scheduled_date else None,
                        'earliest_start': job.earliest_start.isoformat() if job.earliest_start else None,
                        'latest_end': job.latest_end.isoformat() if job.latest_end else None,
                        'duration_minutes': job.duration_minutes,
                    },
                    'priority': job.priority,
                    'state': job.state,
                    'skills': [skill.name for skill in job.skill_ids],
                    'notes': job.notes,
                    'checkins': len(checkins),
                    'photos': len(photos),
                    'signatures': len(signatures),
                    'notes_count': len(notes),
                }
            }
        except Exception as e:
            _logger.error(f'Get job detail failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    # ========== Check-In/Out ==========

    @http.route('/mobile/api/jobs/<int:job_id>/checkin', type='json', auth='user', methods=['POST'])
    def checkin_job(self, job_id, latitude=None, longitude=None, accuracy=None, notes=None, device_info=None):
        """Check in to a job"""
        try:
            job = request.env['property_fielder.job'].browse(job_id)

            if not job.exists():
                return {'success': False, 'error': 'Job not found'}

            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Create check-in
            checkin = request.env['property_fielder.job.checkin'].create({
                'job_id': job_id,
                'inspector_id': inspector.id,
                'checkin_latitude': latitude,
                'checkin_longitude': longitude,
                'checkin_accuracy': accuracy,
                'checkin_notes': notes,
                'device_info': device_info,
                'status': 'checked_in'
            })

            # Update job status
            if job.state in ['draft', 'pending', 'assigned']:
                job.write({'state': 'in_progress'})

            return {
                'success': True,
                'checkin_id': checkin.id,
                'message': 'Checked in successfully'
            }
        except Exception as e:
            _logger.error(f'Check-in failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/mobile/api/jobs/<int:job_id>/checkout', type='json', auth='user', methods=['POST'])
    def checkout_job(self, job_id, latitude=None, longitude=None, notes=None):
        """Check out from a job"""
        try:
            # Find active check-in
            checkin = request.env['property_fielder.job.checkin'].search([
                ('job_id', '=', job_id),
                ('status', '=', 'checked_in')
            ], limit=1)

            if not checkin:
                return {'success': False, 'error': 'No active check-in found'}

            # Check out
            checkin.action_checkout(latitude=latitude, longitude=longitude, notes=notes)

            return {
                'success': True,
                'message': 'Checked out successfully',
                'duration_minutes': checkin.duration_minutes
            }
        except Exception as e:
            _logger.error(f'Check-out failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    # ========== Photos ==========

    @http.route('/mobile/api/jobs/<int:job_id>/photos', type='json', auth='user', methods=['POST'])
    def upload_photo(self, job_id, image_data, name='Photo', category='during',
                     latitude=None, longitude=None, notes=None, device_info=None):
        """Upload a photo for a job"""
        try:
            job = request.env['property_fielder.job'].browse(job_id)

            if not job.exists():
                return {'success': False, 'error': 'Job not found'}

            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Create photo
            photo = request.env['property_fielder.job.photo'].create({
                'job_id': job_id,
                'inspector_id': inspector.id,
                'name': name,
                'image': image_data,  # Base64 encoded
                'category': category,
                'latitude': latitude,
                'longitude': longitude,
                'notes': notes,
                'device_info': device_info
            })

            return {
                'success': True,
                'photo_id': photo.id,
                'message': 'Photo uploaded successfully'
            }
        except Exception as e:
            _logger.error(f'Photo upload failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    # ========== Signatures ==========

    @http.route('/mobile/api/jobs/<int:job_id>/signature', type='json', auth='user', methods=['POST'])
    def capture_signature(self, job_id, signature_data, signer_name, signer_title=None,
                         signer_email=None, signer_phone=None, signature_type='completion',
                         latitude=None, longitude=None, notes=None, agreement_text=None,
                         device_info=None):
        """Capture customer signature"""
        try:
            job = request.env['property_fielder.job'].browse(job_id)

            if not job.exists():
                return {'success': False, 'error': 'Job not found'}

            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Create signature
            signature = request.env['property_fielder.job.signature'].create({
                'job_id': job_id,
                'inspector_id': inspector.id,
                'signature': signature_data,  # Base64 encoded
                'signer_name': signer_name,
                'signer_title': signer_title,
                'signer_email': signer_email,
                'signer_phone': signer_phone,
                'signature_type': signature_type,
                'latitude': latitude,
                'longitude': longitude,
                'notes': notes,
                'agreement_text': agreement_text,
                'device_info': device_info
            })

            return {
                'success': True,
                'signature_id': signature.id,
                'message': 'Signature captured successfully'
            }
        except Exception as e:
            _logger.error(f'Signature capture failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    # ========== Notes ==========

    @http.route('/mobile/api/jobs/<int:job_id>/notes', type='json', auth='user', methods=['POST'])
    def add_note(self, job_id, title, content, category='general', priority='normal',
                 latitude=None, longitude=None, requires_follow_up=False, follow_up_date=None):
        """Add a note to a job"""
        try:
            job = request.env['property_fielder.job'].browse(job_id)

            if not job.exists():
                return {'success': False, 'error': 'Job not found'}

            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Create note
            note = request.env['property_fielder.job.note'].create({
                'job_id': job_id,
                'inspector_id': inspector.id,
                'title': title,
                'content': content,
                'category': category,
                'priority': priority,
                'latitude': latitude,
                'longitude': longitude,
                'requires_follow_up': requires_follow_up,
                'follow_up_date': follow_up_date
            })

            return {
                'success': True,
                'note_id': note.id,
                'message': 'Note added successfully'
            }
        except Exception as e:
            _logger.error(f'Add note failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    # ========== Routes ==========

    @http.route('/mobile/api/routes/my', type='json', auth='user', methods=['GET'])
    def get_my_routes(self, date=None):
        """Get routes assigned to current inspector"""
        try:
            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Build domain
            domain = [('inspector_id', '=', inspector.id)]

            if date:
                domain.append(('route_date', '=', date))

            # Get routes
            routes = request.env['property_fielder.route'].search(domain)

            return {
                'success': True,
                'routes': [{
                    'id': route.id,
                    'route_number': route.route_number,
                    'name': route.name,
                    'route_date': route.route_date.isoformat() if route.route_date else None,
                    'job_count': route.job_count,
                    'total_distance_km': route.total_distance_km,
                    'total_time_minutes': route.total_time_minutes,
                    'state': route.state,
                    'jobs': [{
                        'id': job.id,
                        'job_number': job.job_number,
                        'name': job.name,
                        'customer_name': job.partner_id.name,
                        'latitude': job.latitude,
                        'longitude': job.longitude,
                        'state': job.state,
                    } for job in route.job_ids]
                } for route in routes]
            }
        except Exception as e:
            _logger.error(f'Get my routes failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    # ========== Sync ==========

    @http.route('/mobile/api/sync', type='json', auth='user', methods=['POST'])
    def sync_data(self, sync_type='incremental', device_id=None, device_info=None,
                  app_version=None, network_type=None):
        """Sync mobile app data"""
        try:
            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Create sync log
            sync_log = request.env['property_fielder.mobile.sync'].create({
                'inspector_id': inspector.id,
                'user_id': request.env.user.id,
                'sync_type': sync_type,
                'device_id': device_id,
                'device_info': device_info,
                'app_version': app_version,
                'network_type': network_type,
                'status': 'success'
            })

            # Get data to sync
            # Jobs for today and tomorrow
            from datetime import date, timedelta
            today = date.today()
            tomorrow = today + timedelta(days=1)

            jobs = request.env['property_fielder.job'].search([
                ('inspector_id', '=', inspector.id),
                ('scheduled_date', 'in', [today, tomorrow])
            ])

            routes = request.env['property_fielder.route'].search([
                ('inspector_id', '=', inspector.id),
                ('route_date', 'in', [today, tomorrow])
            ])

            # Update sync log
            sync_log.write({
                'jobs_downloaded': len(jobs),
            })

            return {
                'success': True,
                'sync_id': sync_log.id,
                'jobs': [{
                    'id': job.id,
                    'job_number': job.job_number,
                    'name': job.name,
                    'customer_name': job.partner_id.name,
                    'latitude': job.latitude,
                    'longitude': job.longitude,
                    'scheduled_date': job.scheduled_date.isoformat() if job.scheduled_date else None,
                    'state': job.state,
                } for job in jobs],
                'routes': [{
                    'id': route.id,
                    'route_number': route.route_number,
                    'name': route.name,
                    'route_date': route.route_date.isoformat() if route.route_date else None,
                } for route in routes]
            }
        except Exception as e:
            _logger.error(f'Sync failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

