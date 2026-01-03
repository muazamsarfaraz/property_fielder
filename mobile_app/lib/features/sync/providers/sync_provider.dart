import 'package:flutter/foundation.dart';
import '../../../core/services/sync_service.dart';
import '../../../core/services/storage_service.dart';

class SyncProvider extends ChangeNotifier {
  final SyncService _syncService;
  final StorageService _storageService;

  bool _isSyncing = false;
  SyncResult? _lastResult;
  String? _errorMessage;

  SyncProvider({
    required SyncService syncService,
    required StorageService storageService,
  })  : _syncService = syncService,
        _storageService = storageService;

  bool get isSyncing => _isSyncing;
  SyncResult? get lastResult => _lastResult;
  String? get errorMessage => _errorMessage;
  int get pendingCount => _storageService.unsyncedCount;
  bool get hasPendingData => _storageService.hasUnsyncedData;
  DateTime? get lastSyncTime => _syncService.lastSyncTime;

  Future<void> syncAll() async {
    if (_isSyncing) return;

    _isSyncing = true;
    _errorMessage = null;
    notifyListeners();

    try {
      _lastResult = await _syncService.syncAll();
      if (!_lastResult!.success) {
        _errorMessage = _lastResult!.message;
      }
    } catch (e) {
      _errorMessage = 'Sync failed: $e';
    } finally {
      _isSyncing = false;
      notifyListeners();
    }
  }

  Future<void> refreshData() async {
    _isSyncing = true;
    notifyListeners();

    try {
      await _syncService.refreshJobs();
      await _syncService.refreshRoutes();
    } catch (e) {
      _errorMessage = 'Refresh failed: $e';
    } finally {
      _isSyncing = false;
      notifyListeners();
    }
  }

  String get syncStatusText {
    if (_isSyncing) return 'Syncing...';
    if (hasPendingData) return '$pendingCount items pending';
    return 'All synced';
  }
}

