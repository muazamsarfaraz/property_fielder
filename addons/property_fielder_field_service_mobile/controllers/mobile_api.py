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
    
    @http.route('/mobile/api/auth/login', type='jsonrpc', auth='none', methods=['POST'], csrf=False, cors='*')
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
    
    @http.route('/mobile/api/jobs/my', type='jsonrpc', auth='user', methods=['GET'], cors='*')
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
    
    @http.route('/mobile/api/jobs/<int:job_id>', type='jsonrpc', auth='user', methods=['GET'], cors='*')
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

    @http.route('/mobile/api/jobs/<int:job_id>/checkin', type='jsonrpc', auth='user', methods=['POST'], cors='*')
    def checkin_job(self, job_id, latitude=None, longitude=None, accuracy=None, notes=None,
                    device_info=None, override_section_11=False, emergency_reason=''):
        """Check in to a job.

        Section 11 L&T Act 1985 Compliance:
        - Checks if 24-hour tenant notice has been given
        - Blocks check-in if notice not given (unless emergency override)
        - Emergency override requires documented reason
        """
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

            # ============================================================
            # SECTION 11 COMPLIANCE CHECK
            # ============================================================
            compliance = job.check_section_11_compliance()

            if not compliance['can_start']:
                # Check if emergency override requested
                if override_section_11:
                    if not emergency_reason:
                        return {
                            'success': False,
                            'error': 'Emergency override requires a documented reason.',
                            'section_11_blocked': True,
                            'compliance_status': compliance,
                        }
                    # Mark as emergency access
                    job.action_mark_emergency_access(emergency_reason)
                else:
                    return {
                        'success': False,
                        'error': compliance['reason'],
                        'section_11_blocked': True,
                        'compliance_status': compliance,
                        'hours_remaining': compliance.get('hours_remaining', 0),
                    }

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
                'message': 'Checked in successfully',
                'section_11_compliant': True,
            }
        except Exception as e:
            _logger.error(f'Check-in failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/mobile/api/jobs/<int:job_id>/checkout', type='jsonrpc', auth='user', methods=['POST'], cors='*')
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

    @http.route('/mobile/api/jobs/<int:job_id>/photos', type='jsonrpc', auth='user', methods=['POST'], cors='*')
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

    @http.route('/mobile/api/jobs/<int:job_id>/signature', type='jsonrpc', auth='user', methods=['POST'], cors='*')
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

    @http.route('/mobile/api/jobs/<int:job_id>/notes', type='jsonrpc', auth='user', methods=['POST'], cors='*')
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

    @http.route('/mobile/api/routes/my', type='jsonrpc', auth='user', methods=['GET'], cors='*')
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

    # ========== Safety Timer (Lone Worker Protection) ==========

    @http.route('/mobile/api/safety/timer/start', type='jsonrpc', auth='user', methods=['POST'], cors='*')
    def start_safety_timer(self, job_id=None, duration_minutes=60, latitude=None, longitude=None):
        """Start a safety timer for lone worker protection.

        HSE Compliance: Lone workers must be able to set a check-in timer.
        If the timer expires without being cancelled or extended, alerts are sent.
        """
        try:
            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Create timer
            timer = request.env['property_fielder.safety.timer'].start_timer_for_job(
                job_id=job_id,
                duration_minutes=duration_minutes,
                latitude=latitude,
                longitude=longitude
            )

            return {
                'success': True,
                'timer_id': timer.id,
                'expected_end': timer.expected_end.isoformat(),
                'message': f'Safety timer started for {duration_minutes} minutes'
            }
        except Exception as e:
            _logger.error(f'Start safety timer failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/mobile/api/safety/timer/extend', type='jsonrpc', auth='user', methods=['POST'], cors='*')
    def extend_safety_timer(self, timer_id=None, minutes=30, latitude=None, longitude=None):
        """Extend the current safety timer.

        Allows inspector to add more time if job is taking longer than expected.
        """
        try:
            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Find timer
            if timer_id:
                timer = request.env['property_fielder.safety.timer'].browse(timer_id)
            else:
                timer = request.env['property_fielder.safety.timer'].get_active_timer_for_inspector(
                    inspector.id
                )

            if not timer:
                return {'success': False, 'error': 'No active safety timer found'}

            # Update location if provided
            if latitude and longitude:
                timer.update_location(latitude, longitude)

            # Extend timer
            timer.action_extend(minutes)

            return {
                'success': True,
                'timer_id': timer.id,
                'new_expected_end': timer.expected_end.isoformat(),
                'extension_count': timer.extended_count,
                'message': f'Timer extended by {minutes} minutes'
            }
        except Exception as e:
            _logger.error(f'Extend safety timer failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/mobile/api/safety/timer/cancel', type='jsonrpc', auth='user', methods=['POST'])
    def cancel_safety_timer(self, timer_id=None):
        """Cancel/complete the safety timer (inspector is safe)."""
        try:
            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Find timer
            if timer_id:
                timer = request.env['property_fielder.safety.timer'].browse(timer_id)
            else:
                timer = request.env['property_fielder.safety.timer'].get_active_timer_for_inspector(
                    inspector.id
                )

            if not timer:
                return {'success': False, 'error': 'No active safety timer found'}

            # Complete timer
            timer.action_complete()

            return {
                'success': True,
                'timer_id': timer.id,
                'message': 'Safety timer completed - inspector safe'
            }
        except Exception as e:
            _logger.error(f'Cancel safety timer failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/mobile/api/safety/panic', type='jsonrpc', auth='user', methods=['POST'])
    def trigger_panic(self, reason='', latitude=None, longitude=None):
        """PANIC BUTTON - Trigger immediate emergency response.

        This immediately notifies:
        1. Inspector's emergency contact
        2. Field Service Manager
        3. Logs the event with location
        """
        try:
            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Find or create timer
            timer = request.env['property_fielder.safety.timer'].get_active_timer_for_inspector(
                inspector.id
            )

            if not timer:
                # Create emergency timer for panic
                from datetime import timedelta
                now = request.env['property_fielder.safety.timer'].fields.Datetime.now()
                timer = request.env['property_fielder.safety.timer'].create({
                    'inspector_id': inspector.id,
                    'started_at': now,
                    'expected_end': now + timedelta(minutes=1),
                    'state': 'active',
                })

            # Update location
            if latitude and longitude:
                timer.update_location(latitude, longitude)

            # Trigger panic
            timer.action_trigger_panic(reason)

            return {
                'success': True,
                'timer_id': timer.id,
                'message': '🚨 PANIC ALERT SENT - Help is on the way',
                'alert_sent': True
            }
        except Exception as e:
            _logger.error(f'Panic trigger failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    @http.route('/mobile/api/safety/status', type='jsonrpc', auth='user', methods=['GET'])
    def get_safety_status(self):
        """Get current safety timer status for the inspector."""
        try:
            # Get inspector
            inspector = request.env['property_fielder.inspector'].search([
                ('user_id', '=', request.env.user.id)
            ], limit=1)

            if not inspector:
                return {'success': False, 'error': 'No inspector profile found'}

            # Find active timer
            timer = request.env['property_fielder.safety.timer'].get_active_timer_for_inspector(
                inspector.id
            )

            if not timer:
                return {
                    'success': True,
                    'has_active_timer': False,
                    'timer': None
                }

            return {
                'success': True,
                'has_active_timer': True,
                'timer': {
                    'id': timer.id,
                    'state': timer.state,
                    'started_at': timer.started_at.isoformat(),
                    'expected_end': timer.expected_end.isoformat(),
                    'minutes_remaining': timer.minutes_remaining,
                    'is_overdue': timer.is_overdue,
                    'extension_count': timer.extended_count,
                    'job_id': timer.job_id.id if timer.job_id else None,
                    'job_name': timer.job_id.name if timer.job_id else None,
                }
            }
        except Exception as e:
            _logger.error(f'Get safety status failed: {str(e)}', exc_info=True)
            return {'success': False, 'error': str(e)}

    # ========== Sync ==========

    @http.route('/mobile/api/sync', type='jsonrpc', auth='user', methods=['POST'])
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

