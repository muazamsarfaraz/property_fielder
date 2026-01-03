import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'core/di/injection.dart';
import 'core/services/workmanager_stub.dart'
    if (dart.library.io) 'core/services/workmanager_native.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/providers/auth_provider.dart';
import 'features/jobs/providers/job_provider.dart';
import 'features/routes/providers/route_provider.dart';
import 'features/checkin/providers/checkin_provider.dart';
import 'features/photos/providers/photo_provider.dart';
import 'features/signatures/providers/signature_provider.dart';
import 'features/notes/providers/note_provider.dart';
import 'features/sync/providers/sync_provider.dart';
import 'features/safety/providers/safety_provider.dart';
import 'features/templates/providers/template_provider.dart';
import 'routes/app_router.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // Initialize Hive
    debugPrint('🔧 Initializing Hive...');
    await Hive.initFlutter();
    debugPrint('✅ Hive initialized');

    // Setup dependency injection
    debugPrint('🔧 Setting up dependencies...');
    await setupDependencies();
    debugPrint('✅ Dependencies set up');

    // Initialize WorkManager for background sync (not supported on web)
    debugPrint('🔧 Initializing WorkManager...');
    await initializeWorkManager();
    debugPrint('✅ WorkManager initialized');

    debugPrint('✅ All initialization complete!');

    // Start app
    runApp(const PropertyFielderInspectorApp());
  } catch (e, stackTrace) {
    debugPrint('❌ Initialization error: $e');
    debugPrint('Stack trace: $stackTrace');
    runApp(PropertyFielderInspectorApp(
      initializationError: 'Initialization failed: $e',
    ));
  }
}

class PropertyFielderInspectorApp extends StatelessWidget {
  final String? initializationError;

  const PropertyFielderInspectorApp({
    super.key,
    this.initializationError,
  });

  @override
  Widget build(BuildContext context) {
    // If there's an initialization error, show error screen
    if (initializationError != null) {
      return MaterialApp(
        title: 'Property Fielder Inspector',
        theme: AppTheme.lightTheme,
        home: Scaffold(
          body: Center(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 64,
                    color: Colors.orange,
                  ),
                  const SizedBox(height: 24),
                  Text(
                    initializationError!,
                    textAlign: TextAlign.center,
                    style: const TextStyle(fontSize: 16),
                  ),
                  const SizedBox(height: 24),
                  const CircularProgressIndicator(),
                ],
              ),
            ),
          ),
        ),
      );
    }

    // Normal app with providers
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => getIt<AuthProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<JobProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<RouteProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<CheckinProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<PhotoProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<SignatureProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<NoteProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<SyncProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<SafetyProvider>()),
        ChangeNotifierProvider(create: (_) => getIt<TemplateProvider>()),
      ],
      child: MaterialApp(
        title: 'Property Fielder Inspector',
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        onGenerateRoute: AppRouter.generateRoute,
        initialRoute: AppRouter.splash,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

