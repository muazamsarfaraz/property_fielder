# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging
import os

_logger = logging.getLogger(__name__)


class FieldServiceController(http.Controller):
    """HTTP controllers for Field Service addon"""

    @http.route('/property_fielder/config', type='json', auth='user', methods=['POST'])
    def get_config(self):
        """Get configuration for dispatch view (Mapbox token, etc.)"""
        # Get Mapbox token from environment variable or system parameter
        mapbox_token = os.environ.get('MAPBOX_ACCESS_TOKEN') or \
                      request.env['ir.config_parameter'].sudo().get_param(
                          'property_fielder.mapbox.token',
                          'pk.eyJ1IjoibXVhemFtc2FyZmFyYXoiLCJhIjoiY205b2dzdnVlMTVuZDJqczcwbnBseW1tYiJ9.-MvfX63GtzUQceap1g6iJQ'
                      )

        return {
            'mapbox_token': mapbox_token,
            'osrm_url': request.env['ir.config_parameter'].sudo().get_param(
                'property_fielder.osrm.url',
                'https://osrmproj-production.up.railway.app'
            ),
        }

    @http.route('/Property Fielder/api/jobs', type='jsonrpc', auth='user', methods=['GET'])
    def get_jobs(self, date=None, inspector_id=None):
        """Get jobs for a specific date and/or inspector"""
        domain = []
        
        if date:
            domain.append(('scheduled_date', '=', date))
        
        if inspector_id:
            domain.append(('inspector_id', '=', int(inspector_id)))
        
        jobs = request.env['property_fielder.job'].search(domain)
        
        return {
            'jobs': [{
                'id': job.id,
                'name': job.name,
                'job_number': job.job_number,
                'customer': job.partner_id.name,
                'latitude': job.latitude,
                'longitude': job.longitude,
                'scheduled_date': job.scheduled_date.isoformat() if job.scheduled_date else None,
                'duration_minutes': job.duration_minutes,
                'state': job.state,
                'inspector': job.inspector_id.name if job.inspector_id else None,
            } for job in jobs]
        }
    
    @http.route('/Property Fielder/api/routes', type='jsonrpc', auth='user', methods=['GET'])
    def get_routes(self, date=None, inspector_id=None):
        """Get routes for a specific date and/or inspector"""
        domain = []
        
        if date:
            domain.append(('route_date', '=', date))
        
        if inspector_id:
            domain.append(('inspector_id', '=', int(inspector_id)))
        
        routes = request.env['property_fielder.route'].search(domain)
        
        return {
            'routes': [{
                'id': route.id,
                'name': route.name,
                'route_number': route.route_number,
                'inspector': route.inspector_id.name,
                'route_date': route.route_date.isoformat() if route.route_date else None,
                'job_count': route.job_count,
                'total_distance_km': route.total_distance_km,
                'total_time_minutes': route.total_time_minutes,
                'state': route.state,
                'jobs': [{
                    'id': job.id,
                    'name': job.name,
                    'latitude': job.latitude,
                    'longitude': job.longitude,
                } for job in route.job_ids]
            } for route in routes]
        }
    
    @http.route('/Property Fielder/api/optimize', type='jsonrpc', auth='user', methods=['POST'])
    def run_optimization(self, job_ids, inspector_ids, date, use_osrm=False, solver_time=30):
        """Run route optimization"""
        try:
            # Create optimization record
            optimization = request.env['property_fielder.optimization'].create({
                'name': f'Route Optimization - {date}',
                'optimization_date': date,
                'use_osrm': use_osrm,
                'solver_time_seconds': solver_time,
                'job_ids': [(6, 0, job_ids)],
                'inspector_ids': [(6, 0, inspector_ids)],
            })
            
            # Run optimization
            optimization.action_run_optimization()
            
            return {
                'success': True,
                'optimization_id': optimization.id,
                'message': 'Optimization completed successfully',
                'routes': len(optimization.route_ids),
                'jobs_assigned': optimization.total_jobs_assigned,
            }
            
        except Exception as e:
            _logger.error(f'Optimization failed: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/Property Fielder/api/distance', type='jsonrpc', auth='user', methods=['POST'])
    def calculate_distance(self, from_lat, from_lon, to_lat, to_lon, use_osrm=False):
        """Calculate distance between two points"""
        try:
            if use_osrm:
                # Use OSRM for real road distance
                osrm_url = request.env['ir.config_parameter'].sudo().get_param(
                    'property_fielder.osrm.url',
                    'https://router.project-osrm.org'
                )
                
                import requests
                response = requests.get(
                    f'{osrm_url}/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}',
                    params={'overview': 'false'},
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == 'Ok':
                        route = data['routes'][0]
                        return {
                            'success': True,
                            'distance_meters': route['distance'],
                            'duration_seconds': route['duration'],
                            'method': 'osrm'
                        }
            
            # Fallback to Haversine
            from math import radians, sin, cos, sqrt, atan2
            
            R = 6371000  # Earth radius in meters
            lat1, lon1 = radians(from_lat), radians(from_lon)
            lat2, lon2 = radians(to_lat), radians(to_lon)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            distance = R * c
            
            # Assume 50 km/h average speed
            duration = distance / (50000 / 3600)
            
            return {
                'success': True,
                'distance_meters': distance,
                'duration_seconds': duration,
                'method': 'haversine'
            }
            
        except Exception as e:
            _logger.error(f'Distance calculation failed: {str(e)}', exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

