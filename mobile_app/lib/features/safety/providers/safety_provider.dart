import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
import '../../../core/api/api_client.dart';
import '../../../core/models/safety_timer.dart';
import '../../../core/services/storage_service.dart';

/// Provider for Safety Timer (Lone Worker Protection) feature.
/// 
/// HSE Compliance: Enables field inspectors working alone to:
/// - Start a safety timer when beginning work
/// - Extend the timer if the job takes longer
/// - Cancel/complete the timer when safe
/// - Trigger a PANIC button for immediate help
class SafetyProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final StorageService _storageService;

  SafetyTimer? _activeTimer;
  bool _isLoading = false;
  String? _errorMessage;
  Timer? _countdownTimer;

  SafetyProvider({
    required ApiClient apiClient,
    required StorageService storageService,
  })  : _apiClient = apiClient,
        _storageService = storageService {
    _loadActiveTimer();
  }

  SafetyTimer? get activeTimer => _activeTimer;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  bool get hasActiveTimer => _activeTimer?.isActive ?? false;

  void _loadActiveTimer() {
    // Load from local storage if available
    final timerData = _storageService.getSetting<Map<String, dynamic>>('active_safety_timer');
    if (timerData != null) {
      _activeTimer = SafetyTimer.fromJson(timerData);
      if (_activeTimer!.isActive) {
        _startCountdown();
      }
    }
  }

  void _startCountdown() {
    _countdownTimer?.cancel();
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_activeTimer == null || !_activeTimer!.isActive) {
        timer.cancel();
        return;
      }
      // Update remaining time
      notifyListeners();
      
      // Check if timer expired
      if (_activeTimer!.remainingDuration == Duration.zero) {
        _handleTimerExpired();
      }
    });
  }

  void _handleTimerExpired() {
    _activeTimer = _activeTimer?.copyWith(state: 'overdue', isOverdue: true);
    _saveActiveTimer();
    notifyListeners();
  }

  Future<void> _saveActiveTimer() async {
    if (_activeTimer != null) {
      await _storageService.setSetting('active_safety_timer', _activeTimer!.toJson());
    } else {
      await _storageService.setSetting('active_safety_timer', null);
    }
  }

  /// Start a new safety timer
  Future<bool> startTimer({
    int? jobId,
    int durationMinutes = 60,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Get current location
      Position? position;
      try {
        position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high,
        );
      } catch (e) {
        // Location not available, continue anyway
      }

      final response = await _apiClient.startSafetyTimer({
        'job_id': jobId,
        'duration_minutes': durationMinutes,
        'latitude': position?.latitude,
        'longitude': position?.longitude,
      });

      if (response['success'] == true) {
        _activeTimer = SafetyTimer(
          id: response['timer_id'] as int?,
          inspectorId: 0, // Will be set from storage
          jobId: jobId,
          startedAt: DateTime.now().toIso8601String(),
          expectedEnd: response['expected_end'] as String,
          state: 'active',
          lastKnownLat: position?.latitude,
          lastKnownLong: position?.longitude,
        );
        await _saveActiveTimer();
        _startCountdown();
        _isLoading = false;
        notifyListeners();
        return true;
      }

      _errorMessage = response['error'] as String? ?? 'Failed to start timer';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = 'Connection error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Extend the active timer
  Future<bool> extendTimer({int minutes = 30}) async {
    if (_activeTimer == null || !_activeTimer!.canExtend) {
      _errorMessage = 'No active timer to extend';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.extendSafetyTimer({
        'timer_id': _activeTimer!.id,
        'minutes': minutes,
      });

      if (response['success'] == true) {
        _activeTimer = _activeTimer!.copyWith(
          expectedEnd: response['expected_end'] as String,
          extendedCount: _activeTimer!.extendedCount + 1,
          state: 'active',
          isOverdue: false,
        );
        await _saveActiveTimer();
        _isLoading = false;
        notifyListeners();
        return true;
      }

      _errorMessage = response['error'] as String? ?? 'Failed to extend timer';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = 'Connection error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Cancel/complete the active timer (inspector is safe)
  Future<bool> cancelTimer() async {
    if (_activeTimer == null) {
      _errorMessage = 'No active timer to cancel';
      notifyListeners();
      return false;
    }

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.cancelSafetyTimer({
        'timer_id': _activeTimer!.id,
      });

      if (response['success'] == true) {
        _countdownTimer?.cancel();
        _activeTimer = _activeTimer!.copyWith(state: 'completed');
        await _storageService.setSetting('active_safety_timer', null);
        _activeTimer = null;
        _isLoading = false;
        notifyListeners();
        return true;
      }

      _errorMessage = response['error'] as String? ?? 'Failed to cancel timer';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = 'Connection error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// PANIC BUTTON - Trigger immediate emergency response
  Future<bool> triggerPanic({String reason = ''}) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Get current location for emergency response
      Position? position;
      try {
        position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high,
          timeLimit: const Duration(seconds: 5),
        );
      } catch (e) {
        // Continue even without location
      }

      final response = await _apiClient.triggerPanic({
        'reason': reason,
        'latitude': position?.latitude,
        'longitude': position?.longitude,
      });

      if (response['success'] == true) {
        _activeTimer = _activeTimer?.copyWith(state: 'panic');
        await _saveActiveTimer();
        _isLoading = false;
        notifyListeners();
        return true;
      }

      _errorMessage = response['error'] as String? ?? 'Failed to trigger panic';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = 'Connection error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Fetch current safety status from server
  Future<void> fetchStatus() async {
    try {
      final response = await _apiClient.getSafetyStatus();

      if (response['success'] == true && response['timer'] != null) {
        final timerData = response['timer'] as Map<String, dynamic>;
        _activeTimer = SafetyTimer.fromJson(timerData);
        await _saveActiveTimer();

        if (_activeTimer!.isActive) {
          _startCountdown();
        }
      } else {
        _activeTimer = null;
        await _storageService.setSetting('active_safety_timer', null);
      }
      notifyListeners();
    } catch (e) {
      // Offline - keep local timer state
    }
  }

  @override
  void dispose() {
    _countdownTimer?.cancel();
    super.dispose();
  }
}

