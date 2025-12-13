/** @odoo-module **/

import { Component, onMounted, onWillUnmount, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Vis-Timeline based dispatch timeline widget for Property Fielder
 * Displays inspector schedules with jobs, travel time, and standby time
 */
export class DispatchTimelineWidget extends Component {
    static template = "property_fielder_field_service.DispatchTimelineWidget";
    static props = {
        routes: { type: Array, optional: true },
        inspectors: { type: Array, optional: true },
        jobs: { type: Array, optional: true },
        date: { type: String, optional: true },
        onJobClick: { type: Function, optional: true },
    };

    setup() {
        this.timelineContainer = useRef("timelineContainer");
        this.notification = useService("notification");

        this.timeline = null;

        onMounted(() => this.initTimeline());
        onWillUnmount(() => this.destroyTimeline());
    }

    initTimeline() {
        try {
            const container = this.timelineContainer.el;
            
            // Prepare timeline data
            const items = this.prepareTimelineItems();
            const groups = this.prepareTimelineGroups();

            // Timeline options
            const options = {
                width: '100%',
                height: '400px',
                stack: false,
                showCurrentTime: true,
                zoomMin: 1000 * 60 * 60, // 1 hour
                zoomMax: 1000 * 60 * 60 * 24, // 24 hours
                editable: false,
                margin: {
                    item: 10,
                    axis: 5
                },
                orientation: 'top',
                groupOrder: 'content'
            };

            // Create timeline
            this.timeline = new vis.Timeline(container, items, groups, options);

            // Add click handler
            if (this.props.onJobClick) {
                this.timeline.on('select', (properties) => {
                    if (properties.items.length > 0) {
                        const itemId = properties.items[0];
                        const item = items.get(itemId);
                        if (item && item.jobId) {
                            const job = this.props.jobs?.find(j => j.id === item.jobId);
                            if (job) this.props.onJobClick(job);
                        }
                    }
                });
            }

        } catch (error) {
            console.error("Failed to initialize timeline:", error);
            this.notification.add("Failed to initialize timeline", { type: "danger" });
        }
    }

    destroyTimeline() {
        if (this.timeline) {
            this.timeline.destroy();
            this.timeline = null;
        }
    }

    prepareTimelineGroups() {
        const groups = new vis.DataSet();
        
        if (this.props.inspectors) {
            this.props.inspectors.forEach(inspector => {
                groups.add({
                    id: inspector.id,
                    content: inspector.name,
                    value: inspector.id
                });
            });
        }

        return groups;
    }

    prepareTimelineItems() {
        const items = new vis.DataSet();
        const date = this.props.date || new Date().toISOString().split('T')[0];

        if (!this.props.routes) return items;

        this.props.routes.forEach(route => {
            if (!route.inspector_id || !route.job_ids) return;

            const inspectorId = route.inspector_id[0];
            const jobs = this.props.jobs?.filter(j => route.job_ids.includes(j.id)) || [];

            // Sort jobs by scheduled arrival time (from optimizer), fall back to sequence
            jobs.sort((a, b) => {
                if (a.scheduled_arrival_time && b.scheduled_arrival_time) {
                    return new Date(a.scheduled_arrival_time) - new Date(b.scheduled_arrival_time);
                }
                return (a.sequence_in_route || 0) - (b.sequence_in_route || 0);
            });

            let lastJobEnd = null;

            jobs.forEach((job, index) => {
                // Use actual scheduled times from optimizer if available
                let jobStart, jobEnd;
                const jobDuration = job.duration_minutes || 60;

                if (job.scheduled_arrival_time) {
                    // Use actual optimized times
                    jobStart = new Date(job.scheduled_arrival_time);
                    if (job.scheduled_departure_time) {
                        jobEnd = new Date(job.scheduled_departure_time);
                    } else {
                        jobEnd = new Date(jobStart.getTime() + jobDuration * 60000);
                    }
                } else {
                    // Fallback: calculate from route start time
                    const routeStart = new Date(`${date}T${route.start_time || '08:00:00'}`);
                    if (lastJobEnd) {
                        jobStart = new Date(lastJobEnd.getTime() + 15 * 60000); // 15 min travel
                    } else {
                        jobStart = routeStart;
                    }
                    jobEnd = new Date(jobStart.getTime() + jobDuration * 60000);
                }

                // Add travel time item (if not first job and we have accurate times)
                if (index > 0 && lastJobEnd) {
                    const travelStart = lastJobEnd;
                    const travelEnd = jobStart;
                    const travelMinutes = Math.round((travelEnd - travelStart) / 60000);

                    if (travelMinutes > 0) {
                        items.add({
                            id: `travel-${route.id}-${index}`,
                            group: inspectorId,
                            start: travelStart,
                            end: travelEnd,
                            content: `🚗 ${travelMinutes} min`,
                            className: 'timeline-travel',
                            style: 'background-color: #95a5a6; border-color: #7f8c8d;'
                        });
                    }
                }

                // Format job content with time
                const timeStr = jobStart.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
                const jobContent = `${timeStr} - ${job.name || job.job_number}`;

                // Add job item
                items.add({
                    id: `job-${job.id}`,
                    group: inspectorId,
                    start: jobStart,
                    end: jobEnd,
                    content: jobContent,
                    jobId: job.id,
                    className: `timeline-job timeline-job-${job.state}`,
                    style: `background-color: ${this.getJobColor(job.state)}; border-color: ${this.getJobBorderColor(job.state)};`
                });

                lastJobEnd = jobEnd;
            });
        });

        return items;
    }

    getJobColor(state) {
        const colors = {
            'draft': '#ecf0f1',
            'scheduled': '#d1ecf1',
            'assigned': '#fff3cd',
            'in_progress': '#cce5ff',
            'completed': '#d4edda',
            'cancelled': '#f8d7da'
        };
        return colors[state] || '#ecf0f1';
    }

    getJobBorderColor(state) {
        const colors = {
            'draft': '#95a5a6',
            'scheduled': '#17a2b8',
            'assigned': '#ffc107',
            'in_progress': '#007bff',
            'completed': '#28a745',
            'cancelled': '#dc3545'
        };
        return colors[state] || '#95a5a6';
    }
}

registry.category("fields").add("dispatch_timeline", DispatchTimelineWidget);

