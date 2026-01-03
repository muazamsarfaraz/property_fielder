class Signature {
  final int? id;
  final String localId;
  final int jobId;
  final int inspectorId;
  final String signerName;
  final String? signerRole;
  final String? signerEmail;
  final String localPath;
  final String? remoteUrl;
  final String? signatureData;
  final String signedAt;
  final double? latitude;
  final double? longitude;
  final bool synced;

  Signature({
    this.id,
    required this.localId,
    required this.jobId,
    required this.inspectorId,
    required this.signerName,
    this.signerRole,
    this.signerEmail,
    required this.localPath,
    this.remoteUrl,
    this.signatureData,
    required this.signedAt,
    this.latitude,
    this.longitude,
    this.synced = false,
  });

  factory Signature.fromJson(Map<String, dynamic> json) {
    return Signature(
      id: json['id'] as int?,
      localId: json['local_id'] as String? ?? '',
      jobId: json['job_id'] as int,
      inspectorId: json['inspector_id'] as int,
      signerName: json['signer_name'] as String? ?? '',
      signerRole: json['signer_role'] as String?,
      signerEmail: json['signer_email'] as String?,
      localPath: json['local_path'] as String? ?? '',
      remoteUrl: json['remote_url'] as String?,
      signatureData: json['signature_data'] as String?,
      signedAt: json['signed_at'] as String? ?? '',
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      synced: json['synced'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'local_id': localId,
      'job_id': jobId,
      'inspector_id': inspectorId,
      'signer_name': signerName,
      'signer_role': signerRole,
      'signer_email': signerEmail,
      'local_path': localPath,
      'remote_url': remoteUrl,
      'signature_data': signatureData,
      'signed_at': signedAt,
      'latitude': latitude,
      'longitude': longitude,
      'synced': synced,
    };
  }

  Signature copyWith({
    int? id,
    String? localId,
    int? jobId,
    int? inspectorId,
    String? signerName,
    String? signerRole,
    String? signerEmail,
    String? localPath,
    String? remoteUrl,
    String? signatureData,
    String? signedAt,
    double? latitude,
    double? longitude,
    bool? synced,
  }) {
    return Signature(
      id: id ?? this.id,
      localId: localId ?? this.localId,
      jobId: jobId ?? this.jobId,
      inspectorId: inspectorId ?? this.inspectorId,
      signerName: signerName ?? this.signerName,
      signerRole: signerRole ?? this.signerRole,
      signerEmail: signerEmail ?? this.signerEmail,
      localPath: localPath ?? this.localPath,
      remoteUrl: remoteUrl ?? this.remoteUrl,
      signatureData: signatureData ?? this.signatureData,
      signedAt: signedAt ?? this.signedAt,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      synced: synced ?? this.synced,
    );
  }
}

