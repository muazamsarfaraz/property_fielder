/** @odoo-module **/

import { Component, useState, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Mobile Camera Widget for capturing photos directly from device camera.
 * Supports both file input (fallback) and direct camera access via MediaDevices API.
 */
export class MobileCameraWidget extends Component {
    static template = "property_fielder_property_management.MobileCameraWidget";
    static props = {
        onCapture: { type: Function },
        multiple: { type: Boolean, optional: true },
        category: { type: String, optional: true },
    };

    setup() {
        this.state = useState({
            isCapturing: false,
            hasCamera: false,
            error: null,
            capturedPhotos: [],
        });
        this.videoRef = useRef("video");
        this.canvasRef = useRef("canvas");
        this.fileInputRef = useRef("fileInput");
        this.notification = useService("notification");

        // Check for camera support
        this.checkCameraSupport();
    }

    async checkCameraSupport() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            try {
                const devices = await navigator.mediaDevices.enumerateDevices();
                this.state.hasCamera = devices.some(d => d.kind === "videoinput");
            } catch (e) {
                this.state.hasCamera = false;
            }
        }
    }

    async startCamera() {
        this.state.isCapturing = true;
        this.state.error = null;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    facingMode: "environment", // Prefer back camera
                    width: { ideal: 1920 },
                    height: { ideal: 1080 },
                },
            });
            
            if (this.videoRef.el) {
                this.videoRef.el.srcObject = stream;
                this.stream = stream;
            }
        } catch (error) {
            this.state.error = "Camera access denied. Please use file upload.";
            this.state.isCapturing = false;
            console.error("Camera error:", error);
        }
    }

    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        this.state.isCapturing = false;
    }

    capturePhoto() {
        if (!this.videoRef.el || !this.canvasRef.el) return;

        const video = this.videoRef.el;
        const canvas = this.canvasRef.el;
        const context = canvas.getContext("2d");

        // Set canvas size to video size
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        // Draw video frame to canvas
        context.drawImage(video, 0, 0);

        // Convert to blob
        canvas.toBlob(async (blob) => {
            const photoData = {
                blob: blob,
                dataUrl: canvas.toDataURL("image/jpeg", 0.85),
                timestamp: new Date().toISOString(),
                category: this.props.category || "general",
            };

            // Add GPS if available
            if (navigator.geolocation) {
                try {
                    const position = await this.getLocation();
                    photoData.latitude = position.coords.latitude;
                    photoData.longitude = position.coords.longitude;
                    photoData.accuracy = position.coords.accuracy;
                } catch (e) {
                    console.warn("GPS not available:", e);
                }
            }

            this.state.capturedPhotos.push(photoData);
            this.props.onCapture(photoData);

            this.notification.add("Photo captured!", { type: "success" });

            if (!this.props.multiple) {
                this.stopCamera();
            }
        }, "image/jpeg", 0.85);
    }

    getLocation() {
        return new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0,
            });
        });
    }

    onFileSelect(event) {
        const files = event.target.files;
        if (!files.length) return;

        Array.from(files).forEach(file => {
            const reader = new FileReader();
            reader.onload = (e) => {
                const photoData = {
                    dataUrl: e.target.result,
                    timestamp: new Date().toISOString(),
                    category: this.props.category || "general",
                    filename: file.name,
                };
                this.state.capturedPhotos.push(photoData);
                this.props.onCapture(photoData);
            };
            reader.readAsDataURL(file);
        });
    }

    openFileInput() {
        if (this.fileInputRef.el) {
            this.fileInputRef.el.click();
        }
    }
}

// Register the component
registry.category("components").add("MobileCameraWidget", MobileCameraWidget);

