class SyncResponse {
  final bool success;
  final String? error;
  final int syncedCheckins;
  final int syncedPhotos;
  final int syncedSignatures;
  final int syncedNotes;
  final List<SyncFailedItem>? failedItems;
  final String? serverTime;

  SyncResponse({
    required this.success,
    this.error,
    this.syncedCheckins = 0,
    this.syncedPhotos = 0,
    this.syncedSignatures = 0,
    this.syncedNotes = 0,
    this.failedItems,
    this.serverTime,
  });

  factory SyncResponse.fromJson(Map<String, dynamic> json) {
    return SyncResponse(
      success: json['success'] as bool? ?? false,
      error: json['error'] as String?,
      syncedCheckins: json['synced_checkins'] as int? ?? 0,
      syncedPhotos: json['synced_photos'] as int? ?? 0,
      syncedSignatures: json['synced_signatures'] as int? ?? 0,
      syncedNotes: json['synced_notes'] as int? ?? 0,
      failedItems: (json['failed_items'] as List<dynamic>?)
          ?.map((e) => SyncFailedItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      serverTime: json['server_time'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'success': success,
      'error': error,
      'synced_checkins': syncedCheckins,
      'synced_photos': syncedPhotos,
      'synced_signatures': syncedSignatures,
      'synced_notes': syncedNotes,
      'failed_items': failedItems?.map((e) => e.toJson()).toList(),
      'server_time': serverTime,
    };
  }

  int get totalSynced => syncedCheckins + syncedPhotos + syncedSignatures + syncedNotes;
  bool get hasFailures => failedItems != null && failedItems!.isNotEmpty;
}

class SyncFailedItem {
  final String type;
  final String localId;
  final String error;

  SyncFailedItem({
    required this.type,
    required this.localId,
    required this.error,
  });

  factory SyncFailedItem.fromJson(Map<String, dynamic> json) {
    return SyncFailedItem(
      type: json['type'] as String? ?? '',
      localId: json['local_id'] as String? ?? '',
      error: json['error'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type,
      'local_id': localId,
      'error': error,
    };
  }
}

