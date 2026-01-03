class Checkin {
  final int? id;
  final int jobId;
  final int inspectorId;
  final String checkinTime;
  final double? checkinLatitude;
  final double? checkinLongitude;
  final double? checkinAccuracy;
  final String? checkinNotes;
  final String? checkoutTime;
  final double? checkoutLatitude;
  final double? checkoutLongitude;
  final String? checkoutNotes;
  final int? durationMinutes;
  final String status;
  final String? deviceInfo;
  final bool synced;

  Checkin({
    this.id,
    required this.jobId,
    required this.inspectorId,
    required this.checkinTime,
    this.checkinLatitude,
    this.checkinLongitude,
    this.checkinAccuracy,
    this.checkinNotes,
    this.checkoutTime,
    this.checkoutLatitude,
    this.checkoutLongitude,
    this.checkoutNotes,
    this.durationMinutes,
    required this.status,
    this.deviceInfo,
    this.synced = false,
  });

  factory Checkin.fromJson(Map<String, dynamic> json) {
    return Checkin(
      id: json['id'] as int?,
      jobId: json['job_id'] as int,
      inspectorId: json['inspector_id'] as int,
      checkinTime: json['checkin_time'] as String,
      checkinLatitude: (json['checkin_latitude'] as num?)?.toDouble(),
      checkinLongitude: (json['checkin_longitude'] as num?)?.toDouble(),
      checkinAccuracy: (json['checkin_accuracy'] as num?)?.toDouble(),
      checkinNotes: json['checkin_notes'] as String?,
      checkoutTime: json['checkout_time'] as String?,
      checkoutLatitude: (json['checkout_latitude'] as num?)?.toDouble(),
      checkoutLongitude: (json['checkout_longitude'] as num?)?.toDouble(),
      checkoutNotes: json['checkout_notes'] as String?,
      durationMinutes: json['duration_minutes'] as int?,
      status: json['status'] as String? ?? 'active',
      deviceInfo: json['device_info'] as String?,
      synced: json['synced'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'job_id': jobId,
      'inspector_id': inspectorId,
      'checkin_time': checkinTime,
      'checkin_latitude': checkinLatitude,
      'checkin_longitude': checkinLongitude,
      'checkin_accuracy': checkinAccuracy,
      'checkin_notes': checkinNotes,
      'checkout_time': checkoutTime,
      'checkout_latitude': checkoutLatitude,
      'checkout_longitude': checkoutLongitude,
      'checkout_notes': checkoutNotes,
      'duration_minutes': durationMinutes,
      'status': status,
      'device_info': deviceInfo,
      'synced': synced,
    };
  }

  Checkin copyWith({
    int? id,
    int? jobId,
    int? inspectorId,
    String? checkinTime,
    double? checkinLatitude,
    double? checkinLongitude,
    double? checkinAccuracy,
    String? checkinNotes,
    String? checkoutTime,
    double? checkoutLatitude,
    double? checkoutLongitude,
    String? checkoutNotes,
    int? durationMinutes,
    String? status,
    String? deviceInfo,
    bool? synced,
  }) {
    return Checkin(
      id: id ?? this.id,
      jobId: jobId ?? this.jobId,
      inspectorId: inspectorId ?? this.inspectorId,
      checkinTime: checkinTime ?? this.checkinTime,
      checkinLatitude: checkinLatitude ?? this.checkinLatitude,
      checkinLongitude: checkinLongitude ?? this.checkinLongitude,
      checkinAccuracy: checkinAccuracy ?? this.checkinAccuracy,
      checkinNotes: checkinNotes ?? this.checkinNotes,
      checkoutTime: checkoutTime ?? this.checkoutTime,
      checkoutLatitude: checkoutLatitude ?? this.checkoutLatitude,
      checkoutLongitude: checkoutLongitude ?? this.checkoutLongitude,
      checkoutNotes: checkoutNotes ?? this.checkoutNotes,
      durationMinutes: durationMinutes ?? this.durationMinutes,
      status: status ?? this.status,
      deviceInfo: deviceInfo ?? this.deviceInfo,
      synced: synced ?? this.synced,
    );
  }
}

