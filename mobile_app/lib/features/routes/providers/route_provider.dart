import 'package:flutter/foundation.dart';
import '../../../core/api/api_client.dart';
import '../../../core/models/route.dart';
import '../../../core/services/storage_service.dart';
import '../../../core/services/sync_service.dart';

class RouteProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final StorageService _storageService;
  final SyncService _syncService;

  List<RouteModel> _routes = [];
  RouteModel? _selectedRoute;
  bool _isLoading = false;
  String? _errorMessage;
  String? _filterDate;

  RouteProvider({
    required ApiClient apiClient,
    required StorageService storageService,
    required SyncService syncService,
  })  : _apiClient = apiClient,
        _storageService = storageService,
        _syncService = syncService {
    _loadCachedRoutes();
  }

  List<RouteModel> get routes => _routes;
  RouteModel? get selectedRoute => _selectedRoute;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<RouteModel> get todayRoutes {
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month.toString().padLeft(2, '0')}-${today.day.toString().padLeft(2, '0')}';
    return _routes.where((r) => r.routeDate == todayStr).toList();
  }

  List<RouteModel> get activeRoutes => _routes.where((r) => r.status == 'in_progress').toList();
  List<RouteModel> get completedRoutes => _routes.where((r) => r.status == 'completed').toList();

  void _loadCachedRoutes() {
    _routes = _storageService.getRoutes();
    notifyListeners();
  }

  Future<void> fetchRoutes({String? date, bool forceRefresh = false}) async {
    _isLoading = true;
    _errorMessage = null;
    _filterDate = date;
    notifyListeners();

    try {
      if (await _syncService.hasConnectivity() || forceRefresh) {
        final response = await _apiClient.getMyRoutes(date: date);
        if (response.success) {
          _routes = response.routes;
          await _storageService.saveRoutes(_routes);
        } else {
          _errorMessage = response.error;
          _loadCachedRoutes();
        }
      } else {
        _loadCachedRoutes();
      }
    } catch (e) {
      _errorMessage = 'Failed to fetch routes: $e';
      _loadCachedRoutes();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void selectRoute(RouteModel route) {
    _selectedRoute = route;
    notifyListeners();
  }

  void clearSelection() {
    _selectedRoute = null;
    notifyListeners();
  }

  Future<void> refresh() async {
    await fetchRoutes(date: _filterDate, forceRefresh: true);
  }
}

