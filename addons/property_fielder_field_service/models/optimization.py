# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import requests
import logging

_logger = logging.getLogger(__name__)


class FieldServiceOptimization(models.Model):
    """Route optimization runs using Timefold Solver"""
    
    _name = 'property_fielder.optimization'
    _description = 'Route Optimization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    
    # Basic Information
    name = fields.Char(
        string='Optimization Name',
        required=True,
        default=lambda self: _('Route Optimization'),
        tracking=True
    )
    
    optimization_date = fields.Date(
        string='Optimization Date',
        required=True,
        default=fields.Date.context_today,
        help='Date to optimize routes for'
    )
    
    # Configuration
    use_osrm = fields.Boolean(
        string='Use OSRM Routing',
        default=False,
        help='Use real road routing (OSRM) instead of straight-line distance'
    )
    
    solver_time_seconds = fields.Integer(
        string='Solver Time (seconds)',
        default=30,
        help='How long to run the optimization'
    )
    
    # Input
    job_ids = fields.Many2many(
        'property_fielder.job',
        'optimization_job_rel',
        'optimization_id',
        'job_id',
        string='Jobs to Optimize',
        help='Jobs to include in optimization'
    )
    
    inspector_ids = fields.Many2many(
        'property_fielder.inspector',
        'optimization_inspector_rel',
        'optimization_id',
        'inspector_id',
        string='Available Inspectors',
        help='Inspectors available for assignment'
    )
    
    # Output
    route_ids = fields.One2many(
        'property_fielder.route',
        'optimization_id',
        string='Generated Routes',
        readonly=True
    )
    
    # Results
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', required=True, tracking=True)
    
    score = fields.Char(
        string='Optimization Score',
        readonly=True,
        help='Score from Timefold Solver'
    )
    
    total_routes = fields.Integer(
        string='Total Routes',
        compute='_compute_route_stats',
        store=True
    )
    
    total_jobs_assigned = fields.Integer(
        string='Jobs Assigned',
        compute='_compute_route_stats',
        store=True
    )
    
    total_distance_km = fields.Float(
        string='Total Distance (km)',
        compute='_compute_route_stats',
        store=True,
        digits=(10, 2)
    )
    
    error_message = fields.Text(
        string='Error Message',
        readonly=True
    )
    
    # Technical
    request_json = fields.Text(string='Request JSON', readonly=True)
    response_json = fields.Text(string='Response JSON', readonly=True)
    
    @api.depends('route_ids', 'route_ids.job_count', 'route_ids.total_distance_km')
    def _compute_route_stats(self):
        """Calculate statistics from routes"""
        for opt in self:
            opt.total_routes = len(opt.route_ids)
            opt.total_jobs_assigned = sum(route.job_count for route in opt.route_ids)
            opt.total_distance_km = sum(route.total_distance_km for route in opt.route_ids)

    @api.model
    def run_optimization(self, job_ids, inspector_ids, optimization_date):
        """Create and run optimization - called from JavaScript dispatch view

        Args:
            job_ids: List of job IDs to optimize
            inspector_ids: List of inspector IDs to use
            optimization_date: Date string (YYYY-MM-DD) for the optimization

        Returns:
            dict with optimization results
        """
        from datetime import datetime

        if not job_ids:
            raise UserError(_('Please select jobs to optimize'))
        if not inspector_ids:
            raise UserError(_('Please select inspectors for routing'))

        # Parse date
        if isinstance(optimization_date, str):
            opt_date = datetime.strptime(optimization_date, '%Y-%m-%d').date()
        else:
            opt_date = optimization_date

        # Create optimization record
        optimization = self.create({
            'name': f'Dispatch Optimization {opt_date}',
            'optimization_date': opt_date,
            'job_ids': [(6, 0, job_ids)],
            'inspector_ids': [(6, 0, inspector_ids)],
            'state': 'draft',
        })

        # Run the optimization
        optimization.action_run_optimization()

        # Return results
        return {
            'id': optimization.id,
            'name': optimization.name,
            'state': optimization.state,
            'score': optimization.score,
            'total_routes': optimization.total_routes,
            'total_jobs_assigned': optimization.total_jobs_assigned,
            'total_distance_km': optimization.total_distance_km,
            'error_message': optimization.error_message,
        }

    def action_run_optimization(self):
        """Run route optimization using Timefold Solver"""
        self.ensure_one()
        
        if not self.job_ids:
            raise UserError(_('Please select jobs to optimize'))

        if not self.inspector_ids:
            raise UserError(_('Please select available inspectors'))

        # Update state
        self.write({'state': 'running'})

        try:
            import time

            # Get Timefold server URL from system parameters
            timefold_url = self.env['ir.config_parameter'].sudo().get_param(
                'property_fielder.timefold.url',
                'http://localhost:8080'
            )

            # Build request payload
            request_data = self._build_timefold_request()
            self.request_json = json.dumps(request_data, indent=2)

            # Submit to Timefold API (async - returns job ID)
            _logger.info(f'Submitting to Timefold API at {timefold_url}')
            _logger.info(f'Request: {len(request_data.get("visits", []))} visits, '
                        f'{len(request_data.get("vehicles", []))} vehicles')

            response = requests.post(
                f'{timefold_url}/route-plans',
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            response.raise_for_status()
            job_id = response.text.strip().strip('"')  # Response is plain text job ID
            _logger.info(f'Timefold job submitted: {job_id}')

            # Poll for result
            max_wait = self.solver_time_seconds + 30
            poll_interval = 2  # seconds
            elapsed = 0
            result = None

            while elapsed < max_wait:
                time.sleep(poll_interval)
                elapsed += poll_interval

                # Get current solution
                status_response = requests.get(
                    f'{timefold_url}/route-plans/{job_id}',
                    timeout=30
                )
                status_response.raise_for_status()
                result = status_response.json()

                solver_status = result.get('solverStatus', 'UNKNOWN')
                score = result.get('score', 'N/A')
                _logger.info(f'Timefold status: {solver_status}, score: {score}, elapsed: {elapsed}s')

                # Check if solving is complete
                if solver_status == 'NOT_SOLVING':
                    _logger.info(f'Optimization complete after {elapsed}s')
                    break

                # If we've waited long enough, terminate early
                if elapsed >= self.solver_time_seconds:
                    _logger.info(f'Terminating solver after {elapsed}s')
                    try:
                        requests.delete(f'{timefold_url}/route-plans/{job_id}', timeout=10)
                    except Exception:
                        pass
                    break

            if not result:
                raise UserError(_('No result received from Timefold'))

            self.response_json = json.dumps(result, indent=2)

            # Process results
            self._process_timefold_response(result)

            self.write({
                'state': 'completed',
                'score': str(result.get('score', 'N/A'))
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('Optimization completed! Score: %s') % result.get('score', 'N/A'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f'Timefold API error: {str(e)}', exc_info=True)
            self.write({
                'state': 'failed',
                'error_message': f'API Error: {str(e)}'
            })
            raise UserError(_('Timefold API error: %s') % str(e))
        except Exception as e:
            _logger.error(f'Optimization failed: {str(e)}', exc_info=True)
            self.write({
                'state': 'failed',
                'error_message': str(e)
            })
            raise UserError(_('Optimization failed: %s') % str(e))

    def _build_timefold_request(self):
        """Build request payload for Timefold API

        Format matches the Timefold vehicle-routing service:
        - locations are [lat, lng] arrays
        - serviceDuration is in seconds
        - time fields are ISO datetime strings
        """
        self.ensure_one()
        from datetime import datetime, timedelta

        # Build visits from jobs
        visits = []
        for job in self.job_ids:
            visit = {
                'id': str(job.id),
                'name': job.name,
                'location': [job.latitude, job.longitude],
                'demand': 1,  # Each job = 1 unit of demand
                # CRITICAL: Timefold DurationDeserializer expects MILLISECONDS, not seconds!
                # See SERVICE_DURATION_DESERIALIZATION_FIX.md in old platform docs
                'serviceDuration': job.duration_minutes * 60 * 1000,  # Convert to milliseconds
            }

            # Add time window constraints
            if job.earliest_start:
                visit['minStartTime'] = job.earliest_start.isoformat()
            if job.latest_end:
                visit['maxEndTime'] = job.latest_end.isoformat()

            # Add required skills if any
            if job.skill_ids:
                visit['requiredSkills'] = [skill.code for skill in job.skill_ids]

            # Add priority (1-10 scale, 1 = highest)
            if job.priority:
                visit['priority'] = 10 - int(job.priority) * 3  # Convert 0-3 to 10-1

            visits.append(visit)

        # Build vehicles from inspectors
        vehicles = []
        for inspector in self.inspector_ids:
            # Calculate departure and shift end times from optimization date + shift hours
            opt_date = self.optimization_date
            shift_start = inspector.shift_start or 8.0
            shift_end = inspector.shift_end or 18.0

            shift_start_hours = int(shift_start)
            shift_start_mins = int((shift_start % 1) * 60)
            shift_end_hours = int(shift_end)
            shift_end_mins = int((shift_end % 1) * 60)

            departure_dt = datetime.combine(opt_date, datetime.min.time().replace(
                hour=shift_start_hours, minute=shift_start_mins
            ))
            shift_end_dt = datetime.combine(opt_date, datetime.min.time().replace(
                hour=shift_end_hours, minute=shift_end_mins
            ))

            # Calculate max working minutes from shift duration
            max_working_minutes = int((shift_end - shift_start) * 60)

            vehicle = {
                'id': str(inspector.id),
                'capacity': inspector.vehicle_capacity or 8,  # Default 8 jobs per inspector
                'homeLocation': [
                    inspector.home_latitude or 51.5074,  # Default to London if not set
                    inspector.home_longitude or -0.1278
                ],
                'departureTime': departure_dt.isoformat(),
                'shiftEndTime': shift_end_dt.isoformat(),
                'maxWorkingMinutes': max_working_minutes,
                'visits': [],  # Must be initialized as empty array for Timefold
            }

            # Add skills if any
            if inspector.skill_ids:
                vehicle['skills'] = [skill.code for skill in inspector.skill_ids]

            vehicles.append(vehicle)

        return {
            'name': self.name,
            'vehicles': vehicles,
            'visits': visits,
        }

    def _process_timefold_response(self, result):
        """Process Timefold response and create routes

        Timefold returns:
        {
            "name": "...",
            "score": "-0hard/-12345soft",
            "solverStatus": "NOT_SOLVING",
            "vehicles": [
                {
                    "id": "123",
                    "visits": ["456", "789", ...],  # or full visit objects
                    "totalDrivingTimeSeconds": 3600,
                    ...
                }
            ],
            "visits": [
                {
                    "id": "456",
                    "arrivalTime": "2024-01-15T09:30:00",
                    "departureTime": "2024-01-15T10:00:00",
                    "vehicle": "123",
                    ...
                }
            ]
        }
        """
        self.ensure_one()
        from datetime import datetime

        # Clear existing routes
        self.route_ids.unlink()

        # Build a lookup of visit data for arrival/departure times
        visits_lookup = {}
        for visit in result.get('visits', []):
            visit_id = visit.get('id')
            if visit_id:
                visits_lookup[str(visit_id)] = visit

        # Process each vehicle as a route
        for vehicle_data in result.get('vehicles', []):
            vehicle_id = vehicle_data.get('id')
            if not vehicle_id:
                continue

            inspector_id = int(vehicle_id)

            # Get visits for this vehicle - can be list of IDs or list of objects
            vehicle_visits = vehicle_data.get('visits', [])
            if not vehicle_visits:
                continue  # Skip vehicles with no visits

            # Determine if visits are IDs or objects
            first_visit = vehicle_visits[0]
            if isinstance(first_visit, str):
                visit_ids = vehicle_visits
            elif isinstance(first_visit, dict):
                visit_ids = [v.get('id') for v in vehicle_visits]
            else:
                visit_ids = [str(first_visit)]

            # Create route
            route = self.env['property_fielder.route'].create({
                'name': f'Route for Inspector {inspector_id}',
                'inspector_id': inspector_id,
                'route_date': self.optimization_date,
                'optimization_id': self.id,
                'total_distance_km': vehicle_data.get('totalDistanceMeters', 0) / 1000.0,
                'total_drive_time_minutes': vehicle_data.get('totalDrivingTimeSeconds', 0) / 60,
                'total_work_time_minutes': vehicle_data.get('totalWorkTimeSeconds', 0) / 60,
                'optimization_score': str(result.get('score', 'N/A')),
                'state': 'optimized'
            })

            # Assign jobs to route with scheduled times
            for seq, visit_id in enumerate(visit_ids, start=1):
                try:
                    job = self.env['property_fielder.job'].browse(int(visit_id))
                    if not job.exists():
                        _logger.warning(f"Job {visit_id} not found")
                        continue
                except (ValueError, TypeError):
                    _logger.warning(f"Invalid visit ID: {visit_id}")
                    continue

                # Get visit data from lookup
                visit_data = visits_lookup.get(str(visit_id), {})

                job_data = {
                    'route_id': route.id,
                    'inspector_id': inspector_id,
                    'state': 'assigned',
                    'sequence_in_route': seq,
                }

                # Parse arrival time
                arrival_time = visit_data.get('arrivalTime')
                if arrival_time:
                    try:
                        if isinstance(arrival_time, str):
                            # Handle ISO format with/without timezone
                            arrival_time = arrival_time.replace('Z', '+00:00')
                            if '+' in arrival_time:
                                arrival_time = arrival_time.split('+')[0]
                            job_data['scheduled_arrival_time'] = datetime.fromisoformat(arrival_time)
                    except Exception as e:
                        _logger.warning(f"Could not parse arrival time '{arrival_time}': {e}")

                # Parse departure time
                departure_time = visit_data.get('departureTime')
                if departure_time:
                    try:
                        if isinstance(departure_time, str):
                            departure_time = departure_time.replace('Z', '+00:00')
                            if '+' in departure_time:
                                departure_time = departure_time.split('+')[0]
                            job_data['scheduled_departure_time'] = datetime.fromisoformat(departure_time)
                    except Exception as e:
                        _logger.warning(f"Could not parse departure time '{departure_time}': {e}")

                job.write(job_data)

        _logger.info(f"Processed Timefold response: {len(result.get('vehicles', []))} vehicles, "
                     f"{len(result.get('visits', []))} visits, score={result.get('score')}")

    def _float_to_time(self, float_time):
        """Convert float time (8.5) to time string (08:30)"""
        hours = int(float_time)
        minutes = int((float_time - hours) * 60)
        return f'{hours:02d}:{minutes:02d}'

