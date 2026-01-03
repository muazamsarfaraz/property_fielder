class Job {
  final int id;
  final String jobNumber;
  final String name;
  final String customerName;
  final String? customerPhone;
  final String? customerEmail;
  final String? address;
  final String? city;
  final String? postcode;
  final String? country;
  final double latitude;
  final double longitude;
  final String? scheduledDate;
  final String? scheduledTime;
  final String? earliestStart;
  final String? latestEnd;
  final int durationMinutes;
  final String priority;
  final String status;
  final List<String> skills;
  final String? notes;
  final int? checkinsCount;
  final int? photosCount;
  final int? signaturesCount;
  final int? notesCount;
  final String? propertyName;
  final String? jobType;
  final int? estimatedDuration;

  Job({
    required this.id,
    required this.jobNumber,
    required this.name,
    required this.customerName,
    this.customerPhone,
    this.customerEmail,
    this.address,
    this.city,
    this.postcode,
    this.country,
    required this.latitude,
    required this.longitude,
    this.scheduledDate,
    this.scheduledTime,
    this.earliestStart,
    this.latestEnd,
    required this.durationMinutes,
    required this.priority,
    required this.status,
    required this.skills,
    this.notes,
    this.checkinsCount,
    this.photosCount,
    this.signaturesCount,
    this.notesCount,
    this.propertyName,
    this.jobType,
    this.estimatedDuration,
  });

  factory Job.fromJson(Map<String, dynamic> json) {
    return Job(
      id: json['id'] as int,
      jobNumber: json['job_number'] as String? ?? '',
      name: json['name'] as String? ?? '',
      customerName: json['customer_name'] as String? ?? '',
      customerPhone: json['customer_phone'] as String?,
      customerEmail: json['customer_email'] as String?,
      address: json['address'] as String?,
      city: json['city'] as String?,
      postcode: json['postcode'] as String?,
      country: json['country'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      scheduledDate: json['scheduled_date'] as String?,
      scheduledTime: json['scheduled_time'] as String?,
      earliestStart: json['earliest_start'] as String?,
      latestEnd: json['latest_end'] as String?,
      durationMinutes: json['duration_minutes'] as int? ?? 60,
      priority: json['priority'] as String? ?? '2',
      status: json['status'] as String? ?? 'pending',
      skills: (json['skills'] as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      notes: json['notes'] as String?,
      checkinsCount: json['checkins'] as int?,
      photosCount: json['photos'] as int?,
      signaturesCount: json['signatures'] as int?,
      notesCount: json['notes_count'] as int?,
      propertyName: json['property_name'] as String?,
      jobType: json['job_type'] as String?,
      estimatedDuration: json['estimated_duration'] as int?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'job_number': jobNumber,
      'name': name,
      'customer_name': customerName,
      'customer_phone': customerPhone,
      'customer_email': customerEmail,
      'address': address,
      'city': city,
      'postcode': postcode,
      'country': country,
      'latitude': latitude,
      'longitude': longitude,
      'scheduled_date': scheduledDate,
      'scheduled_time': scheduledTime,
      'earliest_start': earliestStart,
      'latest_end': latestEnd,
      'duration_minutes': durationMinutes,
      'priority': priority,
      'status': status,
      'skills': skills,
      'notes': notes,
      'checkins': checkinsCount,
      'photos': photosCount,
      'signatures': signaturesCount,
      'notes_count': notesCount,
      'property_name': propertyName,
      'job_type': jobType,
      'estimated_duration': estimatedDuration,
    };
  }

  String get fullAddress {
    final parts = [address, city, postcode, country].where((p) => p != null && p.isNotEmpty);
    return parts.join(', ');
  }

  String get priorityLabel {
    switch (priority) {
      case '1':
        return 'Low';
      case '2':
        return 'Normal';
      case '3':
        return 'High';
      case '4':
        return 'Urgent';
      default:
        return 'Normal';
    }
  }

  String get statusLabel {
    switch (status) {
      case 'draft':
        return 'Draft';
      case 'pending':
        return 'Pending';
      case 'assigned':
        return 'Assigned';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  bool get isCompleted => status == 'completed';
  bool get isInProgress => status == 'in_progress';
  bool get canCheckIn => status == 'assigned' || status == 'pending';
  bool get canCheckOut => status == 'in_progress';
}

