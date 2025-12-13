# Property Fielder Field Service Mobile

Mobile application addon for field inspectors to manage jobs on-the-go.

## 📱 Features

### Core Features
- ✅ **Job Management** - View assigned jobs and routes
- ✅ **Check-In/Out** - Track time spent at job sites with GPS
- ✅ **Photo Capture** - Take before/after photos with GPS tagging
- ✅ **Digital Signatures** - Capture customer signatures for job completion
- ✅ **Notes & Observations** - Add notes, issues, and recommendations
- ✅ **Offline Sync** - Work offline and sync when connected
- ✅ **Navigation** - Get directions to job locations
- ✅ **Real-Time Updates** - Sync data with backend

### Mobile-Specific Features
- 📍 **GPS Tracking** - Automatic location capture for check-ins, photos, signatures
- 📷 **Camera Integration** - Direct camera access for photo capture
- ✍️ **Signature Pad** - Touch-based signature capture
- 🗺️ **Map Integration** - View job locations on map
- 🔔 **Push Notifications** - Get notified of new jobs and updates
- 📱 **Responsive Design** - Works on phones and tablets
- 🔒 **Secure Authentication** - User-based access control

## 🏗️ Architecture

### Models

#### 1. **Job Check-In** (`property_fielder.job.checkin`)
Track inspector check-ins and check-outs for jobs.

**Fields:**
- Job reference
- Inspector reference
- Check-in time, latitude, longitude, accuracy
- Check-out time, latitude, longitude
- Duration (computed)
- Status (checked_in, checked_out)
- Notes
- Device info

#### 2. **Job Photo** (`property_fielder.job.photo`)
Photos captured during job execution.

**Fields:**
- Job reference
- Inspector reference
- Image (binary, attachment)
- Capture time, latitude, longitude
- Category (before, during, after, issue, damage, completion, other)
- Notes
- Tags
- Thumbnail (computed)

#### 3. **Job Signature** (`property_fielder.job.signature`)
Customer signatures for job completion.

**Fields:**
- Job reference
- Inspector reference
- Signature (binary, attachment)
- Signer name, title, email, phone
- Signed time, latitude, longitude
- Signature type (completion, approval, receipt, other)
- Agreement text
- Notes

#### 4. **Job Note** (`property_fielder.job.note`)
Notes and observations during job execution.

**Fields:**
- Job reference
- Inspector reference
- Title, content
- Category (observation, issue, recommendation, safety, customer_request, follow_up, general)
- Priority (low, normal, high, urgent)
- Latitude, longitude
- Attachments
- Voice note (binary)
- Tags
- Follow-up tracking

#### 5. **Mobile Sync Log** (`property_fielder.mobile.sync`)
Track mobile app sync operations.

**Fields:**
- Inspector, user
- Sync time, type (full, incremental, upload, download)
- Statistics (jobs, photos, signatures, notes, check-ins)
- Status (success, partial, failed)
- Error message
- Device info, app version, network type
- Duration, data size

#### 6. **Mobile Device** (`property_fielder.mobile.device`)
Registered mobile devices.

**Fields:**
- Device ID (unique)
- Device name, model, OS version
- Inspector reference
- Registration date, last sync
- Active status
- Push token

### REST API Endpoints

#### Authentication
- `POST /mobile/api/auth/login` - Mobile app login

#### Jobs
- `GET /mobile/api/jobs/my` - Get jobs assigned to current inspector
- `GET /mobile/api/jobs/<id>` - Get detailed job information

#### Check-In/Out
- `POST /mobile/api/jobs/<id>/checkin` - Check in to a job
- `POST /mobile/api/jobs/<id>/checkout` - Check out from a job

#### Photos
- `POST /mobile/api/jobs/<id>/photos` - Upload a photo

#### Signatures
- `POST /mobile/api/jobs/<id>/signature` - Capture customer signature

#### Notes
- `POST /mobile/api/jobs/<id>/notes` - Add a note to a job

#### Routes
- `GET /mobile/api/routes/my` - Get routes assigned to current inspector

#### Sync
- `POST /mobile/api/sync` - Sync mobile app data

## 📦 Installation

### Prerequisites
- Odoo 17.0+
- `property_fielder_field_service` addon installed

### Install Steps

1. **Copy addon to Odoo addons directory:**
   ```bash
   cp -r property_fielder_field_service_mobile /path/to/odoo/addons/
   ```

2. **Update apps list:**
   - Go to Apps menu
   - Click "Update Apps List"

3. **Install addon:**
   - Search for "Property Fielder Field Service Mobile"
   - Click "Install"

4. **Configure users:**
   - Go to Settings → Users & Companies → Users
   - Assign "Mobile User" group to field inspectors
   - Link users to inspector profiles

## 🔧 Configuration

### 1. Link Users to Inspectors

Each field inspector must have:
- An Odoo user account
- An inspector profile in Field Service
- The inspector profile linked to the user account

### 2. Mobile App Setup

For native mobile apps (iOS/Android):
- Use the REST API endpoints
- Implement offline storage (SQLite, Realm, etc.)
- Implement sync logic
- Handle GPS, camera, signature capture

For web-based mobile:
- Access Odoo through mobile browser
- Use responsive views provided
- Enable geolocation in browser

## 🚀 Usage

### For Inspectors

1. **Login** - Use Odoo credentials
2. **View Jobs** - See assigned jobs for today/tomorrow
3. **Navigate** - Get directions to job location
4. **Check In** - Arrive at job site, check in with GPS
5. **Capture Photos** - Take before/during/after photos
6. **Add Notes** - Document observations, issues
7. **Get Signature** - Customer signs for completion
8. **Check Out** - Leave job site, check out with GPS
9. **Sync** - Upload all data to server

### For Managers

1. **Monitor Progress** - See real-time job status
2. **View Photos** - Review photos from field
3. **Review Signatures** - Verify job completion
4. **Read Notes** - Check inspector observations
5. **Track Time** - See check-in/out times
6. **Analyze Performance** - Review sync logs, device usage

## 🔐 Security

- **User-based access** - Inspectors only see their own data
- **Manager access** - Managers see all data
- **GPS verification** - Location captured for all actions
- **Audit trail** - All actions logged with timestamps
- **Secure API** - Authentication required for all endpoints

## 📊 Data Flow

```
Mobile App → REST API → Odoo Backend → Database
     ↓           ↓            ↓
  Offline    Validation   Processing
  Storage    Security     Business Logic
     ↓           ↓            ↓
   Sync    →  Response  →  Update UI
```

## 🛠️ Development

### Extend API

Add new endpoints in `controllers/mobile_api.py`:

```python
@http.route('/mobile/api/custom', type='json', auth='user', methods=['POST'])
def custom_endpoint(self, param1, param2):
    # Your logic here
    return {'success': True, 'data': result}
```

### Add New Models

Create model in `models/` directory and add to `__init__.py`.

### Customize Views

Edit XML views in `views/` directory.

## 📝 License

LGPL-3

## 🤝 Support

For issues and questions, contact Property Fielder support.

