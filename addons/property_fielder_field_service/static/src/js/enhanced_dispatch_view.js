/** @odoo-module **/

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { FloatingPanel } from "./floating_panel";
import { DispatchMapWidget } from "./dispatch_map_widget";
import { DispatchTimelineWidget } from "./dispatch_timeline_widget";

/**
 * Enhanced Dispatch View with 3-Tab Layout
 * PLAN → OPTIMIZE → SCHEDULE workflow with persistent map and floating panels
 */
export class EnhancedDispatchView extends Component {
    static template = "property_fielder_field_service.EnhancedDispatchView";
    static components = { FloatingPanel, DispatchMapWidget, DispatchTimelineWidget };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            // Current tab
            activeTab: 'plan', // 'plan', 'optimize', 'schedule'

            // Data
            jobs: [],
            routes: [],
            inspectors: [],
            selectedDate: new Date().toISOString().split('T')[0],
            loading: false,

            // Panel visibility (legacy, kept for compatibility)
            panels: {
                resources: true,
                settings: true,
                optimization: true,
                routeDetails: true,
            },

            // Sidebar state (new docked layout)
            sidebarCollapsed: false,
            settingsExpanded: false,

            // Legend visibility
            legendCollapsed: false,

            // Selected items
            selectedJobIds: [],
            selectedInspectorIds: [],
            selectedRouteId: null,

            // Hover state for map highlighting
            hoveredJobId: null,

            // Search filters
            jobSearchQuery: '',

            // Optimization state
            optimizationRunning: false,
            optimizationProgress: 0,
            optimizationStatus: '', // Current status message
            optimizationElapsed: 0, // Elapsed time in seconds
            optimizationEstimate: 0, // Estimated total time in seconds
            optimizationResult: null,
        });

        onWillStart(async () => {
            await this.loadData(true); // Auto-select date with jobs on initial load
        });

        onMounted(() => {
            this.loadPanelVisibility();
        });
    }

    // Tab Navigation
    setActiveTab(tab) {
        this.state.activeTab = tab;
        this.updatePanelsForTab(tab);
    }

    // Tab click handlers for OWL 2 compatibility
    onSetActiveTabPlan() {
        this.setActiveTab('plan');
    }

    onSetActiveTabOptimize() {
        if (!this.canAccessOptimize()) {
            this.notification.add("Select jobs and inspectors first", { type: "warning" });
            return;
        }
        this.setActiveTab('optimize');
    }

    onSetActiveTabSchedule() {
        if (!this.canAccessSchedule()) {
            this.notification.add("Run optimization first to create routes", { type: "warning" });
            return;
        }
        this.setActiveTab('schedule');
    }

    // Progressive stepper validation
    canAccessOptimize() {
        return this.state.selectedJobIds.length > 0 && this.state.selectedInspectorIds.length > 0;
    }

    canAccessSchedule() {
        // Can access schedule if there are routes OR if optimization has been run
        return this.state.routes.length > 0 || this.state.optimizationResult !== null;
    }

    // Filtered jobs based on search query
    get filteredJobs() {
        const query = (this.state.jobSearchQuery || '').toLowerCase().trim();
        if (!query) return this.state.jobs;

        return this.state.jobs.filter(job => {
            const name = (job.name || job.job_number || '').toLowerCase();
            const address = (job.street || '').toLowerCase();
            const city = (job.city || '').toLowerCase();
            const partner = (job.partner_id?.[1] || '').toLowerCase();

            return name.includes(query) ||
                   address.includes(query) ||
                   city.includes(query) ||
                   partner.includes(query);
        });
    }

    onJobSearchInput(ev) {
        this.state.jobSearchQuery = ev.target.value;
    }

    clearJobSearch() {
        this.state.jobSearchQuery = '';
    }

    // Handle job hover for map highlighting
    onJobHover(jobId) {
        this.state.hoveredJobId = jobId;
    }

    updatePanelsForTab(tab) {
        // Adjust visible panels based on active tab
        if (tab === 'plan') {
            this.state.panels.resources = true;
            this.state.panels.settings = true;
            this.state.panels.optimization = false;
            this.state.panels.routeDetails = false;
        } else if (tab === 'optimize') {
            this.state.panels.resources = false;
            this.state.panels.settings = false;
            this.state.panels.optimization = true;
            this.state.panels.routeDetails = false;
        } else if (tab === 'schedule') {
            this.state.panels.resources = false;
            this.state.panels.settings = false;
            this.state.panels.optimization = false;
            this.state.panels.routeDetails = true;
        }
        this.savePanelVisibility();
    }

    loadPanelVisibility() {
        const saved = localStorage.getItem('dispatch_panel_visibility');
        if (saved) {
            try {
                this.state.panels = { ...this.state.panels, ...JSON.parse(saved) };
            } catch (e) {
                console.warn("Failed to load panel visibility:", e);
            }
        }
    }

    savePanelVisibility() {
        localStorage.setItem('dispatch_panel_visibility', JSON.stringify(this.state.panels));
    }

    togglePanel(panelName) {
        this.state.panels[panelName] = !this.state.panels[panelName];
        this.savePanelVisibility();
    }

    toggleLegend() {
        this.state.legendCollapsed = !this.state.legendCollapsed;
    }

    toggleSidebar() {
        this.state.sidebarCollapsed = !this.state.sidebarCollapsed;
    }

    toggleSettingsSection() {
        this.state.settingsExpanded = !this.state.settingsExpanded;
    }

    // Data Loading
    async loadData(autoSelectDate = false) {
        this.state.loading = true;
        try {
            const [jobs, routes, inspectors] = await Promise.all([
                this.orm.searchRead(
                    "property_fielder.job",
                    [["scheduled_date", "=", this.state.selectedDate]],
                    ["id", "name", "job_number", "partner_id", "street", "city", "latitude", "longitude",
                     "state", "inspector_id", "route_id", "duration_minutes", "sequence_in_route",
                     "priority", "skill_ids", "earliest_start", "latest_end",
                     "scheduled_arrival_time", "scheduled_departure_time"]
                ),
                this.orm.searchRead(
                    "property_fielder.route",
                    [["route_date", "=", this.state.selectedDate]],
                    ["id", "name", "route_number", "inspector_id", "job_ids", "state", "start_time",
                     "total_distance_km", "total_time_minutes", "optimization_score"]
                ),
                this.orm.searchRead(
                    "property_fielder.inspector",
                    [["active", "=", true]],
                    ["id", "name", "user_id", "skill_ids", "active", "available", "home_latitude", "home_longitude",
                     "shift_start", "shift_end"]
                ),
            ]);

            this.state.jobs = jobs;
            this.state.routes = routes;
            this.state.inspectors = inspectors;

            // Auto-select a date with jobs if current date has none
            if (autoSelectDate && jobs.length === 0) {
                await this.findDateWithJobs();
            }
        } catch (error) {
            console.error("Failed to load data:", error);
            this.notification.add(this.formatErrorMessage(error, "Unable to load jobs"), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    /**
     * Find a date with jobs and switch to it
     * Searches within ±14 days of today
     */
    async findDateWithJobs() {
        try {
            // Get dates with jobs in the next 14 days
            const today = new Date();
            const futureDate = new Date();
            futureDate.setDate(today.getDate() + 14);
            const pastDate = new Date();
            pastDate.setDate(today.getDate() - 7);

            const jobsWithDates = await this.orm.searchRead(
                "property_fielder.job",
                [
                    ["scheduled_date", ">=", pastDate.toISOString().split('T')[0]],
                    ["scheduled_date", "<=", futureDate.toISOString().split('T')[0]],
                ],
                ["scheduled_date"],
                { limit: 100 }
            );

            if (jobsWithDates.length > 0) {
                // Count jobs per date and find the date with most jobs
                const dateCounts = {};
                for (const job of jobsWithDates) {
                    const date = job.scheduled_date;
                    dateCounts[date] = (dateCounts[date] || 0) + 1;
                }

                // Find date with most jobs
                let bestDate = null;
                let maxCount = 0;
                for (const [date, count] of Object.entries(dateCounts)) {
                    if (count > maxCount) {
                        maxCount = count;
                        bestDate = date;
                    }
                }

                if (bestDate && bestDate !== this.state.selectedDate) {
                    this.state.selectedDate = bestDate;
                    this.notification.add(`Switched to ${bestDate} (${maxCount} jobs)`, { type: "info" });
                    // Reload data for the new date
                    await this.loadData(false);
                }
            }
        } catch (error) {
            console.warn("Failed to find date with jobs:", error);
        }
    }

    async onDateChange(ev) {
        this.state.selectedDate = ev.target.value;
        await this.loadData();
    }

    async onPrevDay() {
        const date = new Date(this.state.selectedDate);
        date.setDate(date.getDate() - 1);
        this.state.selectedDate = date.toISOString().split('T')[0];
        await this.loadData();
    }

    async onNextDay() {
        const date = new Date(this.state.selectedDate);
        date.setDate(date.getDate() + 1);
        this.state.selectedDate = date.toISOString().split('T')[0];
        await this.loadData();
    }

    async onToday() {
        this.state.selectedDate = new Date().toISOString().split('T')[0];
        await this.loadData();
    }

    async onRefresh() {
        await this.loadData();
        this.notification.add("Data refreshed", { type: "success", sticky: false });
    }

    // Job/Inspector Selection
    toggleJobSelection(jobId) {
        const idx = this.state.selectedJobIds.indexOf(jobId);
        if (idx >= 0) {
            this.state.selectedJobIds.splice(idx, 1);
        } else {
            this.state.selectedJobIds.push(jobId);
        }
    }

    isJobSelected(jobId) {
        return this.state.selectedJobIds.includes(jobId);
    }

    selectAllJobs() {
        console.log("[EnhancedDispatchView] selectAllJobs called, jobs:", this.state.jobs.length);
        this.state.selectedJobIds = this.state.jobs.map(j => j.id);
        console.log("[EnhancedDispatchView] selectedJobIds now:", this.state.selectedJobIds);
    }

    clearJobSelection() {
        this.state.selectedJobIds = [];
    }

    toggleInspectorSelection(inspectorId) {
        const idx = this.state.selectedInspectorIds.indexOf(inspectorId);
        if (idx >= 0) {
            this.state.selectedInspectorIds.splice(idx, 1);
        } else {
            this.state.selectedInspectorIds.push(inspectorId);
        }
    }

    isInspectorSelected(inspectorId) {
        return this.state.selectedInspectorIds.includes(inspectorId);
    }

    selectAllInspectors() {
        this.state.selectedInspectorIds = this.state.inspectors.filter(i => i.available).map(i => i.id);
    }

    clearInspectorSelection() {
        this.state.selectedInspectorIds = [];
    }

    selectRoute(routeId) {
        this.state.selectedRouteId = routeId;
    }

    // Helper to format datetime for display
    formatTime(datetimeStr) {
        if (!datetimeStr) return '--';
        try {
            const date = new Date(datetimeStr);
            if (isNaN(date.getTime())) return '--';
            return date.toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return '--';
        }
    }

    // Helper to format duration in seconds for display
    formatDuration(seconds) {
        if (seconds === null || seconds === undefined || isNaN(seconds)) return '--';
        if (seconds < 60) {
            return `${Math.round(seconds)}s`;
        }
        const mins = Math.floor(seconds / 60);
        const secs = Math.round(seconds % 60);
        return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`;
    }

    // Helper to format distance in km for display
    formatDistance(distanceKm) {
        if (distanceKm === null || distanceKm === undefined || isNaN(distanceKm)) return '--';
        if (distanceKm < 1) {
            return `${Math.round(distanceKm * 1000)}m`;
        }
        return `${distanceKm.toFixed(1)}km`;
    }

    // Helper to format error messages for users
    formatErrorMessage(error, context = '') {
        // Extract the most useful error message
        let message = '';

        if (typeof error === 'string') {
            message = error;
        } else if (error?.data?.message) {
            // Odoo RPC error format
            message = error.data.message;
        } else if (error?.message) {
            message = error.message;
        } else if (error?.data?.arguments?.[0]) {
            // Odoo validation error format
            message = error.data.arguments[0];
        } else {
            message = 'An unexpected error occurred';
        }

        // Clean up technical error messages
        if (message.includes('RPC_ERROR') || message.includes('Traceback')) {
            message = 'Server error - please try again or contact support';
        }

        // Add context if provided
        if (context) {
            return `${context}: ${message}`;
        }
        return message;
    }

    // Optimization
    async startOptimization() {
        console.log("[Optimization] Starting optimization...", {
            selectedJobs: this.state.selectedJobIds,
            selectedInspectors: this.state.selectedInspectorIds,
            date: this.state.selectedDate
        });

        if (this.state.selectedJobIds.length === 0) {
            console.warn("[Optimization] No jobs selected");
            this.notification.add("Please select jobs to optimize", { type: "warning" });
            return;
        }
        if (this.state.selectedInspectorIds.length === 0) {
            console.warn("[Optimization] No inspectors selected");
            this.notification.add("Please select inspectors for routing", { type: "warning" });
            return;
        }

        this.state.optimizationRunning = true;
        this.state.optimizationProgress = 0;
        this.state.optimizationStatus = 'Preparing job data...';
        this.state.optimizationElapsed = 0;
        this.state.optimizationResult = null;

        // Estimate: ~2s per job + ~3s per inspector + 10s base (OSRM + overhead)
        const jobCount = this.state.selectedJobIds.length;
        const inspectorCount = this.state.selectedInspectorIds.length;
        this.state.optimizationEstimate = Math.max(15, 10 + (jobCount * 2) + (inspectorCount * 3));

        console.log("[Optimization] State set to running, estimated time:", this.state.optimizationEstimate, "s");

        // Start elapsed time counter
        const startTime = Date.now();
        const elapsedInterval = setInterval(() => {
            this.state.optimizationElapsed = Math.floor((Date.now() - startTime) / 1000);
        }, 1000);

        try {
            // Step 1: Preparing
            this.state.optimizationProgress = 10;
            this.state.optimizationStatus = `Preparing ${jobCount} jobs and ${inspectorCount} inspectors...`;
            await this._sleep(300); // Brief pause for UI update

            // Step 2: Calculating routes
            this.state.optimizationProgress = 20;
            this.state.optimizationStatus = 'Fetching travel times from OSRM...';
            await this._sleep(200);

            // Step 3: Sending to solver
            this.state.optimizationProgress = 30;
            this.state.optimizationStatus = 'Sending to Timefold solver...';

            console.log("[Optimization] Calling run_optimization with:", {
                job_ids: this.state.selectedJobIds,
                inspector_ids: this.state.selectedInspectorIds,
                optimization_date: this.state.selectedDate,
            });

            // Start progress animation based on estimated time
            const progressInterval = setInterval(() => {
                if (this.state.optimizationProgress < 85) {
                    // Calculate progress based on elapsed vs estimated time
                    const elapsed = this.state.optimizationElapsed;
                    const estimate = this.state.optimizationEstimate;
                    // Progress from 30% to 85% based on time
                    const timeProgress = Math.min(elapsed / estimate, 1);
                    this.state.optimizationProgress = Math.floor(30 + (timeProgress * 55));

                    // Update status message based on progress
                    if (this.state.optimizationProgress < 50) {
                        this.state.optimizationStatus = 'Calculating optimal routes...';
                    } else if (this.state.optimizationProgress < 70) {
                        this.state.optimizationStatus = 'Minimizing travel distance...';
                    } else {
                        this.state.optimizationStatus = 'Finalizing schedules...';
                    }
                }
            }, 500);

            const result = await this.orm.call(
                "property_fielder.optimization",
                "run_optimization",
                [],
                {
                    job_ids: this.state.selectedJobIds,
                    inspector_ids: this.state.selectedInspectorIds,
                    optimization_date: this.state.selectedDate,
                }
            );

            clearInterval(progressInterval);

            console.log("[Optimization] Backend returned:", result);
            this.state.optimizationProgress = 90;
            this.state.optimizationStatus = 'Saving results to database...';
            this.state.optimizationResult = result;

            // Step 4: Reload data
            this.state.optimizationProgress = 95;
            this.state.optimizationStatus = 'Loading updated routes...';
            await this.loadData();

            // Complete
            this.state.optimizationProgress = 100;
            this.state.optimizationStatus = 'Optimization complete!';

            if (result.error_message) {
                this.notification.add("⚠️ Optimization completed with issues: " + result.error_message, { type: "warning" });
            } else {
                this.notification.add(`✅ Optimization complete! ${result.total_routes} routes, ${result.total_jobs_assigned} jobs assigned`, { type: "success" });
            }

            // Switch to schedule tab to view results
            this.setActiveTab('schedule');

        } catch (error) {
            console.error("[Optimization] Failed:", error);
            this.state.optimizationStatus = 'Optimization failed';
            this.notification.add("❌ " + this.formatErrorMessage(error, "Route optimization failed"), { type: "danger" });
        } finally {
            clearInterval(elapsedInterval);
            this.state.optimizationRunning = false;
            console.log("[Optimization] Finished, running = false");
        }
    }

    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Navigation Actions
    onJobClick(job) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property_fielder.job',
            res_id: job.id,
            views: [[false, 'form']],
            target: 'new',
        });
    }

    onRouteClick(route) {
        this.state.selectedRouteId = route.id;
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property_fielder.route',
            res_id: route.id,
            views: [[false, 'form']],
            target: 'new',
        });
    }

    onInspectorClick(inspector) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property_fielder.inspector',
            res_id: inspector.id,
            views: [[false, 'form']],
            target: 'new',
        });
    }

    async onGoToProperties() {
        await this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property_fielder.property',
            name: 'Properties',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }

    // Test Data Management
    async onLoadTestData() {
        const count = 20; // Number of properties to create
        this.state.loading = true;
        this.notification.add(`Creating ${count} test properties, inspections, and jobs...`, { type: "info" });

        try {
            // Call backend method to create test data
            const result = await this.orm.call(
                "property_fielder.job",
                "action_create_test_data",
                [count, this.state.selectedDate]
            );

            if (result.success) {
                this.notification.add(
                    `Created ${result.properties} properties, ${result.inspections} inspections, ${result.jobs} jobs`,
                    { type: "success", sticky: true }
                );
                await this.loadData();
            } else {
                this.notification.add(result.error || "Failed to create test data", { type: "danger" });
            }
        } catch (error) {
            console.error("Failed to create test data:", error);
            this.notification.add(this.formatErrorMessage(error, "Unable to create test data"), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onDeleteTestData() {
        // Show confirmation dialog before deleting
        const confirmed = window.confirm(
            "⚠️ Delete All Test Data?\n\n" +
            "This will permanently delete:\n" +
            "• All properties with 'StressTest' in the name\n" +
            "• Associated inspections and jobs\n" +
            "• Test customer records\n\n" +
            "This action cannot be undone."
        );

        if (!confirmed) {
            return;
        }

        this.state.loading = true;
        this.notification.add("Deleting test data...", { type: "info" });

        try {
            // Call backend method to delete test data
            const result = await this.orm.call(
                "property_fielder.job",
                "action_delete_test_data",
                []
            );

            if (result.success) {
                this.notification.add(
                    `Deleted ${result.routes || 0} routes, ${result.jobs} jobs, ${result.inspections} inspections, ${result.properties} properties`,
                    { type: "success", sticky: true }
                );
                await this.loadData();
            } else {
                this.notification.add(result.error || "Failed to delete test data", { type: "danger" });
            }
        } catch (error) {
            console.error("Failed to delete test data:", error);
            this.notification.add(this.formatErrorMessage(error, "Unable to delete test data"), { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    // Computed properties
    get unassignedJobs() {
        return this.state.jobs.filter(j => !j.route_id);
    }

    get assignedJobs() {
        return this.state.jobs.filter(j => j.route_id);
    }

    get availableInspectors() {
        return this.state.inspectors.filter(i => i.available);
    }

    // Dynamic button text based on selection state
    get optimizeButtonText() {
        const jobCount = this.state.selectedJobIds.length;
        const inspectorCount = this.state.selectedInspectorIds.length;

        if (jobCount === 0) return "Select Jobs to Optimize";
        if (inspectorCount === 0) return "Select Inspectors";

        return `Optimize ${jobCount} Job${jobCount !== 1 ? 's' : ''}`;
    }

    get optimizeButtonDisabled() {
        return this.state.selectedJobIds.length === 0 ||
               this.state.selectedInspectorIds.length === 0 ||
               this.state.optimizationRunning;
    }

    get selectedRoute() {
        if (!this.state.selectedRouteId) return null;
        return this.state.routes.find(r => r.id === this.state.selectedRouteId);
    }

    get routeJobs() {
        if (!this.selectedRoute) return [];
        return this.state.jobs.filter(j => this.selectedRoute.job_ids.includes(j.id))
            .sort((a, b) => (a.sequence_in_route || 0) - (b.sequence_in_route || 0));
    }
}

registry.category("actions").add("property_fielder_field_service.enhanced_dispatch_action", EnhancedDispatchView);


/**
 * Fallback: Add manual event handlers when OWL doesn't mount properly
 * This happens when accessing the page directly via /odoo/action-XXX URL
 * Odoo 19's SSR pre-renders templates but doesn't mount OWL components
 *
 * Uses event delegation for robustness
 */
function initDispatchFallback() {
    const dispatchView = document.querySelector('.o_enhanced_dispatch_view');
    if (!dispatchView) {
        console.log('[DispatchFallback] No dispatch view found');
        return;
    }

    // Check if OWL is mounted
    let owlMounted = false;
    dispatchView.querySelectorAll('*').forEach(el => {
        if (el.__owl__) owlMounted = true;
    });

    if (owlMounted) {
        console.log('[DispatchFallback] OWL is mounted, skipping fallback');
        return;
    }

    console.log('[DispatchFallback] OWL not mounted, adding event delegation');

    // Use event delegation on the dispatch view container
    dispatchView.addEventListener('click', function(e) {
        const target = e.target;
        const button = target.closest('button');

        if (!button) return;

        const buttonText = button.textContent.trim();
        const panelSection = button.closest('.panel-section');

        // Find the heading in this section to determine if it's Jobs or Inspectors
        const heading = panelSection?.querySelector('h6');
        const headingText = heading?.textContent || '';

        console.log('[DispatchFallback] Button clicked:', buttonText, 'in section:', headingText);

        if (buttonText === 'Select All') {
            // Find all checkboxes in this panel section
            const checkboxes = panelSection?.querySelectorAll('input[type="checkbox"]');
            if (checkboxes && checkboxes.length > 0) {
                console.log('[DispatchFallback] Selecting', checkboxes.length, 'checkboxes');
                checkboxes.forEach(cb => {
                    cb.checked = true;
                    const item = cb.closest('.resource-item');
                    if (item) item.classList.add('selected');
                });
            } else {
                console.log('[DispatchFallback] No checkboxes found in section');
            }
        } else if (buttonText === 'Clear') {
            // Find all checkboxes in this panel section
            const checkboxes = panelSection?.querySelectorAll('input[type="checkbox"]');
            if (checkboxes) {
                console.log('[DispatchFallback] Clearing', checkboxes.length, 'checkboxes');
                checkboxes.forEach(cb => {
                    cb.checked = false;
                    const item = cb.closest('.resource-item');
                    if (item) item.classList.remove('selected');
                });
            }
        }
    });

    console.log('[DispatchFallback] Event delegation handler attached');
}

// Run fallback after DOM is ready (with delay to allow Odoo to initialize)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(initDispatchFallback, 1500);
    });
} else {
    // DOM already loaded, run after a delay to let Odoo initialize
    setTimeout(initDispatchFallback, 1500);
}

