import 'package:hive/hive.dart';

/// Safety Timer model for Lone Worker Protection (HSE Compliance)
///
/// Tracks active safety timer state locally for:
/// - Countdown display even when offline
/// - Timer persistence across app restarts
/// - Panic button GPS location
class SafetyTimer {
  final int? id;
  final int inspectorId;
  final int? jobId;
  final String startedAt;
  final String expectedEnd;
  final int extendedCount;
  final String state; // active, completed, overdue, escalated, panic
  final double? lastKnownLat;
  final double? lastKnownLong;
  final int minutesRemaining;
  final bool isOverdue;

  SafetyTimer({
    this.id,
    required this.inspectorId,
    this.jobId,
    required this.startedAt,
    required this.expectedEnd,
    this.extendedCount = 0,
    required this.state,
    this.lastKnownLat,
    this.lastKnownLong,
    this.minutesRemaining = 0,
    this.isOverdue = false,
  });

  factory SafetyTimer.fromJson(Map<String, dynamic> json) {
    return SafetyTimer(
      id: json['id'] as int?,
      inspectorId: json['inspector_id'] as int,
      jobId: json['job_id'] as int?,
      startedAt: json['started_at'] as String? ?? '',
      expectedEnd: json['expected_end'] as String? ?? '',
      extendedCount: json['extended_count'] as int? ?? 0,
      state: json['state'] as String? ?? 'active',
      lastKnownLat: (json['last_known_lat'] as num?)?.toDouble(),
      lastKnownLong: (json['last_known_long'] as num?)?.toDouble(),
      minutesRemaining: json['minutes_remaining'] as int? ?? 0,
      isOverdue: json['is_overdue'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'inspector_id': inspectorId,
      'job_id': jobId,
      'started_at': startedAt,
      'expected_end': expectedEnd,
      'extended_count': extendedCount,
      'state': state,
      'last_known_lat': lastKnownLat,
      'last_known_long': lastKnownLong,
      'minutes_remaining': minutesRemaining,
      'is_overdue': isOverdue,
    };
  }

  /// Calculate remaining time from expected_end
  Duration get remainingDuration {
    final end = DateTime.parse(expectedEnd);
    final now = DateTime.now();
    final diff = end.difference(now);
    return diff.isNegative ? Duration.zero : diff;
  }

  /// Check if timer is currently active
  bool get isActive => state == 'active';

  /// Check if timer can be extended
  bool get canExtend => state == 'active' || state == 'overdue';

  /// Check if timer is in panic state
  bool get isPanic => state == 'panic';

  /// Get formatted remaining time (MM:SS or HH:MM:SS)
  String get formattedRemaining {
    final duration = remainingDuration;
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);
    final seconds = duration.inSeconds.remainder(60);

    if (hours > 0) {
      return '${hours.toString().padLeft(2, '0')}:${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
    }
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }

  /// Create a copy with updated fields
  SafetyTimer copyWith({
    int? id,
    int? inspectorId,
    int? jobId,
    String? startedAt,
    String? expectedEnd,
    int? extendedCount,
    String? state,
    double? lastKnownLat,
    double? lastKnownLong,
    int? minutesRemaining,
    bool? isOverdue,
  }) {
    return SafetyTimer(
      id: id ?? this.id,
      inspectorId: inspectorId ?? this.inspectorId,
      jobId: jobId ?? this.jobId,
      startedAt: startedAt ?? this.startedAt,
      expectedEnd: expectedEnd ?? this.expectedEnd,
      extendedCount: extendedCount ?? this.extendedCount,
      state: state ?? this.state,
      lastKnownLat: lastKnownLat ?? this.lastKnownLat,
      lastKnownLong: lastKnownLong ?? this.lastKnownLong,
      minutesRemaining: minutesRemaining ?? this.minutesRemaining,
      isOverdue: isOverdue ?? this.isOverdue,
    );
  }
}

class SafetyTimerAdapter extends TypeAdapter<SafetyTimer> {
  @override
  final int typeId = 10;

  @override
  SafetyTimer read(BinaryReader reader) {
    final numOfFields = reader.readByte();
    final fields = <int, dynamic>{
      for (int i = 0; i < numOfFields; i++) reader.readByte(): reader.read(),
    };
    return SafetyTimer(
      id: fields[0] as int?,
      inspectorId: fields[1] as int,
      jobId: fields[2] as int?,
      startedAt: fields[3] as String,
      expectedEnd: fields[4] as String,
      extendedCount: fields[5] as int? ?? 0,
      state: fields[6] as String,
      lastKnownLat: fields[7] as double?,
      lastKnownLong: fields[8] as double?,
      minutesRemaining: fields[9] as int? ?? 0,
      isOverdue: fields[10] as bool? ?? false,
    );
  }

  @override
  void write(BinaryWriter writer, SafetyTimer obj) {
    writer
      ..writeByte(11)
      ..writeByte(0)..write(obj.id)
      ..writeByte(1)..write(obj.inspectorId)
      ..writeByte(2)..write(obj.jobId)
      ..writeByte(3)..write(obj.startedAt)
      ..writeByte(4)..write(obj.expectedEnd)
      ..writeByte(5)..write(obj.extendedCount)
      ..writeByte(6)..write(obj.state)
      ..writeByte(7)..write(obj.lastKnownLat)
      ..writeByte(8)..write(obj.lastKnownLong)
      ..writeByte(9)..write(obj.minutesRemaining)
      ..writeByte(10)..write(obj.isOverdue);
  }

  @override
  int get hashCode => typeId.hashCode;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is SafetyTimerAdapter &&
          runtimeType == other.runtimeType &&
          typeId == other.typeId;
}

