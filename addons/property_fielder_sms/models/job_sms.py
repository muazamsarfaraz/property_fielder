# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class JobSMS(models.Model):
    """Extend Job model with SMS capabilities"""
    
    _inherit = 'property_fielder.job'
    
    # SMS tracking
    sms_log_ids = fields.One2many('property_fielder.sms.log', 'job_id', string='SMS Log')
    sms_count = fields.Integer(string='SMS Count', compute='_compute_sms_count')
    last_sms_sent = fields.Datetime(string='Last SMS Sent', compute='_compute_last_sms_sent')
    
    @api.depends('sms_log_ids')
    def _compute_sms_count(self):
        for job in self:
            job.sms_count = len(job.sms_log_ids)
    
    @api.depends('sms_log_ids')
    def _compute_last_sms_sent(self):
        for job in self:
            last_log = job.sms_log_ids.filtered(
                lambda l: l.direction == 'outbound' and l.status == 'sent'
            ).sorted('sent_time', reverse=True)[:1]
            job.last_sms_sent = last_log.sent_time if last_log else False
    
    def _get_sms_values(self):
        """Get template values for SMS"""
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        
        # Format scheduled time
        scheduled_time = ''
        if self.earliest_start and self.latest_end:
            start = self.earliest_start.strftime('%H:%M')
            end = self.latest_end.strftime('%H:%M')
            scheduled_time = f'{start} - {end}'
        
        return {
            'owner_name': self.partner_id.name or 'Customer',
            'property_address': f'{self.street or ""}, {self.city or ""}'.strip(', '),
            'scheduled_date': self.scheduled_date.strftime('%A, %d %B %Y') if self.scheduled_date else 'TBC',
            'scheduled_time': scheduled_time or 'TBC',
            'inspector_name': self.inspector_id.name if self.inspector_id else 'TBC',
            'job_type': self.name or 'Inspection',
            'confirmation_link': f'{base_url}/appointment/{self.confirmation_token}' if self.confirmation_token else '',
            'company_name': self.env.company.name,
            'company_phone': self.env.company.phone or '',
        }
    
    def action_send_confirmation_sms(self):
        """Send appointment confirmation SMS to owner"""
        self.ensure_one()
        if not self.partner_id.mobile and not self.partner_id.phone:
            raise UserError(_('No phone number found for %s') % self.partner_id.name)
        
        phone = self.partner_id.mobile or self.partner_id.phone
        values = self._get_sms_values()
        
        sms_service = self.env['property_fielder.sms.service']
        result = sms_service.send_template_sms(
            to_number=phone,
            template_code='appointment_confirmation',
            values=values,
            job_id=self.id,
            partner_id=self.partner_id.id,
            message_type='confirmation'
        )
        
        if result.get('success'):
            self.message_post(body=_('Confirmation SMS sent to %s') % phone)
        else:
            self.message_post(body=_('Failed to send SMS: %s') % result.get('error'))
        
        return result
    
    def action_send_reminder_sms(self):
        """Send appointment reminder SMS"""
        self.ensure_one()
        if not self.partner_id.mobile and not self.partner_id.phone:
            return {'success': False, 'error': 'No phone number'}
        
        phone = self.partner_id.mobile or self.partner_id.phone
        values = self._get_sms_values()
        
        sms_service = self.env['property_fielder.sms.service']
        result = sms_service.send_template_sms(
            to_number=phone,
            template_code='appointment_reminder',
            values=values,
            job_id=self.id,
            partner_id=self.partner_id.id,
            message_type='reminder'
        )
        
        if result.get('success'):
            self.message_post(body=_('Reminder SMS sent to %s') % phone)
        
        return result
    
    def action_view_sms_log(self):
        """View SMS log for this job"""
        self.ensure_one()
        return {
            'name': _('SMS Log'),
            'type': 'ir.actions.act_window',
            'res_model': 'property_fielder.sms.log',
            'view_mode': 'list,form',
            'domain': [('job_id', '=', self.id)],
            'context': {'default_job_id': self.id},
        }
    
    @api.model
    def _cron_send_reminder_sms(self):
        """Cron job to send reminder SMS for upcoming appointments"""
        config = self.env['property_fielder.sms.config'].search([('active', '=', True)], limit=1)
        if not config or not config.send_reminder_sms:
            return
        
        from datetime import timedelta
        reminder_datetime = fields.Datetime.now() + timedelta(hours=config.reminder_hours_before)
        
        # Find jobs scheduled within the reminder window that haven't had a reminder sent
        jobs = self.search([
            ('state', 'in', ['scheduled', 'draft']),
            ('scheduled_date', '<=', reminder_datetime.date()),
            ('scheduled_date', '>=', fields.Date.today()),
        ])
        
        for job in jobs:
            # Check if reminder already sent
            existing_reminder = self.env['property_fielder.sms.log'].search([
                ('job_id', '=', job.id),
                ('message_type', '=', 'reminder'),
                ('status', '=', 'sent'),
            ], limit=1)
            
            if not existing_reminder:
                job.action_send_reminder_sms()

