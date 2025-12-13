# Property Fielder Inspector - Flutter Mobile App

Flutter mobile application for field inspectors to manage jobs, capture data, and sync with Property Fielder backend.

## 📱 Features

### Core Features
- ✅ **Authentication** - Login with Odoo credentials
- ✅ **Job Management** - View assigned jobs and routes
- ✅ **GPS Check-In/Out** - Track time at job sites with location
- ✅ **Photo Capture** - Take photos with GPS tagging
- ✅ **Digital Signatures** - Capture customer signatures
- ✅ **Notes & Voice** - Add text notes and voice recordings
- ✅ **Offline Mode** - Work without internet, sync later
- ✅ **Navigation** - Get directions to job locations
- ✅ **Background Sync** - Automatic data synchronization

### Technical Features
- 🎨 **Material Design 3** - Modern, beautiful UI
- 🌙 **Dark Mode** - Light and dark themes
- 📦 **Offline Storage** - Hive database for local data
- 🔄 **State Management** - Provider pattern
- 🏗️ **Clean Architecture** - Separation of concerns
- 🧪 **Dependency Injection** - GetIt service locator
- 🔐 **Secure Storage** - Encrypted credentials
- 📡 **REST API** - Retrofit HTTP client

## 🏗️ Project Structure

```
lib/
├── main.dart                          # App entry point
│
├── core/                              # Core functionality
│   ├── api/
│   │   ├── api_client.dart           # Retrofit API client
│   │   └── dio_client.dart           # Dio HTTP configuration
│   │
│   ├── models/                        # Data models
│   │   ├── job.dart
│   │   ├── route.dart
│   │   ├── checkin.dart
│   │   ├── photo.dart
│   │   ├── signature.dart
│   │   ├── note.dart
│   │   └── sync_response.dart
│   │
│   ├── services/                      # Business logic services
│   │   ├── auth_service.dart
│   │   ├── location_service.dart
│   │   ├── camera_service.dart
│   │   ├── storage_service.dart
│   │   └── sync_service.dart
│   │
│   ├── di/                            # Dependency injection
│   │   └── injection.dart
│   │
│   ├── theme/                         # App theming
│   │   └── app_theme.dart
│   │
│   └── utils/                         # Utilities
│       ├── constants.dart
│       ├── validators.dart
│       └── helpers.dart
│
├── features/                          # Feature modules
│   ├── auth/                          # Authentication
│   │   ├── screens/
│   │   │   ├── splash_screen.dart
│   │   │   └── login_screen.dart
│   │   ├── providers/
│   │   │   └── auth_provider.dart
│   │   └── widgets/
│   │
│   ├── jobs/                          # Job management
│   │   ├── screens/
│   │   │   ├── job_list_screen.dart
│   │   │   ├── job_detail_screen.dart
│   │   │   └── job_map_screen.dart
│   │   ├── providers/
│   │   │   └── job_provider.dart
│   │   └── widgets/
│   │       ├── job_card.dart
│   │       └── job_status_badge.dart
│   │
│   ├── routes/                        # Route management
│   │   ├── screens/
│   │   │   └── route_list_screen.dart
│   │   ├── providers/
│   │   │   └── route_provider.dart
│   │   └── widgets/
│   │
│   ├── checkin/                       # Check-in/out
│   │   ├── screens/
│   │   │   └── checkin_screen.dart
│   │   ├── providers/
│   │   │   └── checkin_provider.dart
│   │   └── widgets/
│   │
│   ├── photos/                        # Photo capture
│   │   ├── screens/
│   │   │   ├── photo_capture_screen.dart
│   │   │   └── photo_gallery_screen.dart
│   │   ├── providers/
│   │   │   └── photo_provider.dart
│   │   └── widgets/
│   │
│   ├── signatures/                    # Signature capture
│   │   ├── screens/
│   │   │   └── signature_screen.dart
│   │   ├── providers/
│   │   │   └── signature_provider.dart
│   │   └── widgets/
│   │
│   ├── notes/                         # Notes & voice
│   │   ├── screens/
│   │   │   └── note_screen.dart
│   │   ├── providers/
│   │   │   └── note_provider.dart
│   │   └── widgets/
│   │
│   ├── sync/                          # Data synchronization
│   │   ├── screens/
│   │   │   └── sync_screen.dart
│   │   ├── providers/
│   │   │   └── sync_provider.dart
│   │   └── widgets/
│   │
│   └── dashboard/                     # Dashboard
│       ├── screens/
│       │   └── dashboard_screen.dart
│       └── widgets/
│
└── routes/                            # App routing
    └── app_router.dart
```

## 📦 Dependencies

### Core
- `flutter` - Flutter SDK
- `provider` - State management
- `get_it` - Dependency injection

### HTTP & API
- `dio` - HTTP client
- `retrofit` - Type-safe REST client
- `json_annotation` - JSON serialization

### Local Storage
- `hive` - NoSQL database
- `hive_flutter` - Hive Flutter integration
- `shared_preferences` - Key-value storage
- `path_provider` - File system paths

### Location & Maps
- `geolocator` - GPS location
- `geocoding` - Address geocoding
- `google_maps_flutter` - Google Maps
- `url_launcher` - Launch navigation apps

### Camera & Media
- `image_picker` - Pick images
- `camera` - Camera access
- `photo_view` - Photo viewer

### Signature & Audio
- `signature` - Signature pad
- `record` - Audio recording
- `audioplayers` - Audio playback

### Utilities
- `permission_handler` - Runtime permissions
- `connectivity_plus` - Network status
- `device_info_plus` - Device information
- `package_info_plus` - App version info
- `workmanager` - Background tasks

## 🚀 Getting Started

### Prerequisites
- Flutter SDK 3.0+
- Dart SDK 3.0+
- Android Studio / Xcode
- Property Fielder backend running

### Installation

1. **Clone repository:**
   ```bash
   cd property_fielder/mobile_app
   ```

2. **Install dependencies:**
   ```bash
   flutter pub get
   ```

3. **Generate code:**
   ```bash
   flutter pub run build_runner build --delete-conflicting-outputs
   ```

4. **Configure backend URL:**
   Edit `lib/core/utils/constants.dart`:
   ```dart
   static const String baseUrl = 'http://your-odoo-server:8069';
   ```

5. **Run app:**
   ```bash
   flutter run
   ```

## 🔧 Configuration

### Android

Edit `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.INTERNET"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.RECORD_AUDIO"/>
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>
```

### iOS

Edit `ios/Runner/Info.plist`:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location to track job check-ins</string>
<key>NSCameraUsageDescription</key>
<string>We need camera access to capture job photos</string>
<key>NSMicrophoneUsageDescription</key>
<string>We need microphone access for voice notes</string>
```

## 📱 Usage

### Login
1. Enter Odoo username and password
2. App connects to backend and retrieves inspector profile

### View Jobs
1. Dashboard shows today's jobs
2. Tap job to see details
3. Swipe to filter by status

### Check In
1. Navigate to job location
2. Tap "Check In" button
3. GPS location captured automatically

### Capture Photo
1. Open job detail
2. Tap camera icon
3. Take photo (GPS tagged automatically)
4. Add category and notes

### Get Signature
1. Complete job work
2. Tap "Get Signature"
3. Customer signs on screen
4. Enter signer details

### Sync Data
1. Pull down to refresh
2. Or tap sync icon
3. All offline data uploads to server

## 🧪 Testing

```bash
# Run tests
flutter test

# Run with coverage
flutter test --coverage

# Integration tests
flutter drive --target=test_driver/app.dart
```

## 📦 Build

### Android APK
```bash
flutter build apk --release
```

### Android App Bundle
```bash
flutter build appbundle --release
```

### iOS
```bash
flutter build ios --release
```

## 🔐 Security

- Credentials stored in encrypted storage
- HTTPS for all API calls
- GPS verification for check-ins
- Offline data encrypted with Hive

## 📝 License

LGPL-3

## 🤝 Support

For issues and questions, contact Property Fielder support.

