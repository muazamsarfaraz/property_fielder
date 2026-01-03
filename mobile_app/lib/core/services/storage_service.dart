import 'dart:convert';
import 'package:hive_flutter/hive_flutter.dart';
import '../models/job.dart';
import '../models/route.dart';
import '../models/checkin.dart';
import '../models/photo.dart';
import '../models/signature.dart';
import '../models/note.dart';

/// Service for managing offline data storage using Hive with JSON serialization
class StorageService {
  static const String _jobsBox = 'jobs_json';
  static const String _routesBox = 'routes_json';
  static const String _checkinsBox = 'checkins_json';
  static const String _photosBox = 'photos_json';
  static const String _signaturesBox = 'signatures_json';
  static const String _notesBox = 'notes_json';
  static const String _settingsBox = 'settings';

  late Box<String> _jobs;
  late Box<String> _routes;
  late Box<String> _checkins;
  late Box<String> _photos;
  late Box<String> _signatures;
  late Box<String> _notes;
  late Box _settings;

  bool _initialized = false;

  /// Initialize Hive boxes (no adapters needed - using JSON)
  Future<void> init() async {
    if (_initialized) return;

    // Open boxes with String type for JSON storage
    _jobs = await Hive.openBox<String>(_jobsBox);
    _routes = await Hive.openBox<String>(_routesBox);
    _checkins = await Hive.openBox<String>(_checkinsBox);
    _photos = await Hive.openBox<String>(_photosBox);
    _signatures = await Hive.openBox<String>(_signaturesBox);
    _notes = await Hive.openBox<String>(_notesBox);
    _settings = await Hive.openBox(_settingsBox);

    _initialized = true;
  }

  // Jobs
  Future<void> saveJobs(List<Job> jobs) async {
    await _jobs.clear();
    for (final job in jobs) {
      await _jobs.put(job.id.toString(), jsonEncode(job.toJson()));
    }
  }

  List<Job> getJobs() => _jobs.values
      .map((json) => Job.fromJson(jsonDecode(json) as Map<String, dynamic>))
      .toList();

  Job? getJob(int id) {
    final json = _jobs.get(id.toString());
    if (json == null) return null;
    return Job.fromJson(jsonDecode(json) as Map<String, dynamic>);
  }

  Future<void> saveJob(Job job) async =>
      await _jobs.put(job.id.toString(), jsonEncode(job.toJson()));

  // Routes
  Future<void> saveRoutes(List<RouteModel> routes) async {
    await _routes.clear();
    for (final route in routes) {
      await _routes.put(route.id.toString(), jsonEncode(route.toJson()));
    }
  }

  List<RouteModel> getRoutes() => _routes.values
      .map((json) => RouteModel.fromJson(jsonDecode(json) as Map<String, dynamic>))
      .toList();

  RouteModel? getRoute(int id) {
    final json = _routes.get(id.toString());
    if (json == null) return null;
    return RouteModel.fromJson(jsonDecode(json) as Map<String, dynamic>);
  }

  // Checkins
  Future<void> saveCheckin(Checkin checkin) async {
    final key = checkin.id?.toString() ?? 'local_${checkin.jobId}_${checkin.checkinTime}';
    await _checkins.put(key, jsonEncode(checkin.toJson()));
  }

  List<Checkin> getCheckins() => _checkins.values
      .map((json) => Checkin.fromJson(jsonDecode(json) as Map<String, dynamic>))
      .toList();

  List<Checkin> getUnsyncedCheckins() => getCheckins().where((c) => !c.synced).toList();

  Future<void> markCheckinSynced(String key, int serverId) async {
    final json = _checkins.get(key);
    if (json != null) {
      final checkin = Checkin.fromJson(jsonDecode(json) as Map<String, dynamic>);
      final updated = checkin.copyWith(id: serverId, synced: true);
      await _checkins.put(key, jsonEncode(updated.toJson()));
    }
  }

  // Photos
  Future<void> savePhoto(Photo photo) async {
    await _photos.put(photo.localId, jsonEncode(photo.toJson()));
  }

  List<Photo> getPhotos() => _photos.values
      .map((json) => Photo.fromJson(jsonDecode(json) as Map<String, dynamic>))
      .toList();

  List<Photo> getPhotosForJob(int jobId) =>
      getPhotos().where((p) => p.jobId == jobId).toList();

  List<Photo> getUnsyncedPhotos() => getPhotos().where((p) => !p.synced).toList();

  Future<void> markPhotoSynced(String localId, int serverId, String remoteUrl) async {
    final json = _photos.get(localId);
    if (json != null) {
      final photo = Photo.fromJson(jsonDecode(json) as Map<String, dynamic>);
      final updated = photo.copyWith(id: serverId, remoteUrl: remoteUrl, synced: true);
      await _photos.put(localId, jsonEncode(updated.toJson()));
    }
  }

  // Signatures
  Future<void> saveSignature(Signature signature) async {
    await _signatures.put(signature.localId, jsonEncode(signature.toJson()));
  }

  List<Signature> getSignatures() => _signatures.values
      .map((json) => Signature.fromJson(jsonDecode(json) as Map<String, dynamic>))
      .toList();
  
  List<Signature> getSignaturesForJob(int jobId) =>
      getSignatures().where((s) => s.jobId == jobId).toList();

  List<Signature> getUnsyncedSignatures() =>
      getSignatures().where((s) => !s.synced).toList();

  Future<void> markSignatureSynced(String localId, int serverId) async {
    final json = _signatures.get(localId);
    if (json != null) {
      final sig = Signature.fromJson(jsonDecode(json) as Map<String, dynamic>);
      final updated = sig.copyWith(id: serverId, synced: true);
      await _signatures.put(localId, jsonEncode(updated.toJson()));
    }
  }

  // Notes
  Future<void> saveNote(Note note) async {
    await _notes.put(note.localId, jsonEncode(note.toJson()));
  }

  List<Note> getNotes() => _notes.values
      .map((json) => Note.fromJson(jsonDecode(json) as Map<String, dynamic>))
      .toList();

  List<Note> getNotesForJob(int jobId) =>
      getNotes().where((n) => n.jobId == jobId).toList();

  List<Note> getUnsyncedNotes() =>
      getNotes().where((n) => !n.synced).toList();

  Future<void> markNoteSynced(String localId, int serverId) async {
    final json = _notes.get(localId);
    if (json != null) {
      final note = Note.fromJson(jsonDecode(json) as Map<String, dynamic>);
      final updated = note.copyWith(id: serverId, synced: true);
      await _notes.put(localId, jsonEncode(updated.toJson()));
    }
  }

  // Settings
  Future<void> setSetting(String key, dynamic value) async {
    await _settings.put(key, value);
  }

  T? getSetting<T>(String key) => _settings.get(key) as T?;

  // Auth
  Future<void> saveAuthToken(String token) async {
    await _settings.put('auth_token', token);
  }

  String? getAuthToken() => _settings.get('auth_token') as String?;

  Future<void> saveUserId(int userId) async {
    await _settings.put('user_id', userId);
  }

  int? getUserId() => _settings.get('user_id') as int?;

  Future<void> saveInspectorId(int inspectorId) async {
    await _settings.put('inspector_id', inspectorId);
  }

  int? getInspectorId() => _settings.get('inspector_id') as int?;

  Future<void> saveServerUrl(String url) async {
    await _settings.put('server_url', url);
  }

  String? getServerUrl() => _settings.get('server_url') as String?;

  // Clear all data (logout)
  Future<void> clearAll() async {
    await _jobs.clear();
    await _routes.clear();
    await _checkins.clear();
    await _photos.clear();
    await _signatures.clear();
    await _notes.clear();
    await _settings.clear();
  }

  // Get sync status
  int get unsyncedCount =>
      getUnsyncedCheckins().length +
      getUnsyncedPhotos().length +
      getUnsyncedSignatures().length +
      getUnsyncedNotes().length;

  bool get hasUnsyncedData => unsyncedCount > 0;
}

