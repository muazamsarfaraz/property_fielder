# 🚀 Deploy Flutter Mobile App to Railway - Quick Guide

## Option 1: Deploy via Railway Dashboard (Recommended)

### Step 1: Open Railway Project
1. Go to: https://railway.app/project/1da4fd12-9fe3-4daa-aec7-33cd8e164098
2. You should see the `property-fielder` project

### Step 2: Create New Service
1. Click **"+ New"** button
2. Select **"GitHub Repo"** (if you have this repo on GitHub)
   - OR select **"Empty Service"** to deploy manually

### Step 3: Configure Service (if using Empty Service)
1. Name the service: `mobile-app`
2. Go to **Settings** tab
3. Under **Source**, click **"Connect Repo"**
4. Select your repository and set:
   - **Root Directory:** `property_fielder/mobile_app`
   - **Build Command:** (leave empty - Docker will handle it)

### Step 4: Deploy
1. Railway will automatically detect the `Dockerfile`
2. Click **"Deploy"** or push to trigger deployment
3. Wait 5-10 minutes for build to complete

### Step 5: Generate Domain
1. Go to **Settings** tab
2. Under **Networking**, click **"Generate Domain"**
3. Copy the generated URL (e.g., `https://mobile-app-production.up.railway.app`)

### Step 6: Test
1. Open the generated URL in your browser
2. You should see the Flutter app login screen
3. Try logging in with:
   - Username: `admin`
   - Password: `admin`

---

## Option 2: Deploy via Railway CLI

### Prerequisites
```bash
# Install Railway CLI (if not installed)
# Windows: scoop install railway
# Mac: brew install railway
# Or: npm install -g @railway/cli

# Login
railway login
```

### Deploy Steps

```bash
# Navigate to mobile app directory
cd property_fielder/mobile_app

# Link to project
railway link -p 1da4fd12-9fe3-4daa-aec7-33cd8e164098

# Create service (in Railway dashboard first!)
# Then deploy
railway up --service mobile-app

# Generate domain
railway domain --service mobile-app
```

---

## Option 3: Deploy via GitHub Actions (CI/CD)

Create `.github/workflows/deploy-mobile-app.yml`:

```yaml
name: Deploy Mobile App to Railway

on:
  push:
    branches: [main]
    paths:
      - 'property_fielder/mobile_app/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      
      - name: Deploy to Railway
        run: |
          cd property_fielder/mobile_app
          railway up --service mobile-app
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Troubleshooting

### Build Fails

**Error:** "Flutter SDK not found"
- **Solution:** Dockerfile uses official Flutter image, should work automatically

**Error:** "Out of memory"
- **Solution:** Increase Railway service memory in Settings

### App Loads but Shows Blank Screen

**Issue:** Flutter web rendering issue
- **Solution:** App uses `canvaskit` renderer, should work in all modern browsers
- Try different browser (Chrome recommended)

### Can't Connect to Backend

**Error:** "Connection error" or CORS error
- **Solution:** 
  1. Verify backend is running: https://propertyfielder-production.up.railway.app
  2. Check backend logs for errors
  3. Ensure mobile API module is installed in Odoo

### Login Fails

**Error:** "No inspector profile found"
- **Solution:**
  1. Access Odoo: https://propertyfielder-production.up.railway.app
  2. Login as admin/admin
  3. Create inspector user and profile
  4. Install `property_fielder_field_service_mobile` module

---

## Current Status

✅ **Files Ready:**
- `Dockerfile` - Multi-stage build
- `nginx.conf` - Web server config
- `railway.toml` - Railway config
- `.dockerignore` - Build optimization

✅ **App Configuration:**
- Backend URL: `https://propertyfielder-production.up.railway.app`
- Build: Production optimized
- Renderer: CanvasKit (best compatibility)

⏳ **Next Steps:**
1. Create service in Railway dashboard
2. Deploy the app
3. Generate domain
4. Test login

---

## Quick Deploy Command

If you just want to deploy NOW:

```bash
cd property_fielder/mobile_app
railway link -p 1da4fd12-9fe3-4daa-aec7-33cd8e164098
railway up
railway domain
```

Then open the generated URL! 🎉

