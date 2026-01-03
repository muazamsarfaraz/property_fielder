class Note {
  final int? id;
  final String localId;
  final int jobId;
  final int inspectorId;
  final String content;
  final String category;
  final bool isVoiceNote;
  final String? audioPath;
  final String? audioUrl;
  final int? audioDuration;
  final String createdAt;
  final bool synced;

  Note({
    this.id,
    required this.localId,
    required this.jobId,
    required this.inspectorId,
    required this.content,
    required this.category,
    this.isVoiceNote = false,
    this.audioPath,
    this.audioUrl,
    this.audioDuration,
    required this.createdAt,
    this.synced = false,
  });

  factory Note.fromJson(Map<String, dynamic> json) {
    return Note(
      id: json['id'] as int?,
      localId: json['local_id'] as String? ?? '',
      jobId: json['job_id'] as int,
      inspectorId: json['inspector_id'] as int,
      content: json['content'] as String? ?? '',
      category: json['category'] as String? ?? 'general',
      isVoiceNote: json['is_voice_note'] as bool? ?? false,
      audioPath: json['audio_path'] as String?,
      audioUrl: json['audio_url'] as String?,
      audioDuration: json['audio_duration'] as int?,
      createdAt: json['created_at'] as String? ?? '',
      synced: json['synced'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'local_id': localId,
      'job_id': jobId,
      'inspector_id': inspectorId,
      'content': content,
      'category': category,
      'is_voice_note': isVoiceNote,
      'audio_path': audioPath,
      'audio_url': audioUrl,
      'audio_duration': audioDuration,
      'created_at': createdAt,
      'synced': synced,
    };
  }

  Note copyWith({
    int? id,
    String? localId,
    int? jobId,
    int? inspectorId,
    String? content,
    String? category,
    bool? isVoiceNote,
    String? audioPath,
    String? audioUrl,
    int? audioDuration,
    String? createdAt,
    bool? synced,
  }) {
    return Note(
      id: id ?? this.id,
      localId: localId ?? this.localId,
      jobId: jobId ?? this.jobId,
      inspectorId: inspectorId ?? this.inspectorId,
      content: content ?? this.content,
      category: category ?? this.category,
      isVoiceNote: isVoiceNote ?? this.isVoiceNote,
      audioPath: audioPath ?? this.audioPath,
      audioUrl: audioUrl ?? this.audioUrl,
      audioDuration: audioDuration ?? this.audioDuration,
      createdAt: createdAt ?? this.createdAt,
      synced: synced ?? this.synced,
    );
  }

  String get categoryLabel {
    switch (category) {
      case 'general':
        return 'General';
      case 'issue':
        return 'Issue';
      case 'follow_up':
        return 'Follow-up';
      case 'customer':
        return 'Customer';
      case 'internal':
        return 'Internal';
      default:
        return category;
    }
  }
}

