# Property Fielder Mobile App - Testing Guide

## Current Status

✅ **App Successfully Initialized!**

The Flutter web app has been successfully built and is running. The initialization logs show:

```
🔧 Initializing Hive...
✅ Hive initialized
🔧 Setting up dependencies...
✅ Dependencies set up
🔧 Initializing WorkManager...
✅ WorkManager initialized
✅ All initialization complete!
```

## Running the App

### Start the App
```bash
cd property_fielder/mobile_app
flutter run -d chrome --web-port=8081
```

The app will open in Chrome automatically.

### Important Notes
- **Do NOT use `web-server` device** - it doesn't render Flutter apps properly
- **Use Chrome device** for proper rendering and debugging
- The app runs on `http://localhost:8081`

## Manual Testing Checklist

### 1. Splash Screen (First Screen)
- [ ] App shows "Property Fielder" logo/icon
- [ ] Shows "Field Service Inspector" subtitle
- [ ] Shows loading spinner
- [ ] Automatically navigates to login after 2 seconds

### 2. Login Screen
- [ ] Shows username/email input field
- [ ] Shows password input field
- [ ] Shows "Login" button
- [ ] Shows app branding

#### Test Login
**Backend URL:** `https://propertyfielder-production.up.railway.app`

**Test Credentials:**
- Username: `inspector`
- Password: `inspector123`

**Expected Behavior:**
- On success: Navigate to dashboard
- On failure: Show error message
- While loading: Show loading indicator

### 3. Dashboard (After Login)
- [ ] Shows navigation drawer/menu
- [ ] Shows list of jobs or empty state
- [ ] Shows sync status
- [ ] Can navigate to different sections

### 4. Navigation Menu
Test all menu items:
- [ ] Jobs
- [ ] Routes
- [ ] Check-ins
- [ ] Photos
- [ ] Signatures
- [ ] Notes
- [ ] Sync
- [ ] Safety
- [ ] Templates
- [ ] Settings
- [ ] Logout

### 5. Settings Screen
- [ ] Can view/change server URL
- [ ] Can view app version
- [ ] Can clear local data
- [ ] Can logout

## Known Issues

### Flutter Web Rendering
- **Issue:** Flutter web doesn't render in automated browsers (Playwright, Puppeteer)
- **Workaround:** Use Chrome device directly with `flutter run -d chrome`
- **Root Cause:** Flutter web rendering engine doesn't create `flt-scene-host` in headless/automated browsers

### Backend Connection
- **Issue:** Backend API might not be deployed yet
- **Check:** Verify Railway deployment status
- **Workaround:** Can test offline features (local storage, UI navigation)

## Debugging

### View Console Logs
Open Chrome DevTools (F12) and check the Console tab for:
- Initialization logs
- API request/response logs
- Error messages

### View Network Requests
Open Chrome DevTools → Network tab to see:
- API calls to backend
- Request/response payloads
- HTTP status codes

### View Local Storage
Open Chrome DevTools → Application → Storage:
- IndexedDB (Hive databases)
- Local Storage (settings)

## Next Steps

1. **Test Login Flow**
   - Try logging in with test credentials
   - Verify navigation to dashboard
   - Check if auth token is stored

2. **Test Offline Features**
   - Create local data (jobs, notes, photos)
   - Verify data persists after refresh
   - Test sync functionality

3. **Test Backend Integration**
   - Verify API endpoints are accessible
   - Test data synchronization
   - Test real-time updates

4. **Deploy Backend**
   - Ensure Railway backend is deployed
   - Verify API endpoints are working
   - Test end-to-end flow

## Troubleshooting

### App Won't Load
```bash
# Clean build
flutter clean
flutter pub get
flutter run -d chrome --web-port=8081
```

### Chrome Won't Open
```bash
# Kill all Chrome processes
taskkill /F /IM chrome.exe

# Restart app
flutter run -d chrome --web-port=8081
```

### Port Already in Use
```bash
# Use different port
flutter run -d chrome --web-port=8082
```

