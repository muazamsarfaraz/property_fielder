import 'package:dio/dio.dart';
import 'package:get_it/get_it.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

import '../api/api_client.dart';
import '../services/storage_service.dart';
import '../services/sync_service.dart';
import '../../features/auth/providers/auth_provider.dart';
import '../../features/jobs/providers/job_provider.dart';
import '../../features/routes/providers/route_provider.dart';
import '../../features/checkin/providers/checkin_provider.dart';
import '../../features/photos/providers/photo_provider.dart';
import '../../features/signatures/providers/signature_provider.dart';
import '../../features/notes/providers/note_provider.dart';
import '../../features/sync/providers/sync_provider.dart';
import '../../features/safety/providers/safety_provider.dart';
import '../../features/templates/providers/template_provider.dart';

final getIt = GetIt.instance;

Future<void> setupDependencies() async {
  // Storage Service (singleton)
  final storageService = StorageService();
  try {
    await storageService.init();
  } catch (e) {
    print('⚠️ Storage service initialization failed: $e');
    // Continue anyway - Hive might work on web
  }
  getIt.registerSingleton<StorageService>(storageService);

  // Dio HTTP Client with cookie support
  final dio = Dio(BaseOptions(
    connectTimeout: const Duration(seconds: 30),
    receiveTimeout: const Duration(seconds: 30),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  ));

  // Add auth interceptor - send session_id as Bearer token for cross-origin compatibility
  // Note: Cookie headers are blocked by browsers for cross-origin requests (CORS),
  // so we use Authorization: Bearer header instead which works across all platforms.
  dio.interceptors.add(InterceptorsWrapper(
    onRequest: (options, handler) {
      final token = storageService.getAuthToken();
      if (token != null) {
        // Send session_id as Bearer token (works for cross-origin requests)
        options.headers['Authorization'] = 'Bearer $token';
      }
      return handler.next(options);
    },
    onError: (error, handler) {
      if (error.response?.statusCode == 401) {
        // Token expired - trigger logout
        storageService.clearAll();
      }
      return handler.next(error);
    },
  ));

  getIt.registerSingleton<Dio>(dio);

  // API Client - default to Railway production URL
  // Users can override this via settings
  final baseUrl = storageService.getServerUrl() ?? 'https://propertyfielder-production.up.railway.app';
  final apiClient = ApiClient(dio, baseUrl: baseUrl);
  getIt.registerSingleton<ApiClient>(apiClient);

  // Connectivity
  getIt.registerSingleton<Connectivity>(Connectivity());

  // Sync Service
  final syncService = SyncService(
    apiClient: apiClient,
    storageService: storageService,
    connectivity: getIt<Connectivity>(),
  );
  getIt.registerSingleton<SyncService>(syncService);

  // Providers
  getIt.registerFactory<AuthProvider>(() => AuthProvider(
    apiClient: apiClient,
    storageService: storageService,
  ));

  getIt.registerFactory<JobProvider>(() => JobProvider(
    apiClient: apiClient,
    storageService: storageService,
    syncService: syncService,
  ));

  getIt.registerFactory<RouteProvider>(() => RouteProvider(
    apiClient: apiClient,
    storageService: storageService,
    syncService: syncService,
  ));

  getIt.registerFactory<CheckinProvider>(() => CheckinProvider(
    apiClient: apiClient,
    storageService: storageService,
  ));

  getIt.registerFactory<PhotoProvider>(() => PhotoProvider(
    storageService: storageService,
  ));

  getIt.registerFactory<SignatureProvider>(() => SignatureProvider(
    storageService: storageService,
  ));

  getIt.registerFactory<NoteProvider>(() => NoteProvider(
    storageService: storageService,
  ));

  getIt.registerFactory<SyncProvider>(() => SyncProvider(
    syncService: syncService,
    storageService: storageService,
  ));

  getIt.registerFactory<SafetyProvider>(() => SafetyProvider(
    apiClient: apiClient,
    storageService: storageService,
  ));

  getIt.registerFactory<TemplateProvider>(() => TemplateProvider(
    apiClient: apiClient,
    storageService: storageService,
  ));
}

