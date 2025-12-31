# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
import re

_logger = logging.getLogger(__name__)

try:
    from twilio.rest import Client
    from twilio.base.exceptions import TwilioRestException
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    _logger.warning('Twilio library not installed. SMS features will be disabled.')


class SMSService(models.AbstractModel):
    """SMS Service - handles sending SMS via Twilio"""
    
    _name = 'property_fielder.sms.service'
    _description = 'SMS Service'
    
    @api.model
    def _check_twilio(self):
        """Check if Twilio is available"""
        if not TWILIO_AVAILABLE:
            raise UserError(_('Twilio library is not installed. Please install it with: pip install twilio'))
    
    @api.model
    def _normalize_phone(self, phone_number):
        """Normalize phone number to E.164 format"""
        if not phone_number:
            return None
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone_number)
        # Handle UK numbers
        if cleaned.startswith('0') and len(cleaned) == 11:
            cleaned = '+44' + cleaned[1:]
        elif cleaned.startswith('44') and not cleaned.startswith('+'):
            cleaned = '+' + cleaned
        elif not cleaned.startswith('+'):
            cleaned = '+44' + cleaned  # Assume UK
        return cleaned
    
    @api.model
    def send_sms(self, to_number, message, config=None, job_id=None, partner_id=None, 
                 template_id=None, message_type='custom'):
        """Send SMS via Twilio"""
        self._check_twilio()
        
        if not config:
            config = self.env['property_fielder.sms.config'].get_config()
        
        # Check rate limiting
        if config.sms_sent_today >= config.max_sms_per_day:
            _logger.warning('SMS daily limit reached')
            return {'success': False, 'error': 'Daily SMS limit reached'}
        
        # Normalize phone number
        to_number = self._normalize_phone(to_number)
        if not to_number:
            return {'success': False, 'error': 'Invalid phone number'}
        
        # Get credentials
        creds = config.get_credentials()
        
        # Create log entry
        log = self.env['property_fielder.sms.log'].create({
            'to_number': to_number,
            'from_number': creds['phone_number'],
            'message_body': message,
            'status': 'pending',
            'direction': 'outbound',
            'job_id': job_id,
            'partner_id': partner_id,
            'template_id': template_id,
            'message_type': message_type,
            'segment_count': (len(message) // 160) + 1,
        })
        
        try:
            client = Client(creds['account_sid'], creds['auth_token'])
            
            twilio_message = client.messages.create(
                body=message,
                from_=creds['phone_number'],
                to=to_number
            )
            
            # Update log with success
            log.write({
                'status': 'sent',
                'twilio_sid': twilio_message.sid,
                'sent_time': fields.Datetime.now(),
            })
            
            # Update counter
            config.sudo().write({'sms_sent_today': config.sms_sent_today + 1})
            
            _logger.info(f'SMS sent successfully to {to_number}, SID: {twilio_message.sid}')
            return {'success': True, 'sid': twilio_message.sid, 'log_id': log.id}
            
        except TwilioRestException as e:
            _logger.error(f'Twilio error: {e}')
            log.write({'status': 'failed', 'error_message': str(e)})
            return {'success': False, 'error': str(e), 'log_id': log.id}
        except Exception as e:
            _logger.error(f'SMS error: {e}')
            log.write({'status': 'failed', 'error_message': str(e)})
            return {'success': False, 'error': str(e), 'log_id': log.id}
    
    @api.model
    def send_template_sms(self, to_number, template_code, values, **kwargs):
        """Send SMS using a template"""
        template = self.env['property_fielder.sms.template'].get_template(template_code)
        if not template:
            return {'success': False, 'error': f'Template {template_code} not found'}
        
        message = template.render_message(values)
        return self.send_sms(to_number, message, template_id=template.id, **kwargs)

