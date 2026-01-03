import 'package:flutter/foundation.dart';
import '../../../core/api/api_client.dart';
import '../../../core/models/job.dart';
import '../../../core/services/storage_service.dart';
import '../../../core/services/sync_service.dart';

class JobProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final StorageService _storageService;
  final SyncService _syncService;

  List<Job> _jobs = [];
  Job? _selectedJob;
  bool _isLoading = false;
  String? _errorMessage;
  String? _filterDate;
  String? _filterStatus;

  JobProvider({
    required ApiClient apiClient,
    required StorageService storageService,
    required SyncService syncService,
  })  : _apiClient = apiClient,
        _storageService = storageService,
        _syncService = syncService {
    _loadCachedJobs();
  }

  List<Job> get jobs => _jobs;
  Job? get selectedJob => _selectedJob;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<Job> get todayJobs {
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}';
    return _jobs.where((j) => j.scheduledDate == todayStr).toList();
  }

  List<Job> get pendingJobs => _jobs.where((j) => j.status == 'pending' || j.status == 'assigned').toList();
  List<Job> get inProgressJobs => _jobs.where((j) => j.status == 'in_progress').toList();
  List<Job> get completedJobs => _jobs.where((j) => j.status == 'completed').toList();

  void _loadCachedJobs() {
    _jobs = _storageService.getJobs();
    notifyListeners();
  }

  Future<void> fetchJobs({String? date, String? status, bool forceRefresh = false}) async {
    _isLoading = true;
    _errorMessage = null;
    _filterDate = date;
    _filterStatus = status;
    notifyListeners();

    try {
      if (await _syncService.hasConnectivity() || forceRefresh) {
        final response = await _apiClient.getMyJobs(date: date, status: status);
        if (response.success) {
          _jobs = response.jobs;
          await _storageService.saveJobs(_jobs);
        } else {
          _errorMessage = response.error;
          _loadCachedJobs();
        }
      } else {
        _loadCachedJobs();
      }
    } catch (e) {
      _errorMessage = 'Failed to fetch jobs: $e';
      _loadCachedJobs();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchJobDetail(int jobId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      if (await _syncService.hasConnectivity()) {
        final response = await _apiClient.getJobDetail(jobId);
        if (response.success && response.job != null) {
          _selectedJob = response.job;
          await _storageService.saveJob(_selectedJob!);
        } else {
          _errorMessage = response.error;
          _selectedJob = _storageService.getJob(jobId);
        }
      } else {
        _selectedJob = _storageService.getJob(jobId);
      }
    } catch (e) {
      _errorMessage = 'Failed to fetch job detail: $e';
      _selectedJob = _storageService.getJob(jobId);
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void selectJob(Job job) {
    _selectedJob = job;
    notifyListeners();
  }

  void clearSelection() {
    _selectedJob = null;
    notifyListeners();
  }

  Future<void> refresh() async {
    await fetchJobs(date: _filterDate, status: _filterStatus, forceRefresh: true);
  }
}

