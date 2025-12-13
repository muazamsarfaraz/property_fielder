/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { DispatchMapWidget } from "./dispatch_map_widget";
import { DispatchTimelineWidget } from "./dispatch_timeline_widget";

/**
 * Main dispatch view component
 * Combines map and timeline widgets with controls
 */
export class DispatchView extends Component {
    static template = "property_fielder_field_service.DispatchView";
    static components = { DispatchMapWidget, DispatchTimelineWidget };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");

        this.state = useState({
            jobs: [],
            routes: [],
            inspectors: [],
            selectedDate: new Date().toISOString().split('T')[0],
            loading: false,
            viewMode: 'split', // 'split', 'map', 'timeline'
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {
            // Load jobs for selected date
            const jobs = await this.orm.searchRead(
                "property_fielder.job",
                [["scheduled_date", "=", this.state.selectedDate]],
                ["id", "name", "job_number", "partner_id", "street", "city", "latitude", "longitude", 
                 "state", "inspector_id", "route_id", "duration_minutes", "sequence_in_route"]
            );

            // Load routes for selected date
            const routes = await this.orm.searchRead(
                "property_fielder.route",
                [["route_date", "=", this.state.selectedDate]],
                ["id", "name", "route_number", "inspector_id", "job_ids", "state", "start_time"]
            );

            // Load active inspectors
            const inspectors = await this.orm.searchRead(
                "property_fielder.inspector",
                [["active", "=", true]],
                ["id", "name"]
            );

            this.state.jobs = jobs;
            this.state.routes = routes;
            this.state.inspectors = inspectors;

        } catch (error) {
            console.error("Failed to load dispatch data:", error);
            this.notification.add("Failed to load dispatch data", { type: "danger" });
        } finally {
            this.state.loading = false;
        }
    }

    async onDateChange(ev) {
        this.state.selectedDate = ev.target.value;
        await this.loadData();
    }

    async onRefresh() {
        await this.loadData();
        this.notification.add("Data refreshed", { type: "success" });
    }

    async onOptimize() {
        try {
            // Open optimization wizard
            await this.action.doAction({
                type: 'ir.actions.act_window',
                res_model: 'property_fielder.optimization',
                views: [[false, 'form']],
                target: 'new',
                context: {
                    default_optimization_date: this.state.selectedDate,
                }
            });
        } catch (error) {
            console.error("Failed to open optimization wizard:", error);
            this.notification.add("Failed to open optimization wizard", { type: "danger" });
        }
    }

    onJobClick(job) {
        // Open job form view
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property_fielder.job',
            res_id: job.id,
            views: [[false, 'form']],
            target: 'new',
        });
    }

    onRouteClick(route) {
        // Open route form view
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property_fielder.route',
            res_id: route.id,
            views: [[false, 'form']],
            target: 'new',
        });
    }

    setViewMode(mode) {
        this.state.viewMode = mode;
    }

    onGoToProperties() {
        // Navigate to properties list view
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'property_fielder.property',
            name: 'Properties',
            views: [[false, 'list'], [false, 'form']],
            target: 'current',
        });
    }
}

registry.category("actions").add("property_fielder_field_service.dispatch_action", DispatchView);

