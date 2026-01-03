import 'package:dio/dio.dart';
import '../models/job.dart';
import '../models/route.dart';
import '../models/sync_response.dart';

class ApiClient {
  final Dio _dio;
  final String baseUrl;
  int _requestId = 0;

  ApiClient(this._dio, {this.baseUrl = ''});

  /// Wraps params in JSON-RPC 2.0 format required by Odoo
  Map<String, dynamic> _jsonRpc(Map<String, dynamic> params) {
    return {
      'jsonrpc': '2.0',
      'method': 'call',
      'params': params,
      'id': ++_requestId,
    };
  }

  /// Extract result from JSON-RPC response
  Map<String, dynamic> _unwrapResponse(Map<String, dynamic> data) {
    if (data.containsKey('result')) {
      return data['result'] as Map<String, dynamic>;
    } else if (data.containsKey('error')) {
      final error = data['error'];
      final message = error is Map ? (error['message'] ?? error['data']?['message'] ?? 'Unknown error') : 'Unknown error';
      return {'success': false, 'error': message};
    }
    return data;
  }

  // Authentication
  Future<Map<String, dynamic>> login(Map<String, dynamic> credentials) async {
    final response = await _dio.post('$baseUrl/mobile/api/auth/login', data: _jsonRpc(credentials));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  // Jobs
  Future<JobListResponse> getMyJobs({String? date, String? status}) async {
    final queryParams = <String, dynamic>{};
    if (date != null) queryParams['date'] = date;
    if (status != null) queryParams['status'] = status;

    final response = await _dio.get(
      '$baseUrl/mobile/api/jobs/my',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );
    return JobListResponse.fromJson(response.data as Map<String, dynamic>);
  }

  Future<JobDetailResponse> getJobDetail(int id) async {
    final response = await _dio.get('$baseUrl/mobile/api/jobs/$id');
    return JobDetailResponse.fromJson(response.data as Map<String, dynamic>);
  }

  // Check-In/Out
  Future<Map<String, dynamic>> checkin(int jobId, Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/jobs/$jobId/checkin', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> checkout(int jobId, Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/jobs/$jobId/checkout', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  // Photos
  Future<Map<String, dynamic>> uploadPhoto(int jobId, Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/jobs/$jobId/photos', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  // Signatures
  Future<Map<String, dynamic>> captureSignature(int jobId, Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/jobs/$jobId/signature', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  // Notes
  Future<Map<String, dynamic>> addNote(int jobId, Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/jobs/$jobId/notes', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  // Routes
  Future<RouteListResponse> getMyRoutes({String? date}) async {
    final queryParams = <String, dynamic>{};
    if (date != null) queryParams['date'] = date;

    final response = await _dio.get(
      '$baseUrl/mobile/api/routes/my',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );
    return RouteListResponse.fromJson(response.data as Map<String, dynamic>);
  }

  // Sync
  Future<SyncResponse> sync(Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/sync', data: _jsonRpc(data));
    final unwrapped = _unwrapResponse(response.data as Map<String, dynamic>);
    return SyncResponse.fromJson(unwrapped);
  }

  // Safety Timer (Lone Worker Protection)
  Future<Map<String, dynamic>> startSafetyTimer(Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/safety/timer/start', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> extendSafetyTimer(Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/safety/timer/extend', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> cancelSafetyTimer(Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/safety/timer/cancel', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> getSafetyStatus() async {
    final response = await _dio.get('$baseUrl/mobile/api/safety/status');
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> triggerPanic(Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/safety/panic', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  // Inspection Templates
  Future<Map<String, dynamic>> getTemplates() async {
    final response = await _dio.get('$baseUrl/mobile/api/templates');
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> getTemplateDetail(int id) async {
    final response = await _dio.get('$baseUrl/mobile/api/templates/$id');
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> submitResponses(int inspectionId, Map<String, dynamic> data) async {
    final response = await _dio.post('$baseUrl/mobile/api/inspections/$inspectionId/responses', data: _jsonRpc(data));
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }

  Future<Map<String, dynamic>> getJobInspection(int jobId) async {
    final response = await _dio.get('$baseUrl/mobile/api/jobs/$jobId/inspection');
    return _unwrapResponse(response.data as Map<String, dynamic>);
  }
}

// Response models
class JobListResponse {
  final bool success;
  final List<Job> jobs;
  final String? error;

  JobListResponse({
    required this.success,
    required this.jobs,
    this.error,
  });

  factory JobListResponse.fromJson(Map<String, dynamic> json) {
    return JobListResponse(
      success: json['success'] ?? false,
      jobs: json['jobs'] != null
          ? (json['jobs'] as List).map((j) => Job.fromJson(j)).toList()
          : [],
      error: json['error'],
    );
  }
}

class JobDetailResponse {
  final bool success;
  final Job? job;
  final String? error;

  JobDetailResponse({
    required this.success,
    this.job,
    this.error,
  });

  factory JobDetailResponse.fromJson(Map<String, dynamic> json) {
    return JobDetailResponse(
      success: json['success'] ?? false,
      job: json['job'] != null ? Job.fromJson(json['job']) : null,
      error: json['error'],
    );
  }
}

class RouteListResponse {
  final bool success;
  final List<RouteModel> routes;
  final String? error;

  RouteListResponse({
    required this.success,
    required this.routes,
    this.error,
  });

  factory RouteListResponse.fromJson(Map<String, dynamic> json) {
    return RouteListResponse(
      success: json['success'] ?? false,
      routes: json['routes'] != null
          ? (json['routes'] as List).map((r) => RouteModel.fromJson(r)).toList()
          : [],
      error: json['error'],
    );
  }
}

