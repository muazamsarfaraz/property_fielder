import 'package:flutter/foundation.dart';
import '../../../core/api/api_client.dart';
import '../../../core/services/storage_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final StorageService _storageService;

  bool _isAuthenticated = false;
  bool _isLoading = false;
  String? _errorMessage;
  int? _userId;
  int? _inspectorId;
  String? _userName;
  String? _userEmail;

  AuthProvider({
    required ApiClient apiClient,
    required StorageService storageService,
  })  : _apiClient = apiClient,
        _storageService = storageService {
    _checkAuthStatus();
  }

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  int? get userId => _userId;
  int? get inspectorId => _inspectorId;
  String? get userName => _userName;
  String? get userEmail => _userEmail;

  void _checkAuthStatus() {
    final token = _storageService.getAuthToken();
    _userId = _storageService.getUserId();
    _inspectorId = _storageService.getInspectorId();
    _isAuthenticated = token != null && _userId != null;
    notifyListeners();
  }

  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.login({
        'username': username,
        'password': password,
      });

      if (response['success'] == true) {
        final token = response['token'] as String?;
        final userId = response['user_id'] as int?;
        final inspectorId = response['inspector_id'] as int?;
        final userName = response['name'] as String?;
        final userEmail = response['email'] as String?;

        if (token != null && userId != null) {
          await _storageService.saveAuthToken(token);
          await _storageService.saveUserId(userId);
          if (inspectorId != null) {
            await _storageService.saveInspectorId(inspectorId);
          }

          _isAuthenticated = true;
          _userId = userId;
          _inspectorId = inspectorId;
          _userName = userName;
          _userEmail = userEmail;
          _isLoading = false;
          notifyListeners();
          return true;
        }
      }

      _errorMessage = response['error'] as String? ?? 'Login failed';
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _errorMessage = 'Connection error: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<void> logout() async {
    await _storageService.clearAll();
    _isAuthenticated = false;
    _userId = null;
    _inspectorId = null;
    _userName = null;
    _userEmail = null;
    notifyListeners();
  }

  Future<bool> checkSession() async {
    if (!_isAuthenticated) return false;
    
    try {
      // Try to fetch jobs to verify session is still valid
      await _apiClient.getMyJobs();
      return true;
    } catch (e) {
      // Session invalid
      await logout();
      return false;
    }
  }
}

