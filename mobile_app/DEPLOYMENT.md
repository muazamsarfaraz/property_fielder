# Flutter Mobile App - Railway Deployment Guide

## Overview

This guide explains how to deploy the Flutter web app to Railway as a separate service.

## Prerequisites

- Railway CLI installed and authenticated
- Railway project: `property-fielder` (ID: 1da4fd12-9fe3-4daa-aec7-33cd8e164098)

## Deployment Steps

### 1. Navigate to Mobile App Directory

```bash
cd property_fielder/mobile_app
```

### 2. Link to Railway Project

```bash
railway link -p 1da4fd12-9fe3-4daa-aec7-33cd8e164098
```

### 3. Create New Service

In the Railway dashboard or CLI, create a new service called `mobile-app`.

### 4. Deploy

```bash
railway up
```

Or use the Railway dashboard to deploy from GitHub.

## Configuration

### Environment Variables

No environment variables are required. The app is configured to connect to:
- **Backend URL:** `https://propertyfielder-production.up.railway.app`

Users can override this in the app settings.

### Build Configuration

The app uses a multi-stage Docker build:

1. **Stage 1:** Build Flutter web app using official Flutter Docker image
2. **Stage 2:** Serve with Nginx

### Files

- `Dockerfile` - Multi-stage build configuration
- `nginx.conf` - Nginx server configuration
- `railway.toml` - Railway deployment configuration
- `.dockerignore` - Files to exclude from Docker build

## Architecture

```
┌─────────────────────────────────────────┐
│         Railway Project                 │
│  (property-fielder)                     │
│                                         │
│  ┌─────────────────┐  ┌──────────────┐ │
│  │  Service 1:     │  │  Service 2:  │ │
│  │  property_      │  │  mobile-app  │ │
│  │  fielder        │  │  (Flutter)   │ │
│  │  (Odoo Backend) │  │              │ │
│  │                 │  │              │ │
│  │  Port: 8069     │  │  Port: 80    │ │
│  └─────────────────┘  └──────────────┘ │
│         ▲                     │         │
│         │                     │         │
│         └─────────────────────┘         │
│           API Calls                     │
└─────────────────────────────────────────┘
```

## Testing After Deployment

1. **Get the deployed URL:**
   ```bash
   railway domain
   ```

2. **Access the app:**
   Open the URL in your browser (e.g., `https://mobile-app-production.up.railway.app`)

3. **Test login:**
   - Username: `admin` or `inspector`
   - Password: `admin` or `inspector123`

## Troubleshooting

### Build Fails

**Check logs:**
```bash
railway logs --deployment
```

**Common issues:**
- Flutter version mismatch
- Missing dependencies
- Docker build timeout

**Solution:**
- Ensure Dockerfile uses stable Flutter image
- Check pubspec.yaml for correct dependencies

### App Loads but Can't Connect to Backend

**Issue:** CORS errors or connection refused

**Solution:**
1. Verify backend is running: `https://propertyfielder-production.up.railway.app`
2. Check backend has CORS enabled for mobile app domain
3. Verify API endpoints exist

### Login Fails

**Issue:** "No inspector profile found" or "Invalid credentials"

**Solution:**
1. Access Odoo backend: `https://propertyfielder-production.up.railway.app`
2. Login as admin
3. Create inspector user and profile
4. Ensure mobile API module is installed

## Local Development

For local development with hot reload:

```bash
# Start local backend
cd ../
docker-compose up -d

# Start CORS proxy
cd mobile_app
node cors-proxy.js

# Run Flutter app
flutter run -d chrome --web-port=8081
```

Update `lib/core/di/injection.dart` to use `http://localhost:8070` for local development.

## Production URLs

- **Mobile App:** TBD (after deployment)
- **Backend API:** `https://propertyfielder-production.up.railway.app`

## Next Steps

1. Deploy the mobile app to Railway
2. Generate domain for the mobile app service
3. Test login and functionality
4. Configure custom domain (optional)
5. Set up CI/CD for automatic deployments

