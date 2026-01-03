/// Inspection Response - captures answers to template items
class InspectionResponse {
  final String localId;
  final int? serverId;
  final int inspectionId;
  final int templateItemId;
  final int sectionId;
  final String? value; // The response value
  final double? numericValue;
  final String? notes;
  final List<String>? photoIds;
  final bool hasDefect;
  final String? defectSeverity;
  final String respondedAt;
  final bool synced;

  InspectionResponse({
    required this.localId,
    this.serverId,
    required this.inspectionId,
    required this.templateItemId,
    required this.sectionId,
    this.value,
    this.numericValue,
    this.notes,
    this.photoIds,
    this.hasDefect = false,
    this.defectSeverity,
    required this.respondedAt,
    this.synced = false,
  });

  factory InspectionResponse.fromJson(Map<String, dynamic> json) {
    return InspectionResponse(
      localId: json['local_id'] as String? ?? '',
      serverId: json['server_id'] as int?,
      inspectionId: json['inspection_id'] as int,
      templateItemId: json['template_item_id'] as int,
      sectionId: json['section_id'] as int,
      value: json['value'] as String?,
      numericValue: (json['numeric_value'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      photoIds: (json['photo_ids'] as List<dynamic>?)?.map((e) => e as String).toList(),
      hasDefect: json['has_defect'] as bool? ?? false,
      defectSeverity: json['defect_severity'] as String?,
      respondedAt: json['responded_at'] as String? ?? '',
      synced: json['synced'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'local_id': localId,
      'server_id': serverId,
      'inspection_id': inspectionId,
      'template_item_id': templateItemId,
      'section_id': sectionId,
      'value': value,
      'numeric_value': numericValue,
      'notes': notes,
      'photo_ids': photoIds,
      'has_defect': hasDefect,
      'defect_severity': defectSeverity,
      'responded_at': respondedAt,
      'synced': synced,
    };
  }

  InspectionResponse copyWith({
    String? localId,
    int? serverId,
    int? inspectionId,
    int? templateItemId,
    int? sectionId,
    String? value,
    double? numericValue,
    String? notes,
    List<String>? photoIds,
    bool? hasDefect,
    String? defectSeverity,
    String? respondedAt,
    bool? synced,
  }) {
    return InspectionResponse(
      localId: localId ?? this.localId,
      serverId: serverId ?? this.serverId,
      inspectionId: inspectionId ?? this.inspectionId,
      templateItemId: templateItemId ?? this.templateItemId,
      sectionId: sectionId ?? this.sectionId,
      value: value ?? this.value,
      numericValue: numericValue ?? this.numericValue,
      notes: notes ?? this.notes,
      photoIds: photoIds ?? this.photoIds,
      hasDefect: hasDefect ?? this.hasDefect,
      defectSeverity: defectSeverity ?? this.defectSeverity,
      respondedAt: respondedAt ?? this.respondedAt,
      synced: synced ?? this.synced,
    );
  }
}

/// Active Inspection - tracks current inspection execution
class ActiveInspection {
  final int id;
  final int jobId;
  final int templateId;
  final int propertyId;
  final int inspectorId;
  final String state; // draft, in_progress, completed
  final String? startedAt;
  final String? completedAt;
  final String? overallResult; // pass, fail, conditional, incomplete
  final double completionPercentage;

  ActiveInspection({
    required this.id,
    required this.jobId,
    required this.templateId,
    required this.propertyId,
    required this.inspectorId,
    this.state = 'draft',
    this.startedAt,
    this.completedAt,
    this.overallResult,
    this.completionPercentage = 0.0,
  });

  factory ActiveInspection.fromJson(Map<String, dynamic> json) {
    return ActiveInspection(
      id: json['id'] as int,
      jobId: json['job_id'] as int,
      templateId: json['template_id'] as int,
      propertyId: json['property_id'] as int,
      inspectorId: json['inspector_id'] as int,
      state: json['state'] as String? ?? 'draft',
      startedAt: json['started_at'] as String?,
      completedAt: json['completed_at'] as String?,
      overallResult: json['overall_result'] as String?,
      completionPercentage: (json['completion_percentage'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'job_id': jobId,
      'template_id': templateId,
      'property_id': propertyId,
      'inspector_id': inspectorId,
      'state': state,
      'started_at': startedAt,
      'completed_at': completedAt,
      'overall_result': overallResult,
      'completion_percentage': completionPercentage,
    };
  }

  bool get isComplete => state == 'completed';
  bool get isInProgress => state == 'in_progress';
}

