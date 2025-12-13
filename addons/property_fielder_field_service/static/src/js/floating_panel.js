/** @odoo-module **/

import { Component, useState, useRef, onMounted, onWillUnmount } from "@odoo/owl";

/**
 * Floating Panel Component - Draggable, Resizable, Collapsible
 * Used in the enhanced dispatch view for PLAN, OPTIMIZE, SCHEDULE tabs
 */
export class FloatingPanel extends Component {
    static template = "property_fielder_field_service.FloatingPanel";
    static props = {
        title: { type: String },
        icon: { type: String, optional: true },
        defaultPosition: { type: Object, optional: true },
        defaultSize: { type: Object, optional: true },
        minWidth: { type: Number, optional: true },
        minHeight: { type: Number, optional: true },
        collapsible: { type: Boolean, optional: true },
        resizable: { type: Boolean, optional: true },
        panelId: { type: String },
        onClose: { type: Function, optional: true },
        slots: { type: Object, optional: true },
    };

    static defaultProps = {
        icon: "fa-window-maximize",
        defaultPosition: { x: 20, y: 80 },
        defaultSize: { width: 320, height: 400 },
        minWidth: 250,
        minHeight: 200,
        collapsible: true,
        resizable: true,
    };

    setup() {
        this.panelRef = useRef("panel");
        this.headerRef = useRef("header");
        
        this.state = useState({
            collapsed: false,
            position: { ...this.props.defaultPosition },
            size: { ...this.props.defaultSize },
            isDragging: false,
            isResizing: false,
            zIndex: 100,
        });

        this.dragOffset = { x: 0, y: 0 };
        this.resizeStart = { width: 0, height: 0, x: 0, y: 0 };

        onMounted(() => this.loadState());
        onWillUnmount(() => this.saveState());
    }

    loadState() {
        const saved = localStorage.getItem(`panel_state_${this.props.panelId}`);
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                this.state.position = parsed.position || this.state.position;
                this.state.size = parsed.size || this.state.size;
                this.state.collapsed = parsed.collapsed || false;
            } catch (e) {
                console.warn("Failed to load panel state:", e);
            }
        }
    }

    saveState() {
        const stateToSave = {
            position: this.state.position,
            size: this.state.size,
            collapsed: this.state.collapsed,
        };
        localStorage.setItem(`panel_state_${this.props.panelId}`, JSON.stringify(stateToSave));
    }

    toggleCollapse() {
        this.state.collapsed = !this.state.collapsed;
        this.saveState();
    }

    onClose() {
        if (this.props.onClose) {
            this.props.onClose();
        }
    }

    bringToFront() {
        // Increase z-index to bring panel to front
        this.state.zIndex = Date.now() % 10000 + 100;
    }

    // Drag handlers
    onDragStart(ev) {
        if (ev.target.classList.contains('panel-resize-handle')) return;
        
        this.bringToFront();
        this.state.isDragging = true;
        this.dragOffset = {
            x: ev.clientX - this.state.position.x,
            y: ev.clientY - this.state.position.y,
        };

        document.addEventListener('mousemove', this.onDragMove.bind(this));
        document.addEventListener('mouseup', this.onDragEnd.bind(this));
        ev.preventDefault();
    }

    onDragMove(ev) {
        if (!this.state.isDragging) return;
        
        this.state.position = {
            x: Math.max(0, ev.clientX - this.dragOffset.x),
            y: Math.max(0, ev.clientY - this.dragOffset.y),
        };
    }

    onDragEnd() {
        this.state.isDragging = false;
        document.removeEventListener('mousemove', this.onDragMove.bind(this));
        document.removeEventListener('mouseup', this.onDragEnd.bind(this));
        this.saveState();
    }

    // Resize handlers
    onResizeStart(ev) {
        if (!this.props.resizable) return;
        
        this.bringToFront();
        this.state.isResizing = true;
        this.resizeStart = {
            width: this.state.size.width,
            height: this.state.size.height,
            x: ev.clientX,
            y: ev.clientY,
        };

        document.addEventListener('mousemove', this.onResizeMove.bind(this));
        document.addEventListener('mouseup', this.onResizeEnd.bind(this));
        ev.preventDefault();
        ev.stopPropagation();
    }

    onResizeMove(ev) {
        if (!this.state.isResizing) return;
        
        const deltaX = ev.clientX - this.resizeStart.x;
        const deltaY = ev.clientY - this.resizeStart.y;
        
        this.state.size = {
            width: Math.max(this.props.minWidth, this.resizeStart.width + deltaX),
            height: Math.max(this.props.minHeight, this.resizeStart.height + deltaY),
        };
    }

    onResizeEnd() {
        this.state.isResizing = false;
        document.removeEventListener('mousemove', this.onResizeMove.bind(this));
        document.removeEventListener('mouseup', this.onResizeEnd.bind(this));
        this.saveState();
    }

    get panelStyle() {
        const styles = [
            `left: ${this.state.position.x}px`,
            `top: ${this.state.position.y}px`,
            `z-index: ${this.state.zIndex}`,
        ];
        
        if (!this.state.collapsed) {
            styles.push(`width: ${this.state.size.width}px`);
            styles.push(`height: ${this.state.size.height}px`);
        }
        
        return styles.join('; ');
    }
}

