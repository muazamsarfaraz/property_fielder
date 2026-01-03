import 'job.dart';

class RouteModel {
  final int id;
  final String routeNumber;
  final String name;
  final String routeDate;
  final int inspectorId;
  final String? inspectorName;
  final String? startTime;
  final String? endTime;
  final double? totalDistance;
  final int? totalDuration;
  final int jobCount;
  final int completedCount;
  final String status;
  final List<Job>? jobs;

  RouteModel({
    required this.id,
    required this.routeNumber,
    required this.name,
    required this.routeDate,
    required this.inspectorId,
    this.inspectorName,
    this.startTime,
    this.endTime,
    this.totalDistance,
    this.totalDuration,
    required this.jobCount,
    this.completedCount = 0,
    required this.status,
    this.jobs,
  });

  factory RouteModel.fromJson(Map<String, dynamic> json) {
    return RouteModel(
      id: json['id'] as int,
      routeNumber: json['route_number'] as String? ?? '',
      name: json['name'] as String? ?? '',
      routeDate: json['route_date'] as String? ?? '',
      inspectorId: json['inspector_id'] as int? ?? 0,
      inspectorName: json['inspector_name'] as String?,
      startTime: json['start_time'] as String?,
      endTime: json['end_time'] as String?,
      totalDistance: (json['total_distance'] as num?)?.toDouble(),
      totalDuration: json['total_duration'] as int?,
      jobCount: json['job_count'] as int? ?? 0,
      completedCount: json['completed_count'] as int? ?? 0,
      status: json['status'] as String? ?? 'draft',
      jobs: (json['jobs'] as List<dynamic>?)
          ?.map((e) => Job.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'route_number': routeNumber,
      'name': name,
      'route_date': routeDate,
      'inspector_id': inspectorId,
      'inspector_name': inspectorName,
      'start_time': startTime,
      'end_time': endTime,
      'total_distance': totalDistance,
      'total_duration': totalDuration,
      'job_count': jobCount,
      'completed_count': completedCount,
      'status': status,
      'jobs': jobs?.map((e) => e.toJson()).toList(),
    };
  }

  double get progressPercent {
    if (jobCount == 0) return 0;
    return (completedCount / jobCount) * 100;
  }

  String get statusLabel {
    switch (status) {
      case 'draft':
        return 'Draft';
      case 'planned':
        return 'Planned';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      default:
        return status;
    }
  }

  bool get isCompleted => status == 'completed';
  bool get isInProgress => status == 'in_progress';
}

