/** @odoo-module **/

/**
 * Property Management - Collapsible Chatter
 * 
 * Adds toggle functionality to hide/show the chatter panel.
 * Chatter is hidden by default to maximize form space.
 */

import { Component, onMounted, onPatched, useState } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { FormRenderer } from "@web/views/form/form_renderer";

// SVG icons for toggle button
const ICON_EXPAND = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 18 9 12 15 6"></polyline></svg>`;
const ICON_COLLAPSE = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>`;

// Storage key for remembering state
const STORAGE_KEY = 'pm_chatter_expanded';

/**
 * Initialize the collapsible chatter functionality
 */
function initCollapsibleChatter() {
    const chatter = document.querySelector('.oe_chatter');
    if (!chatter || chatter.dataset.pmInitialized) {
        return;
    }
    
    // Mark as initialized
    chatter.dataset.pmInitialized = 'true';
    
    // Check if this is a property management form (check for property-specific fields)
    const formRenderer = chatter.closest('.o_form_renderer');
    if (!formRenderer) return;
    
    // Get saved state (default to collapsed)
    const isExpanded = localStorage.getItem(STORAGE_KEY) === 'true';
    
    // Set initial state
    chatter.classList.add(isExpanded ? 'pm-chatter-expanded' : 'pm-chatter-collapsed');
    
    // Create toggle button if not exists
    if (!chatter.querySelector('.pm-chatter-toggle')) {
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'pm-chatter-toggle';
        toggleBtn.title = isExpanded ? 'Hide Activity Panel' : 'Show Activity Panel';
        toggleBtn.innerHTML = isExpanded ? ICON_COLLAPSE : ICON_EXPAND;
        toggleBtn.setAttribute('aria-label', 'Toggle activity panel');
        
        toggleBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const expanded = chatter.classList.contains('pm-chatter-expanded');
            
            if (expanded) {
                chatter.classList.remove('pm-chatter-expanded');
                chatter.classList.add('pm-chatter-collapsed');
                toggleBtn.innerHTML = ICON_EXPAND;
                toggleBtn.title = 'Show Activity Panel';
                localStorage.setItem(STORAGE_KEY, 'false');
            } else {
                chatter.classList.remove('pm-chatter-collapsed');
                chatter.classList.add('pm-chatter-expanded');
                toggleBtn.innerHTML = ICON_COLLAPSE;
                toggleBtn.title = 'Hide Activity Panel';
                localStorage.setItem(STORAGE_KEY, 'true');
            }
        });
        
        chatter.insertBefore(toggleBtn, chatter.firstChild);
    }
}

// Patch FormRenderer to initialize chatter on mount/patch
patch(FormRenderer.prototype, {
    setup() {
        super.setup(...arguments);
        
        onMounted(() => {
            // Delay to ensure DOM is fully rendered
            setTimeout(initCollapsibleChatter, 100);
        });
        
        onPatched(() => {
            setTimeout(initCollapsibleChatter, 100);
        });
    }
});

// Also initialize on document ready for initial load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initCollapsibleChatter, 500);
    });
} else {
    setTimeout(initCollapsibleChatter, 500);
}

// Re-initialize when URL changes (SPA navigation)
let lastUrl = location.href;
function setupUrlObserver() {
    const target = document.body || document.documentElement;
    if (target) {
        new MutationObserver(() => {
            if (location.href !== lastUrl) {
                lastUrl = location.href;
                setTimeout(initCollapsibleChatter, 300);
            }
        }).observe(target, { childList: true, subtree: true });
    }
}

// Setup observer when DOM is ready
if (document.body) {
    setupUrlObserver();
} else {
    document.addEventListener('DOMContentLoaded', setupUrlObserver);
}

