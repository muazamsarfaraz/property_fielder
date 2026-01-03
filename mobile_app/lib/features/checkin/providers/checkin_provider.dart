import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'dart:io';
import '../../../core/api/api_client.dart';
import '../../../core/models/checkin.dart';
import '../../../core/services/storage_service.dart';

class CheckinProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final StorageService _storageService;

  Checkin? _activeCheckin;
  bool _isLoading = false;
  String? _errorMessage;
  Position? _currentPosition;

  CheckinProvider({
    required ApiClient apiClient,
    required StorageService storageService,
  })  : _apiClient = apiClient,
        _storageService = storageService;

  Checkin? get activeCheckin => _activeCheckin;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasActiveCheckin => _activeCheckin != null && _activeCheckin!.checkoutTime == null;

  Future<Position?> _getCurrentPosition() async {
    try {
      final permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        final requested = await Geolocator.requestPermission();
        if (requested == LocationPermission.denied || requested == LocationPermission.deniedForever) {
          return null;
        }
      }
      return await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
    } catch (e) {
      return null;
    }
  }

  Future<String> _getDeviceInfo() async {
    final deviceInfo = DeviceInfoPlugin();
    if (Platform.isAndroid) {
      final info = await deviceInfo.androidInfo;
      return '${info.manufacturer} ${info.model} (Android ${info.version.release})';
    } else if (Platform.isIOS) {
      final info = await deviceInfo.iosInfo;
      return '${info.name} (iOS ${info.systemVersion})';
    }
    return 'Unknown device';
  }

  Future<bool> checkIn(int jobId, int inspectorId, {String? notes}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentPosition = await _getCurrentPosition();
      final deviceInfo = await _getDeviceInfo();
      final now = DateTime.now().toIso8601String();

      final checkin = Checkin(
        jobId: jobId,
        inspectorId: inspectorId,
        checkinTime: now,
        checkinLatitude: _currentPosition?.latitude,
        checkinLongitude: _currentPosition?.longitude,
        checkinAccuracy: _currentPosition?.accuracy,
        checkinNotes: notes,
        status: 'checked_in',
        deviceInfo: deviceInfo,
        synced: false,
      );

      // Save locally first
      await _storageService.saveCheckin(checkin);
      _activeCheckin = checkin;

      // Try to sync with server
      try {
        final response = await _apiClient.checkin(jobId, checkin.toJson());
        if (response['success'] == true && response['id'] != null) {
          final syncedCheckin = checkin.copyWith(
            id: response['id'],
            synced: true,
          );
          await _storageService.saveCheckin(syncedCheckin);
          _activeCheckin = syncedCheckin;
        }
      } catch (e) {
        // Offline - will sync later
      }

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Check-in failed: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> checkOut(int jobId, {String? notes}) async {
    if (_activeCheckin == null) {
      _errorMessage = 'No active check-in found';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _currentPosition = await _getCurrentPosition();
      final now = DateTime.now().toIso8601String();

      final checkinTime = DateTime.parse(_activeCheckin!.checkinTime);
      final checkoutTime = DateTime.now();
      final duration = checkoutTime.difference(checkinTime).inMinutes;

      final updatedCheckin = _activeCheckin!.copyWith(
        checkoutTime: now,
        checkoutLatitude: _currentPosition?.latitude,
        checkoutLongitude: _currentPosition?.longitude,
        checkoutNotes: notes,
        durationMinutes: duration,
        status: 'checked_out',
        synced: false,
      );

      await _storageService.saveCheckin(updatedCheckin);

      // Try to sync with server
      try {
        final response = await _apiClient.checkout(jobId, {
          'checkout_time': now,
          'checkout_latitude': _currentPosition?.latitude,
          'checkout_longitude': _currentPosition?.longitude,
          'checkout_notes': notes,
          'duration_minutes': duration,
        });
        if (response['success'] == true) {
          final syncedCheckin = updatedCheckin.copyWith(synced: true);
          await _storageService.saveCheckin(syncedCheckin);
        }
      } catch (e) {
        // Offline - will sync later
      }

      _activeCheckin = null;
      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = 'Check-out failed: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}

