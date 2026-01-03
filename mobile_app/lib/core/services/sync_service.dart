import 'dart:convert';
import 'dart:io';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../api/api_client.dart';
import '../models/sync_response.dart';
import 'storage_service.dart';

/// Service for syncing offline data with the server
class SyncService {
  final ApiClient _apiClient;
  final StorageService _storageService;
  final Connectivity _connectivity;

  bool _isSyncing = false;
  DateTime? _lastSyncTime;

  SyncService({
    required ApiClient apiClient,
    required StorageService storageService,
    Connectivity? connectivity,
  })  : _apiClient = apiClient,
        _storageService = storageService,
        _connectivity = connectivity ?? Connectivity();

  bool get isSyncing => _isSyncing;
  DateTime? get lastSyncTime => _lastSyncTime;
  int get pendingCount => _storageService.unsyncedCount;
  bool get hasPendingData => _storageService.hasUnsyncedData;

  /// Check if device has network connectivity
  Future<bool> hasConnectivity() async {
    final result = await _connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }

  /// Sync all pending data with the server
  Future<SyncResult> syncAll() async {
    if (_isSyncing) {
      return SyncResult(success: false, message: 'Sync already in progress');
    }

    if (!await hasConnectivity()) {
      return SyncResult(success: false, message: 'No network connectivity');
    }

    _isSyncing = true;
    final result = SyncResult(success: true);

    try {
      // Sync checkins
      final checkins = _storageService.getUnsyncedCheckins();
      for (final checkin in checkins) {
        try {
          final response = await _apiClient.checkin(
            checkin.jobId,
            checkin.toJson(),
          );
          if (response['success'] == true && response['id'] != null) {
            await _storageService.markCheckinSynced(
              'local_${checkin.jobId}_${checkin.checkinTime}',
              response['id'],
            );
            result.syncedCheckins++;
          }
        } catch (e) {
          result.failedCheckins++;
          result.errors.add('Checkin sync failed: $e');
        }
      }

      // Sync photos
      final photos = _storageService.getUnsyncedPhotos();
      for (final photo in photos) {
        try {
          final file = File(photo.localPath);
          if (await file.exists()) {
            final bytes = await file.readAsBytes();
            final base64Image = base64Encode(bytes);
            
            final response = await _apiClient.uploadPhoto(
              photo.jobId,
              {
                ...photo.toJson(),
                'image_data': base64Image,
              },
            );
            
            if (response['success'] == true && response['id'] != null) {
              await _storageService.markPhotoSynced(
                photo.localId,
                response['id'],
                response['url'] ?? '',
              );
              result.syncedPhotos++;
            }
          }
        } catch (e) {
          result.failedPhotos++;
          result.errors.add('Photo sync failed: $e');
        }
      }

      // Sync signatures
      final signatures = _storageService.getUnsyncedSignatures();
      for (final signature in signatures) {
        try {
          final file = File(signature.localPath);
          String? signatureData = signature.signatureData;
          
          if (signatureData == null && await file.exists()) {
            final bytes = await file.readAsBytes();
            signatureData = base64Encode(bytes);
          }
          
          final response = await _apiClient.captureSignature(
            signature.jobId,
            {
              ...signature.toJson(),
              'signature_data': signatureData,
            },
          );
          
          if (response['success'] == true && response['id'] != null) {
            await _storageService.markSignatureSynced(
              signature.localId,
              response['id'],
            );
            result.syncedSignatures++;
          }
        } catch (e) {
          result.failedSignatures++;
          result.errors.add('Signature sync failed: $e');
        }
      }

      // Sync notes
      final notes = _storageService.getUnsyncedNotes();
      for (final note in notes) {
        try {
          final response = await _apiClient.addNote(
            note.jobId,
            note.toJson(),
          );
          
          if (response['success'] == true && response['id'] != null) {
            await _storageService.markNoteSynced(
              note.localId,
              response['id'],
            );
            result.syncedNotes++;
          }
        } catch (e) {
          result.failedNotes++;
          result.errors.add('Note sync failed: $e');
        }
      }

      _lastSyncTime = DateTime.now();
      result.message = 'Sync completed';
    } catch (e) {
      result.success = false;
      result.message = 'Sync failed: $e';
    } finally {
      _isSyncing = false;
    }

    return result;
  }

  /// Sync in background (called by WorkManager)
  Future<void> syncInBackground() async {
    if (!await hasConnectivity()) return;
    await syncAll();
  }

  /// Refresh jobs from server
  Future<void> refreshJobs({String? date}) async {
    if (!await hasConnectivity()) return;

    try {
      final response = await _apiClient.getMyJobs(date: date);
      if (response.success) {
        await _storageService.saveJobs(response.jobs);
      }
    } catch (e) {
      // Silently fail - use cached data
    }
  }

  /// Refresh routes from server
  Future<void> refreshRoutes({String? date}) async {
    if (!await hasConnectivity()) return;

    try {
      final response = await _apiClient.getMyRoutes(date: date);
      if (response.success) {
        await _storageService.saveRoutes(response.routes);
      }
    } catch (e) {
      // Silently fail - use cached data
    }
  }
}

/// Result of a sync operation
class SyncResult {
  bool success;
  String message;
  int syncedCheckins;
  int syncedPhotos;
  int syncedSignatures;
  int syncedNotes;
  int failedCheckins;
  int failedPhotos;
  int failedSignatures;
  int failedNotes;
  List<String> errors;

  SyncResult({
    this.success = true,
    this.message = '',
    this.syncedCheckins = 0,
    this.syncedPhotos = 0,
    this.syncedSignatures = 0,
    this.syncedNotes = 0,
    this.failedCheckins = 0,
    this.failedPhotos = 0,
    this.failedSignatures = 0,
    this.failedNotes = 0,
    List<String>? errors,
  }) : errors = errors ?? [];

  int get totalSynced => syncedCheckins + syncedPhotos + syncedSignatures + syncedNotes;
  int get totalFailed => failedCheckins + failedPhotos + failedSignatures + failedNotes;
  bool get hasErrors => errors.isNotEmpty;
}

