/** @odoo-module **/

import { Component, onMounted, onWillUnmount, onWillUpdateProps, useRef, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

/**
 * Property Map Widget - Displays a single property's location on an interactive Mapbox map
 * Shows the property marker with address popup
 */
export class PropertyMapWidget extends Component {
    static template = "property_fielder_property_management.PropertyMapWidget";
    static props = {
        ...standardFieldProps,
    };

    setup() {
        this.mapContainer = useRef("mapContainer");
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        this.map = null;
        this.marker = null;
        this.mapboxToken = null;
        this.mapLoaded = false;

        this.state = useState({
            loading: true,
            error: null,
        });

        onMounted(() => this.initMap());
        onWillUnmount(() => this.destroyMap());
        
        // Re-render when coordinates change
        onWillUpdateProps((nextProps) => {
            if (this.mapLoaded && this.map) {
                const record = nextProps.record?.data || {};
                const lat = record.latitude;
                const lng = record.longitude;
                if (lat && lng) {
                    this.updateMarker(lat, lng, record);
                }
            }
        });
    }

    get latitude() {
        return this.props.record?.data?.latitude || 0;
    }

    get longitude() {
        return this.props.record?.data?.longitude || 0;
    }

    get hasCoordinates() {
        return this.latitude !== 0 && this.longitude !== 0;
    }

    get propertyData() {
        return this.props.record?.data || {};
    }

    async initMap() {
        if (!this.hasCoordinates) {
            this.state.loading = false;
            this.state.error = "No GPS coordinates available";
            return;
        }

        try {
            // Get Mapbox token from Odoo config
            const config = await this.orm.call(
                "ir.config_parameter",
                "get_param",
                ["property_fielder.mapbox.token", ""]
            );
            this.mapboxToken = config || "pk.eyJ1IjoibXVhemFtc2FyZmFyYXoiLCJhIjoiY205b2dzdnVlMTVuZDJqczcwbnBseW1tYiJ9.-MvfX63GtzUQceap1g6iJQ";

            // Check if mapboxgl is available
            if (typeof mapboxgl === 'undefined') {
                throw new Error("Mapbox GL JS not loaded");
            }

            // Initialize Mapbox
            mapboxgl.accessToken = this.mapboxToken;

            this.map = new mapboxgl.Map({
                container: this.mapContainer.el,
                style: 'mapbox://styles/mapbox/streets-v12',
                center: [this.longitude, this.latitude],
                zoom: 15,
                attributionControl: false
            });

            // Add navigation controls
            this.map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), 'bottom-right');

            this.map.on('load', () => {
                this.mapLoaded = true;
                this.addPropertyMarker();
                this.state.loading = false;
            });

            this.map.on('error', (e) => {
                console.error("Map error:", e);
                this.state.error = "Map failed to load";
                this.state.loading = false;
            });

        } catch (error) {
            console.error("Failed to initialize property map:", error);
            this.state.error = error.message || "Failed to load map";
            this.state.loading = false;
        }
    }

    addPropertyMarker() {
        if (!this.map || !this.hasCoordinates) return;

        // Create custom marker element
        const el = document.createElement('div');
        el.className = 'property-map-marker';
        el.innerHTML = '<i class="fa fa-building"></i>';
        el.style.cssText = `
            width: 36px;
            height: 36px;
            background: #714B67;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            cursor: pointer;
        `;

        // Create popup with property info
        const popup = new mapboxgl.Popup({ offset: 25 })
            .setHTML(this.getPopupHTML());

        // Add marker
        this.marker = new mapboxgl.Marker({ element: el, anchor: 'center' })
            .setLngLat([this.longitude, this.latitude])
            .setPopup(popup)
            .addTo(this.map);
    }

    getPopupHTML() {
        const data = this.propertyData;
        const address = [data.street, data.city, data.zip].filter(Boolean).join(', ');

        return `
            <div class="property-map-popup" style="min-width: 180px; padding: 4px;">
                <h6 style="margin: 0 0 8px 0; font-weight: 600; color: #714B67;">
                    <i class="fa fa-building"></i> ${data.name || 'Property'}
                </h6>
                ${address ? `<p style="margin: 4px 0; font-size: 13px;"><i class="fa fa-map-marker"></i> ${address}</p>` : ''}
                <p style="margin: 4px 0; font-size: 12px; color: #666;">
                    <i class="fa fa-crosshairs"></i> ${this.latitude.toFixed(5)}, ${this.longitude.toFixed(5)}
                </p>
            </div>
        `;
    }

    updateMarker(lat, lng, data) {
        if (this.marker) {
            this.marker.setLngLat([lng, lat]);
            this.marker.getPopup().setHTML(this.getPopupHTML());
            this.map.flyTo({ center: [lng, lat], zoom: 15 });
        } else {
            this.addPropertyMarker();
        }
    }

    destroyMap() {
        if (this.marker) {
            this.marker.remove();
            this.marker = null;
        }
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
        this.mapLoaded = false;
    }

    onOpenInMaps() {
        // Open in Google Maps
        const url = `https://www.google.com/maps?q=${this.latitude},${this.longitude}`;
        window.open(url, '_blank');
    }

    onCenterMap() {
        if (this.map && this.hasCoordinates) {
            this.map.flyTo({ center: [this.longitude, this.latitude], zoom: 15 });
        }
    }
}

// Register as a field widget
registry.category("fields").add("property_map", {
    component: PropertyMapWidget,
    supportedTypes: ["float"],
});

