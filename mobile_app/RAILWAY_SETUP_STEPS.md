# 🚂 Railway Mobile App Deployment - Step by Step

## ⚠️ Important: The Issue

The error you're seeing:
```
ERROR: failed to build: "/start.sh": not found
```

This happens because Railway is trying to build the **Odoo backend** (property_fielder service) instead of the mobile app.

## ✅ Solution: Create Mobile App Service First

### Step 1: Open Railway Dashboard

Go to your project:
```
https://railway.com/project/1da4fd12-9fe3-4daa-aec7-33cd8e164098
```

### Step 2: Create New Service

1. Click the **"+ New"** button in the top right
2. Select **"Empty Service"**
3. You'll see a new empty service card

### Step 3: Configure the Service

1. Click on the new service card
2. Click **"Settings"** in the left sidebar
3. Under **"Service Name"**, enter: `mobile-app`
4. Scroll down to **"Source"** section
5. Click **"Connect Repo"** (if using GitHub)
   - OR click **"Deploy from CLI"** if deploying manually

### Step 4A: If Using GitHub

1. Select your repository
2. **IMPORTANT:** Set **"Root Directory"** to: `property_fielder/mobile_app`
3. Click **"Deploy"**
4. Railway will detect the Dockerfile and start building

### Step 4B: If Using CLI

1. In your terminal, navigate to the mobile app directory:
   ```bash
   cd e:\dev\RoutingScheduling\property_fielder\mobile_app
   ```

2. Link to the new service:
   ```bash
   railway service mobile-app
   ```

3. Deploy:
   ```bash
   railway up --detach
   ```

### Step 5: Generate Domain

Once deployed:

1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Copy the URL (e.g., `https://mobile-app-production.up.railway.app`)

### Step 6: Test

Open the generated URL in your browser. You should see the Flutter app login screen!

---

## 🔍 Why This Happens

Railway projects can have multiple services:

```
property-fielder (project)
├── property_fielder (service) ← Odoo backend
│   └── Uses: property_fielder/Dockerfile
│   └── Needs: start.sh, odoo.conf, etc.
│
└── mobile-app (service) ← Flutter web app (NEW!)
    └── Uses: property_fielder/mobile_app/Dockerfile
    └── Needs: nginx.conf, Flutter build files
```

When you deploy without specifying a service, Railway uses the default service (property_fielder), which has the wrong Dockerfile.

---

## 🎯 Quick Fix Checklist

- [ ] Open Railway dashboard
- [ ] Create new service named "mobile-app"
- [ ] Set root directory to "property_fielder/mobile_app" (if using GitHub)
- [ ] Deploy
- [ ] Generate domain
- [ ] Test the URL

---

## 🐛 Troubleshooting

### Error: "Could not find root directory: property_fielder/mobile_app"

**Cause:** Railway is looking from the wrong base directory

**Fix:**
1. Make sure you're creating a **new service**, not modifying the existing one
2. When setting root directory, use exactly: `property_fielder/mobile_app`
3. If using CLI, make sure you're in the mobile_app directory when running `railway up`

### Error: "Service not found"

**Cause:** The mobile-app service doesn't exist yet

**Fix:**
1. Create the service in the Railway dashboard first
2. Then link to it with: `railway service mobile-app`

### Build succeeds but app doesn't load

**Cause:** Nginx configuration or Flutter build issue

**Fix:**
1. Check deployment logs: `railway logs --service mobile-app`
2. Verify Dockerfile is correct
3. Check that nginx.conf exists

---

## 📋 Current Status

✅ **Files Ready:**
- Dockerfile (multi-stage Flutter + Nginx)
- nginx.conf (web server config)
- railway.toml (deployment config)
- .dockerignore (build optimization)

✅ **Railway Project:**
- Project: property-fielder
- Environment: production
- Existing service: property_fielder (Odoo)

❌ **Missing:**
- mobile-app service (needs to be created)

---

## 🚀 After Deployment

Once the mobile-app service is deployed:

```bash
# Check status
railway status --service mobile-app

# View logs
railway logs --service mobile-app

# Get domain
railway domain --service mobile-app

# Redeploy
railway up --service mobile-app
```

---

## 💡 Pro Tip

If you're deploying from GitHub, Railway will automatically redeploy when you push changes to the `property_fielder/mobile_app` directory. Set up a watch pattern in railway.toml (already configured!).

---

**Ready to deploy? Follow the steps above and you'll have a live Flutter web app in 5-10 minutes!** 🎉

