class Photo {
  final int? id;
  final String localId;
  final int jobId;
  final int inspectorId;
  final String localPath;
  final String? remoteUrl;
  final String? caption;
  final String category;
  final double? latitude;
  final double? longitude;
  final String takenAt;
  final bool synced;
  final int? fileSize;
  final String? mimeType;

  Photo({
    this.id,
    required this.localId,
    required this.jobId,
    required this.inspectorId,
    required this.localPath,
    this.remoteUrl,
    this.caption,
    required this.category,
    this.latitude,
    this.longitude,
    required this.takenAt,
    this.synced = false,
    this.fileSize,
    this.mimeType,
  });

  factory Photo.fromJson(Map<String, dynamic> json) {
    return Photo(
      id: json['id'] as int?,
      localId: json['local_id'] as String? ?? '',
      jobId: json['job_id'] as int,
      inspectorId: json['inspector_id'] as int,
      localPath: json['local_path'] as String? ?? '',
      remoteUrl: json['remote_url'] as String?,
      caption: json['caption'] as String?,
      category: json['category'] as String? ?? 'general',
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      takenAt: json['taken_at'] as String? ?? '',
      synced: json['synced'] as bool? ?? false,
      fileSize: json['file_size'] as int?,
      mimeType: json['mime_type'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'local_id': localId,
      'job_id': jobId,
      'inspector_id': inspectorId,
      'local_path': localPath,
      'remote_url': remoteUrl,
      'caption': caption,
      'category': category,
      'latitude': latitude,
      'longitude': longitude,
      'taken_at': takenAt,
      'synced': synced,
      'file_size': fileSize,
      'mime_type': mimeType,
    };
  }

  Photo copyWith({
    int? id,
    String? localId,
    int? jobId,
    int? inspectorId,
    String? localPath,
    String? remoteUrl,
    String? caption,
    String? category,
    double? latitude,
    double? longitude,
    String? takenAt,
    bool? synced,
    int? fileSize,
    String? mimeType,
  }) {
    return Photo(
      id: id ?? this.id,
      localId: localId ?? this.localId,
      jobId: jobId ?? this.jobId,
      inspectorId: inspectorId ?? this.inspectorId,
      localPath: localPath ?? this.localPath,
      remoteUrl: remoteUrl ?? this.remoteUrl,
      caption: caption ?? this.caption,
      category: category ?? this.category,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      takenAt: takenAt ?? this.takenAt,
      synced: synced ?? this.synced,
      fileSize: fileSize ?? this.fileSize,
      mimeType: mimeType ?? this.mimeType,
    );
  }

  String get categoryLabel {
    switch (category) {
      case 'before':
        return 'Before';
      case 'during':
        return 'During';
      case 'after':
        return 'After';
      case 'issue':
        return 'Issue';
      case 'document':
        return 'Document';
      default:
        return category;
    }
  }
}

