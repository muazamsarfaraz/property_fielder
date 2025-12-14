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
            
            // Panel visibility
            panels: {
                resources: true,
                settings: true,
                optimization: true,
                routeDetails: true,
            },

            // Legend visibility
            legendCollapsed: false,

            // Selected items
            selectedJobIds: [],
            selectedInspectorIds: [],
            selectedRouteId: null,

            // Optimization state
            optimizationRunning: false,
            optimizationProgress: 0,
            optimizationStatus: '', // Current status message
            optimizationElapsed: 0, // Elapsed time in seconds
            optimizationEstimate: 0, // Estimated total time in seconds
            optimizationResult: null,
        });

        onWillStart(async () => {
            await this.loadData();
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

    // Data Loading
    async loadData() {
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
        } catch (error) {
            console.error("Failed to load data:", error);
            this.notification.add("Failed to load dispatch data", { type: "danger" });
        } finally {
            this.state.loading = false;
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
        if (!datetimeStr) return '';
        try {
            const date = new Date(datetimeStr);
            return date.toLocaleTimeString('en-GB', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch (e) {
            return '';
        }
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
            this.notification.add("❌ Optimization failed: " + (error.message || error.data?.message || "Unknown error"), { type: "danger" });
        } finally {
            clearInterval(elapsedInterval);
            this.state.optimizationRunning = false;
            console.log("[Optimization] Finished, running = false");
        }
    }

    _sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Public method for template access
    formatTime(seconds) {
        if (seconds < 60) {
            return `${seconds}s`;
        }
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return secs > 0 ? `${mins}m ${secs}s` : `${mins}m`;
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
            this.notification.add(`Error: ${error.message || error}`, { type: "danger" });
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
            this.notification.add(`Error: ${error.message || error}`, { type: "danger" });
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

