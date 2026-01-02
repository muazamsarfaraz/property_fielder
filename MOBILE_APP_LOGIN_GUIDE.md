# How to Login to the Flutter Mobile App

## ✅ Backend is Now Running Locally!

The Odoo backend is running on your machine at:
- **URL:** `http://localhost:8069`
- **Database:** `property_fielder`

The Flutter mobile app has been updated to connect to this local backend.

## 🔐 Login Credentials

### Option 1: Default Admin User
- **Username:** `admin`
- **Password:** `admin`

### Option 2: Create an Inspector User

1. **Access Odoo Web Interface:**
   - Open browser: `http://localhost:8069`
   - Login with admin credentials above
   - Database: `property_fielder`

2. **Create Inspector User:**
   - Go to Settings → Users & Companies → Users
   - Click "Create"
   - Fill in:
     - Name: `Test Inspector`
     - Login: `inspector`
     - Password: `inspector123`
   - Save

3. **Assign Inspector Role:**
   - In the user form, go to "Access Rights" tab
   - Enable "Field Service / Inspector" access
   - Save

## 📱 Testing the Mobile App

### Step 1: Open the App
The Flutter app should already be open in Chrome at `http://localhost:8081`

If not, run:
```bash
cd property_fielder/mobile_app
flutter run -d chrome --web-port=8081
```

### Step 2: Login
1. Wait for the splash screen (2 seconds)
2. You'll see the login screen
3. Enter credentials:
   - Username: `admin` (or `inspector` if you created one)
   - Password: `admin` (or `inspector123`)
4. Click "Login"

### Step 3: Expected Behavior
- ✅ Loading indicator appears
- ✅ API call to `http://localhost:8069/mobile/api/auth/login`
- ✅ On success: Navigate to dashboard
- ✅ Auth token saved in local storage

## 🐛 Troubleshooting

### Error: "Connection error"
**Cause:** Backend not running or wrong URL

**Fix:**
```bash
# Check if Odoo is running
docker ps | findstr property_fielder

# If not running, start it
cd property_fielder
docker-compose up -d

# Wait 30 seconds for Odoo to initialize
```

### Error: "Login failed" or "Invalid credentials"
**Cause:** User doesn't exist or wrong password

**Fix:**
1. Access Odoo web: `http://localhost:8069`
2. Login as admin
3. Check/create the user
4. Verify password

### Error: "Database not found"
**Cause:** Odoo database not initialized

**Fix:**
1. Access `http://localhost:8069`
2. Create database named `property_fielder`
3. Install required modules:
   - Field Service
   - Property Fielder modules

### App won't load in Chrome
**Fix:**
```bash
# Kill Chrome
taskkill /F /IM chrome.exe

# Restart Flutter app
cd property_fielder/mobile_app
flutter clean
flutter pub get
flutter run -d chrome --web-port=8081
```

## 🔍 Debugging

### Check Backend Logs
```bash
docker logs property_fielder_odoo --tail 100 -f
```

### Check API Endpoint
Test the login endpoint directly:
```powershell
$headers = @{'Content-Type'='application/json'}
$body = @{
    jsonrpc='2.0'
    method='call'
    params=@{
        username='admin'
        password='admin'
    }
    id=1
} | ConvertTo-Json

Invoke-WebRequest -Uri 'http://localhost:8069/mobile/api/auth/login' -Method POST -Body $body -Headers $headers
```

### Check Flutter Console
Open Chrome DevTools (F12) and check:
- Console tab for errors
- Network tab for API calls
- Application → Storage → IndexedDB for saved data

## 📝 Next Steps After Login

Once logged in, you should see:
1. **Dashboard** - Overview of jobs and routes
2. **Navigation Menu** - Access to all features
3. **Sync Status** - Shows connection to backend

You can then test:
- Creating jobs
- Viewing routes
- Taking photos
- Adding notes
- Offline functionality

## 🚀 Production Deployment

To use the Railway production backend instead:

1. Update `property_fielder/mobile_app/lib/core/di/injection.dart`:
   ```dart
   final baseUrl = storageService.getServerUrl() ?? 'https://propertyfielder-production.up.railway.app';
   ```

2. Or change it in the app settings (if settings screen allows server URL configuration)

---

**Current Status:**
- ✅ Backend running locally on `http://localhost:8069`
- ✅ Mobile app configured to use local backend
- ✅ App running in Chrome on `http://localhost:8081`
- ✅ Ready to login and test!

