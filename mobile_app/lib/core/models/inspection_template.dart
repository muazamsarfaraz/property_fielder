/// Inspection Template model for structured inspection checklists
class InspectionTemplate {
  final int id;
  final String code;
  final String name;
  final String? description;
  final String version;
  final String? certificationType;
  final int estimatedDuration;
  final bool requiresPhotos;
  final int minPhotos;
  final List<TemplateSection> sections;

  InspectionTemplate({
    required this.id,
    required this.code,
    required this.name,
    this.description,
    required this.version,
    this.certificationType,
    this.estimatedDuration = 60,
    this.requiresPhotos = false,
    this.minPhotos = 0,
    this.sections = const [],
  });

  factory InspectionTemplate.fromJson(Map<String, dynamic> json) {
    return InspectionTemplate(
      id: json['id'] as int,
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      description: json['description'] as String?,
      version: json['version'] as String? ?? '1.0',
      certificationType: json['certification_type'] as String?,
      estimatedDuration: json['estimated_duration'] as int? ?? 60,
      requiresPhotos: json['requires_photos'] as bool? ?? false,
      minPhotos: json['min_photos'] as int? ?? 0,
      sections: (json['sections'] as List<dynamic>?)
          ?.map((e) => TemplateSection.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'name': name,
      'description': description,
      'version': version,
      'certification_type': certificationType,
      'estimated_duration': estimatedDuration,
      'requires_photos': requiresPhotos,
      'min_photos': minPhotos,
      'sections': sections.map((e) => e.toJson()).toList(),
    };
  }

  int get totalItems => sections.fold(0, (sum, s) => sum + s.items.length);
}

/// Template Section - groups related checklist items
class TemplateSection {
  final int id;
  final String code;
  final String name;
  final int sequence;
  final bool isRequired;
  final bool isRepeatable;
  final String? icon;
  final List<TemplateItem> items;

  TemplateSection({
    required this.id,
    required this.code,
    required this.name,
    this.sequence = 0,
    this.isRequired = true,
    this.isRepeatable = false,
    this.icon,
    this.items = const [],
  });

  factory TemplateSection.fromJson(Map<String, dynamic> json) {
    return TemplateSection(
      id: json['id'] as int,
      code: json['code'] as String? ?? '',
      name: json['name'] as String? ?? '',
      sequence: json['sequence'] as int? ?? 0,
      isRequired: json['is_required'] as bool? ?? true,
      isRepeatable: json['is_repeatable'] as bool? ?? false,
      icon: json['icon'] as String?,
      items: (json['items'] as List<dynamic>?)
          ?.map((e) => TemplateItem.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'name': name,
      'sequence': sequence,
      'is_required': isRequired,
      'is_repeatable': isRepeatable,
      'icon': icon,
      'items': items.map((e) => e.toJson()).toList(),
    };
  }
}

/// Template Item - individual checklist question
class TemplateItem {
  final int id;
  final String code;
  final String question;
  final int sequence;
  final String responseType; // yes_no, severity, numeric, text, photo, reading
  final bool isMandatory;
  final bool requiresPhoto;
  final String? helpText;
  final String? defectTriggerValue;
  final int? parentItemId;
  final String? showWhenParentValue;

  TemplateItem({
    required this.id,
    required this.code,
    required this.question,
    this.sequence = 0,
    this.responseType = 'yes_no',
    this.isMandatory = false,
    this.requiresPhoto = false,
    this.helpText,
    this.defectTriggerValue,
    this.parentItemId,
    this.showWhenParentValue,
  });

  factory TemplateItem.fromJson(Map<String, dynamic> json) {
    return TemplateItem(
      id: json['id'] as int,
      code: json['code'] as String? ?? '',
      question: json['question'] as String? ?? '',
      sequence: json['sequence'] as int? ?? 0,
      responseType: json['response_type'] as String? ?? 'yes_no',
      isMandatory: json['is_mandatory'] as bool? ?? false,
      requiresPhoto: json['requires_photo'] as bool? ?? false,
      helpText: json['help_text'] as String?,
      defectTriggerValue: json['defect_trigger_value'] as String?,
      parentItemId: json['parent_item_id'] as int?,
      showWhenParentValue: json['show_when_parent_value'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'code': code,
      'question': question,
      'sequence': sequence,
      'response_type': responseType,
      'is_mandatory': isMandatory,
      'requires_photo': requiresPhoto,
      'help_text': helpText,
      'defect_trigger_value': defectTriggerValue,
      'parent_item_id': parentItemId,
      'show_when_parent_value': showWhenParentValue,
    };
  }

  bool get isConditional => parentItemId != null;
}

