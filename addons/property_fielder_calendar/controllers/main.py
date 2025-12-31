# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class CalendarOAuthController(http.Controller):
    """Handle OAuth2 callbacks from Google and Microsoft"""
    
    @http.route('/calendar/oauth/google/callback', type='http', auth='user')
    def google_oauth_callback(self, **kwargs):
        """Handle Google OAuth2 callback"""
        code = kwargs.get('code')
        state = kwargs.get('state')  # Inspector calendar ID
        error = kwargs.get('error')
        
        if error:
            _logger.error(f"Google OAuth error: {error}")
            return request.redirect('/web#action=property_fielder_calendar.action_inspector_calendar&error=oauth_failed')
        
        if not code or not state:
            return request.redirect('/web#error=missing_params')
        
        try:
            inspector_calendar = request.env['property_fielder.inspector.calendar'].browse(int(state))
            if not inspector_calendar.exists():
                return request.redirect('/web#error=invalid_state')
            
            # Exchange code for tokens
            config = inspector_calendar._get_provider_config()
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
            redirect_uri = f"{base_url}/calendar/oauth/google/callback"
            
            # In production, would exchange code for tokens via Google API
            # For now, simulate successful connection
            inspector_calendar.sudo().write({
                'access_token': 'simulated_access_token',
                'refresh_token': 'simulated_refresh_token',
                'connection_status': 'connected',
                'calendar_id': 'primary',
                'calendar_name': 'Primary Calendar',
            })
            
            return request.redirect('/web#action=property_fielder_calendar.action_inspector_calendar&success=connected')
            
        except Exception as e:
            _logger.error(f"Google OAuth callback error: {e}")
            return request.redirect('/web#error=callback_failed')
    
    @http.route('/calendar/oauth/microsoft/callback', type='http', auth='user')
    def microsoft_oauth_callback(self, **kwargs):
        """Handle Microsoft OAuth2 callback"""
        code = kwargs.get('code')
        state = kwargs.get('state')
        error = kwargs.get('error')
        
        if error:
            _logger.error(f"Microsoft OAuth error: {error} - {kwargs.get('error_description')}")
            return request.redirect('/web#action=property_fielder_calendar.action_inspector_calendar&error=oauth_failed')
        
        if not code or not state:
            return request.redirect('/web#error=missing_params')
        
        try:
            inspector_calendar = request.env['property_fielder.inspector.calendar'].browse(int(state))
            if not inspector_calendar.exists():
                return request.redirect('/web#error=invalid_state')
            
            # In production, would exchange code for tokens via Microsoft Graph API
            inspector_calendar.sudo().write({
                'access_token': 'simulated_access_token',
                'refresh_token': 'simulated_refresh_token',
                'connection_status': 'connected',
                'calendar_id': 'default',
                'calendar_name': 'Outlook Calendar',
            })
            
            return request.redirect('/web#action=property_fielder_calendar.action_inspector_calendar&success=connected')
            
        except Exception as e:
            _logger.error(f"Microsoft OAuth callback error: {e}")
            return request.redirect('/web#error=callback_failed')

