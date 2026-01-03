/** @odoo-module **/

import { Component, onMounted, onWillUnmount, onWillUpdateProps, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Mapbox-based dispatch map widget for Property Fielder
 * Displays jobs as markers (with clustering) and routes as polylines
 * Uses Mapbox Light style for cleaner logistics view
 */
export class DispatchMapWidget extends Component {
    static template = "property_fielder_field_service.DispatchMapWidget";
    static props = {
        jobs: { type: Array, optional: true },
        routes: { type: Array, optional: true },
        inspectors: { type: Array, optional: true },
        selectedInspectorIds: { type: Array, optional: true }, // Highlight selected inspectors
        selectedJobIds: { type: Array, optional: true }, // Selected job IDs for visual differentiation
        hoveredJobId: { type: [Number, { value: null }], optional: true }, // Job to highlight on map
        onJobClick: { type: Function, optional: true },
        onJobHover: { type: Function, optional: true }, // Callback when hovering a job pin on map
        onRouteClick: { type: Function, optional: true },
        dataVersion: { type: String, optional: true }, // Used to trigger re-render on data changes
    };

    setup() {
        this.mapContainer = useRef("mapContainer");
        this.orm = useService("orm");
        this.notification = useService("notification");

        this.map = null;
        this.markers = [];
        this.inspectorMarkers = []; // Inspector home location markers
        this.routeLayers = [];
        this.mapboxToken = null;
        this.clusterSourceId = 'job-clusters';
        this.mapLoaded = false;
        this.spiderMarkers = []; // Spiderfy cluster markers
        this.spiderLines = []; // Spider leg lines

        onMounted(() => this.initMap());
        onWillUnmount(() => this.destroyMap());

        // Re-render when props change (jobs/routes updated)
        // Using onWillUpdateProps for reliable prop change detection
        onWillUpdateProps((nextProps) => {
            if (this.mapLoaded) {
                // Check if data actually changed by comparing versions or counts
                const currentVersion = this.props.dataVersion || '';
                const nextVersion = nextProps.dataVersion || '';
                const jobsChanged = (this.props.jobs?.length || 0) !== (nextProps.jobs?.length || 0);
                const routesChanged = (this.props.routes?.length || 0) !== (nextProps.routes?.length || 0);
                const inspectorsChanged = JSON.stringify(this.props.selectedInspectorIds || []) !==
                                          JSON.stringify(nextProps.selectedInspectorIds || []);
                const hoveredJobChanged = this.props.hoveredJobId !== nextProps.hoveredJobId;

                if (currentVersion !== nextVersion || jobsChanged || routesChanged) {
                    console.log('[MapWidget] Data changed, re-rendering...', {
                        currentVersion, nextVersion, jobsChanged, routesChanged
                    });
                    // Schedule re-render after props are applied
                    setTimeout(() => {
                        this.renderJobs();
                        this.renderRoutes();
                        this.renderInspectorMarkers();
                    }, 50);
                } else if (inspectorsChanged) {
                    // Only inspector selection changed
                    setTimeout(() => this.renderInspectorMarkers(), 50);
                } else if (hoveredJobChanged) {
                    // Only hovered job changed - highlight marker
                    setTimeout(() => this.highlightJobMarker(nextProps.hoveredJobId), 10);
                }
            }
        });
    }

    // Highlight a specific job marker on the map
    highlightJobMarker(jobId) {
        // Reset all markers to normal state
        this.markers.forEach(marker => {
            const el = marker.getElement();
            if (el) {
                el.classList.remove('highlighted');
                el.style.zIndex = '1';
            }
        });

        // If a job is hovered, highlight it
        if (jobId) {
            const marker = this.markers.find(m => m._jobId === jobId);
            if (marker) {
                const el = marker.getElement();
                if (el) {
                    el.classList.add('highlighted');
                    el.style.zIndex = '100';
                }
            }
        }
    }

    async initMap() {
        try {
            // Get Mapbox token from Odoo config via ORM call
            const config = await this.orm.call(
                "ir.config_parameter",
                "get_param",
                ["property_fielder.mapbox.token", "pk.eyJ1IjoibXVhemFtc2FyZmFyYXoiLCJhIjoiY205b2dzdnVlMTVuZDJqczcwbnBseW1tYiJ9.-MvfX63GtzUQceap1g6iJQ"]
            );
            this.mapboxToken = config || "pk.eyJ1IjoibXVhemFtc2FyZmFyYXoiLCJhIjoiY205b2dzdnVlMTVuZDJqczcwbnBseW1tYiJ9.-MvfX63GtzUQceap1g6iJQ";

            // Initialize Mapbox GL JS
            mapboxgl.accessToken = this.mapboxToken;

            // Use Mapbox Streets style for better contrast and road visibility
            this.map = new mapboxgl.Map({
                container: this.mapContainer.el,
                style: 'mapbox://styles/mapbox/streets-v12',
                center: [-0.1278, 51.5074], // London default (UK focus)
                zoom: 11,
                attributionControl: true
            });

            // Add navigation controls
            this.map.addControl(new mapboxgl.NavigationControl(), 'bottom-right');
            this.map.addControl(new mapboxgl.FullscreenControl(), 'bottom-right');

            // Wait for map to load
            this.map.on('load', () => {
                this.mapLoaded = true;
                this.setupClusterSource();
                this.renderJobs();
                this.renderRoutes();
                this.renderInspectorMarkers();
                this.setupPopupClickHandler();
            });

        } catch (error) {
            console.error("Failed to initialize map:", error);
            this.notification.add("Failed to initialize map", { type: "danger" });
        }
    }

    /**
     * Setup click handler for popup "Add to Route" buttons
     * Uses event delegation on the map container
     */
    setupPopupClickHandler() {
        // Use event delegation on the map container to catch popup button clicks
        this.mapContainer.el.addEventListener('click', (e) => {
            const btn = e.target.closest('.job-popup-select-btn');
            if (btn && this.props.onJobClick) {
                const jobId = parseInt(btn.dataset.jobId, 10);
                const job = (this.props.jobs || []).find(j => j.id === jobId);
                if (job) {
                    this.props.onJobClick(job);
                    // Close the popup after selection
                    this.markers.forEach(marker => {
                        if (marker._jobId === jobId && marker.getPopup()) {
                            marker.getPopup().remove();
                        }
                    });
                }
            }
        });
    }

    setupClusterSource() {
        // Add a clustered GeoJSON source for jobs
        this.map.addSource(this.clusterSourceId, {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: [] },
            cluster: true,
            clusterMaxZoom: 14,
            clusterRadius: 50
        });

        // Cluster circle layer - Using Orange/Red gradient (distinct from job status colors)
        this.map.addLayer({
            id: 'clusters',
            type: 'circle',
            source: this.clusterSourceId,
            filter: ['has', 'point_count'],
            paint: {
                'circle-color': [
                    'step',
                    ['get', 'point_count'],
                    '#FF9500',  // < 10 jobs - Orange
                    10, '#FF6B00',  // 10-30 jobs - Dark Orange
                    30, '#DC3545'   // 30+ jobs - Red (high density warning)
                ],
                'circle-radius': [
                    'step',
                    ['get', 'point_count'],
                    20,   // < 10 jobs
                    10, 30,  // 10-30 jobs
                    30, 40   // 30+ jobs
                ],
                'circle-stroke-width': 3,
                'circle-stroke-color': '#fff'
            }
        });

        // Cluster count text layer
        this.map.addLayer({
            id: 'cluster-count',
            type: 'symbol',
            source: this.clusterSourceId,
            filter: ['has', 'point_count'],
            layout: {
                'text-field': '{point_count_abbreviated}',
                'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
                'text-size': 14
            },
            paint: {
                'text-color': '#fff'
            }
        });

        // Click on cluster - Spiderfy if at max zoom, otherwise zoom in
        // Gemini UX Recommendation: Implement spiderfy for overlapping pins
        this.map.on('click', 'clusters', (e) => {
            const features = this.map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
            if (!features.length) return;

            const clusterId = features[0].properties.cluster_id;
            const clusterCenter = features[0].geometry.coordinates;
            const pointCount = features[0].properties.point_count;
            const currentZoom = this.map.getZoom();

            // Get expansion zoom to see if we can zoom in more
            this.map.getSource(this.clusterSourceId).getClusterExpansionZoom(
                clusterId,
                (err, expansionZoom) => {
                    if (err) return;

                    // If we're already near max zoom or expansion zoom, use spiderfy
                    if (currentZoom >= 14 || expansionZoom >= 15 || pointCount <= 10) {
                        this.spiderfyCluster(clusterId, clusterCenter, pointCount);
                    } else {
                        // Otherwise zoom in normally
                        this.map.easeTo({
                            center: clusterCenter,
                            zoom: expansionZoom
                        });
                    }
                }
            );
        });

        // Change cursor on cluster hover
        this.map.on('mouseenter', 'clusters', () => {
            this.map.getCanvas().style.cursor = 'pointer';
        });
        this.map.on('mouseleave', 'clusters', () => {
            this.map.getCanvas().style.cursor = '';
        });

        // Click on map (not cluster/marker) to close spiderfy
        this.map.on('click', (e) => {
            // Check if click was on a cluster or marker
            const features = this.map.queryRenderedFeatures(e.point, { layers: ['clusters'] });
            if (features.length === 0 && !e.originalEvent.target.closest('.mapboxgl-marker')) {
                this.clearSpiderfy();
            }
        });
    }

    /**
     * Spiderfy a cluster - spread its points in a circle pattern
     * @param {number} clusterId - The cluster ID
     * @param {Array} center - [lng, lat] of cluster center
     * @param {number} pointCount - Number of points in cluster
     */
    spiderfyCluster(clusterId, center, pointCount) {
        // Clear any existing spiderfy
        this.clearSpiderfy();

        // Get the leaves (individual points) of this cluster
        this.map.getSource(this.clusterSourceId).getClusterLeaves(
            clusterId,
            pointCount,
            0,
            (err, leaves) => {
                if (err || !leaves) return;

                this.spiderMarkers = [];
                this.spiderLines = [];

                // Calculate spider leg positions in a circle
                const radius = 50; // pixels
                const angleStep = (2 * Math.PI) / leaves.length;

                leaves.forEach((leaf, i) => {
                    const angle = angleStep * i - Math.PI / 2; // Start from top
                    const offsetX = Math.cos(angle) * radius;
                    const offsetY = Math.sin(angle) * radius;

                    // Get the job data
                    const jobId = leaf.properties.id;
                    const jobState = leaf.properties.state || 'draft';
                    const jobName = leaf.properties.name || '';

                    // Get status color - GEMINI UX FIX: Reduce alarm fatigue
                    // Blue/grey for standard unassigned, Red ONLY for urgent
                    const statusColors = {
                        'draft': '#3B82F6',       // Blue - standard unassigned (NOT red)
                        'pending': '#F97316',     // Orange - pending action
                        'scheduled': '#10B981',   // Green - scheduled/confirmed
                        'assigned': '#8B5CF6',    // Purple - assigned to inspector
                        'in_progress': '#0EA5E9', // Sky blue - actively being worked
                        'completed': '#22C55E',   // Green - done
                        'cancelled': '#6B7280',   // Grey - cancelled
                    };
                    const color = statusColors[jobState] || '#3B82F6'; // Default to blue

                    // Create spider pin element
                    const el = document.createElement('div');
                    el.className = 'job-pin-marker spider-marker';
                    el.innerHTML = `
                        <div class="job-pin spider-pin"
                             data-status="${jobState}"
                             style="background: ${color}; width: 24px; height: 24px;">
                            <span class="job-pin-icon">●</span>
                        </div>
                    `;
                    el.title = jobName;

                    // Create marker at offset position (using pixel offset)
                    const marker = new mapboxgl.Marker({
                        element: el,
                        offset: [offsetX, offsetY],
                        anchor: 'center'
                    })
                    .setLngLat(center)
                    .addTo(this.map);

                    // Add click handler
                    el.addEventListener('click', (e) => {
                        e.stopPropagation();
                        if (this.props.onJobClick) {
                            const job = this.props.jobs.find(j => j.id === jobId);
                            if (job) this.props.onJobClick(job);
                        }
                    });

                    this.spiderMarkers.push(marker);
                });

                // Add a center marker to close the spider
                const centerEl = document.createElement('div');
                centerEl.className = 'job-pin-marker spider-center-marker';
                centerEl.innerHTML = `
                    <div class="job-pin spider-center" title="Click to close">
                        <span class="job-pin-icon">×</span>
                    </div>
                `;
                centerEl.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.clearSpiderfy();
                });

                const centerMarker = new mapboxgl.Marker({
                    element: centerEl,
                    anchor: 'center'
                })
                .setLngLat(center)
                .addTo(this.map);

                this.spiderMarkers.push(centerMarker);
            }
        );
    }

    /**
     * Clear any existing spiderfy markers
     */
    clearSpiderfy() {
        if (this.spiderMarkers) {
            this.spiderMarkers.forEach(m => m.remove());
            this.spiderMarkers = [];
        }
        if (this.spiderLines) {
            this.spiderLines.forEach(l => l.remove());
            this.spiderLines = [];
        }
    }

    destroyMap() {
        this.clearSpiderfy(); // Clear any spider markers first
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
    }

    renderJobs() {
        if (!this.map) return;

        // Clear existing markers FIRST (even if no jobs)
        this.markers.forEach(marker => marker.remove());
        this.markers = [];

        // Clear cluster source data
        const source = this.map.getSource(this.clusterSourceId);
        if (source) {
            source.setData({ type: 'FeatureCollection', features: [] });
        }

        // If no jobs, we're done (map is now clear)
        if (!this.props.jobs || this.props.jobs.length === 0) return;

        // Build GeoJSON features for clustering
        const features = [];
        let jobIndex = 0;

        // Get selected job IDs for visual differentiation
        const selectedJobIds = this.props.selectedJobIds || [];

        // Add job markers with proper pin styling
        this.props.jobs.forEach(job => {
            if (!job.latitude || !job.longitude) return;

            jobIndex++;
            const isSelected = selectedJobIds.includes(job.id);
            const hasRoute = job.sequence_in_route && job.sequence_in_route > 0;

            // Color logic: Status-based colors with priority override
            // Urgent (high priority) jobs get RED, others get neutral colors
            const color = this.getJobColor(job.state, job.priority);

            // Only show sequence number if job has been routed
            const displayContent = hasRoute
                ? `<span class="job-pin-number">${job.sequence_in_route}</span>`
                : `<span class="job-pin-icon">●</span>`;

            // Add to cluster features
            features.push({
                type: 'Feature',
                properties: {
                    id: job.id,
                    name: job.name || job.job_number,
                    state: job.state,
                    sequence: hasRoute ? job.sequence_in_route : jobIndex
                },
                geometry: {
                    type: 'Point',
                    coordinates: [job.longitude, job.latitude]
                }
            });

            // Create custom pin marker element - simple circle centered on coordinate
            const el = document.createElement('div');
            el.className = `job-pin-marker ${isSelected ? 'selected' : ''} ${hasRoute ? 'routed' : ''}`;
            el.innerHTML = `
                <div class="job-pin" data-status="${job.state}" data-selected="${isSelected}" style="--pin-color: ${color};">
                    ${displayContent}
                </div>
            `;

            // Use 'center' anchor so the circle center is exactly on the geo-coordinate
            const marker = new mapboxgl.Marker({ element: el, anchor: 'center' })
                .setLngLat([job.longitude, job.latitude])
                .setPopup(new mapboxgl.Popup({ offset: 25 }).setHTML(this.getJobPopupHTML(job)))
                .addTo(this.map);

            // Store job ID on marker for hover highlighting
            marker._jobId = job.id;

            if (this.props.onJobClick) {
                el.addEventListener('click', () => this.props.onJobClick(job));
            }

            // Bidirectional highlighting: hovering map pin highlights list item
            if (this.props.onJobHover) {
                el.addEventListener('mouseenter', () => this.props.onJobHover(job.id));
                el.addEventListener('mouseleave', () => this.props.onJobHover(null));
            }

            this.markers.push(marker);
        });

        // Update cluster source with job features
        if (this.map.getSource(this.clusterSourceId)) {
            this.map.getSource(this.clusterSourceId).setData({
                type: 'FeatureCollection',
                features: features
            });
        }

        // Fit bounds to show all markers with animation
        if (this.markers.length > 0) {
            const bounds = new mapboxgl.LngLatBounds();
            this.markers.forEach(marker => bounds.extend(marker.getLngLat()));
            this.map.fitBounds(bounds, {
                padding: { top: 100, bottom: 100, left: 350, right: 100 }, // Extra left padding for side panel
                maxZoom: 15,
                duration: 1000 // Smooth animation
            });
        }
    }

    async renderRoutes() {
        if (!this.map) return;

        // Clear existing route layers FIRST (even if no routes)
        this.routeLayers.forEach(layerId => {
            if (this.map.getLayer(layerId)) this.map.removeLayer(layerId);
            if (this.map.getSource(layerId)) this.map.removeSource(layerId);
        });
        this.routeLayers = [];

        // If no routes, we're done (map is now clear)
        if (!this.props.routes || this.props.routes.length === 0) return;

        // OSRM server URL
        const osrmUrl = 'https://osrmproj-production.up.railway.app';

        // Add route polylines - fetch real road geometry from OSRM
        for (let index = 0; index < this.props.routes.length; index++) {
            const route = this.props.routes[index];
            if (!route.job_ids || route.job_ids.length === 0) continue;

            const layerId = `route-${route.id}`;

            // Get inspector home location as start/end point
            const inspector = this.props.inspectors?.find(i =>
                route.inspector_id && i.id === route.inspector_id[0]
            );
            const homeLat = inspector?.home_latitude || 51.5074;
            const homeLng = inspector?.home_longitude || -0.1278;

            // Get jobs in sequence order
            const jobs = this.props.jobs?.filter(j => route.job_ids.includes(j.id)) || [];
            jobs.sort((a, b) => (a.sequence_in_route || 0) - (b.sequence_in_route || 0));

            // Build waypoints: home -> jobs -> home
            const waypoints = [[homeLng, homeLat]];
            jobs.forEach(job => {
                if (job.latitude && job.longitude) {
                    waypoints.push([job.longitude, job.latitude]);
                }
            });
            waypoints.push([homeLng, homeLat]); // Return to home

            if (waypoints.length < 2) continue;

            let routeGeometry = null;

            try {
                // Build OSRM coordinates string: lng,lat;lng,lat;...
                const coordsStr = waypoints.map(c => `${c[0]},${c[1]}`).join(';');
                const osrmRequestUrl = `${osrmUrl}/route/v1/driving/${coordsStr}?overview=full&geometries=geojson`;

                const response = await fetch(osrmRequestUrl);
                if (response.ok) {
                    const data = await response.json();
                    if (data.code === 'Ok' && data.routes && data.routes[0]?.geometry) {
                        routeGeometry = data.routes[0].geometry;
                        console.log(`[Route ${route.id}] OSRM returned ${routeGeometry.coordinates.length} points`);
                    }
                }
            } catch (error) {
                console.warn(`[Route ${route.id}] OSRM failed, using straight lines:`, error.message);
            }

            // Fallback to straight lines if OSRM failed
            if (!routeGeometry) {
                routeGeometry = {
                    type: 'LineString',
                    coordinates: waypoints
                };
            }

            this.map.addSource(layerId, {
                type: 'geojson',
                data: {
                    type: 'Feature',
                    properties: { route_id: route.id },
                    geometry: routeGeometry
                }
            });

            this.map.addLayer({
                id: layerId,
                type: 'line',
                source: layerId,
                layout: {
                    'line-join': 'round',
                    'line-cap': 'round'
                },
                paint: {
                    'line-color': this.getRouteColor(index),
                    'line-width': 4,
                    'line-opacity': 0.85
                }
            });

            this.routeLayers.push(layerId);
        }
    }

    getRouteCoordinates(route) {
        // Get coordinates from jobs in the route (used as fallback)
        const jobs = this.props.jobs?.filter(j => route.job_ids.includes(j.id)) || [];
        return jobs
            .filter(j => j.latitude && j.longitude)
            .map(j => [j.longitude, j.latitude]);
    }

    getJobColor(state, priority = null) {
        // GEMINI UX FIX: Reduce "alarm fatigue"
        // Use neutral Blue/Grey for standard unassigned jobs
        // Red ONLY for urgent jobs (high priority)
        // Green for scheduled/confirmed jobs
        const colors = {
            'draft': '#3B82F6',       // Blue - standard unassigned (NOT red!)
            'pending': '#F97316',     // Orange - pending action
            'scheduled': '#10B981',   // Green - scheduled/confirmed
            'assigned': '#8B5CF6',    // Purple - assigned to inspector
            'in_progress': '#0EA5E9', // Sky blue - actively being worked
            'completed': '#22C55E',   // Green - done
            'cancelled': '#6B7280'    // Grey - cancelled
        };

        // Override: High priority/urgent jobs get RED regardless of state
        if (priority === '2' || priority === 2 || priority === 'urgent') {
            return '#EF4444'; // Red - truly urgent
        }

        return colors[state] || '#3B82F6'; // Default to blue (not red)
    }

    getRouteColor(index) {
        const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c'];
        return colors[index % colors.length];
    }

    getJobPopupHTML(job) {
        // Format the deadline (latest_end)
        let deadlineStr = 'Not set';
        if (job.latest_end) {
            const deadline = new Date(job.latest_end);
            deadlineStr = deadline.toLocaleString('en-GB', {
                day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
            });
        }

        // Format the scheduled arrival and departure times (set by optimizer)
        let scheduledTimeStr = '';
        if (job.scheduled_arrival_time) {
            const arrival = new Date(job.scheduled_arrival_time);
            const arrivalTimeStr = arrival.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });

            let departureTimeStr = '';
            if (job.scheduled_departure_time) {
                const departure = new Date(job.scheduled_departure_time);
                departureTimeStr = ` - ${departure.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}`;
            }

            scheduledTimeStr = `${arrivalTimeStr}${departureTimeStr}`;
        }

        // Format duration
        const durationMinutes = job.duration_minutes || 60;
        let durationStr;
        if (durationMinutes >= 60) {
            const hours = Math.floor(durationMinutes / 60);
            const mins = durationMinutes % 60;
            durationStr = mins > 0 ? `${hours}h ${mins}m` : `${hours}h`;
        } else {
            durationStr = `${durationMinutes}m`;
        }

        // Extract property name for compact display
        let propertyName = job.name || job.job_number;
        const dashIdx = propertyName.lastIndexOf(' - ');
        if (dashIdx > 0) {
            propertyName = propertyName.substring(dashIdx + 3).trim();
        }

        // Check if job is selected
        const selectedJobIds = this.props.selectedJobIds || [];
        const isSelected = selectedJobIds.includes(job.id);
        const buttonText = isSelected ? 'Remove from Route' : 'Add to Route';
        const buttonIcon = isSelected ? 'fa-times' : 'fa-check-square-o';
        const buttonClass = isSelected ? 'btn-outline-danger' : 'btn-primary';

        // Build navigation URL (Google Maps for click-to-navigate)
        const navUrl = job.latitude && job.longitude
            ? `https://www.google.com/maps/dir/?api=1&destination=${job.latitude},${job.longitude}`
            : null;

        return `
            <div class="job-popup-content" data-job-id="${job.id}">
                <div class="job-popup-header">
                    <h6>${propertyName}</h6>
                    <span class="job-popup-status" style="background: ${this.getJobColor(job.state, job.priority)};">${job.state}</span>
                </div>
                <div class="job-popup-body">
                    <div class="job-popup-row"><i class="fa fa-user"></i> ${job.partner_id?.[1] || 'N/A'}</div>
                    <div class="job-popup-row"><i class="fa fa-map-marker"></i> ${job.street || ''}, ${job.city || ''}</div>
                    <div class="job-popup-row"><i class="fa fa-clock-o"></i> Due: ${deadlineStr}</div>
                    ${scheduledTimeStr ? `<div class="job-popup-row job-popup-scheduled"><i class="fa fa-calendar-check-o"></i> ${scheduledTimeStr}</div>` : ''}
                    <div class="job-popup-row"><i class="fa fa-hourglass-half"></i> ${durationStr}</div>
                    ${job.inspector_id ? `<div class="job-popup-row"><i class="fa fa-id-badge"></i> ${job.inspector_id[1]}</div>` : ''}
                </div>
                <div class="d-flex gap-1 mt-2">
                    <button class="btn btn-sm ${buttonClass} flex-grow-1 job-popup-select-btn" data-job-id="${job.id}">
                        <i class="fa ${buttonIcon}"></i> ${buttonText}
                    </button>
                    ${navUrl ? `<a href="${navUrl}" target="_blank" class="btn btn-sm btn-outline-secondary" title="Navigate (Google Maps)">
                        <i class="fa fa-external-link"></i>
                    </a>` : ''}
                </div>
            </div>
        `;
    }

    /**
     * Render inspector home location markers for selected inspectors
     */
    renderInspectorMarkers() {
        // Clear existing inspector markers
        for (const marker of this.inspectorMarkers) {
            marker.remove();
        }
        this.inspectorMarkers = [];

        const inspectors = this.props.inspectors || [];
        const selectedIds = this.props.selectedInspectorIds || [];

        // Only show markers for selected inspectors
        const selectedInspectors = inspectors.filter(i => selectedIds.includes(i.id));

        for (const inspector of selectedInspectors) {
            if (!inspector.home_latitude || !inspector.home_longitude) continue;

            // Get initials from inspector name (e.g., "John Smith" -> "JS")
            const nameParts = (inspector.name || 'U').split(' ');
            const initials = nameParts.length >= 2
                ? (nameParts[0][0] + nameParts[nameParts.length - 1][0]).toUpperCase()
                : nameParts[0].substring(0, 2).toUpperCase();

            // Create a custom marker element for inspector home with avatar
            const el = document.createElement('div');
            el.className = 'inspector-home-marker';
            el.innerHTML = `
                <div class="inspector-avatar">
                    <span class="inspector-initials">${initials}</span>
                </div>
                <div class="inspector-marker-label">${inspector.name.split(' ')[0]}</div>
            `;

            // Create popup
            const popup = new mapboxgl.Popup({ offset: 25 })
                .setHTML(`
                    <div style="min-width: 150px;">
                        <h6 style="margin: 0 0 8px 0; font-weight: 600;">
                            <i class="fa fa-user-tie" style="color: #714B67;"></i> ${inspector.name}
                        </h6>
                        <p style="margin: 4px 0; font-size: 13px;"><strong>Home Base</strong></p>
                        ${inspector.shift_start ? `<p style="margin: 4px 0; font-size: 13px;"><strong>Shift:</strong> ${inspector.shift_start} - ${inspector.shift_end || 'N/A'}</p>` : ''}
                    </div>
                `);

            // Create marker
            const marker = new mapboxgl.Marker(el)
                .setLngLat([inspector.home_longitude, inspector.home_latitude])
                .setPopup(popup)
                .addTo(this.map);

            this.inspectorMarkers.push(marker);
        }
    }
}

// Export the component for use in dispatch views
// Note: This is a standalone OWL component, NOT a form field widget
// It is imported directly by enhanced_dispatch_view.js and dispatch_view.js

