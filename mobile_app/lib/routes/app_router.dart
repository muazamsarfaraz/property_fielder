import 'package:flutter/material.dart';
import '../features/splash/screens/splash_screen.dart';
import '../features/auth/screens/login_screen.dart';
import '../features/jobs/screens/job_list_screen.dart';
import '../features/jobs/screens/job_detail_screen.dart';
import '../features/routes/screens/route_list_screen.dart';
import '../features/dashboard/screens/dashboard_screen.dart';
import '../features/photos/screens/photo_gallery_screen.dart';
import '../features/signatures/screens/signature_capture_screen.dart';
import '../features/notes/screens/note_list_screen.dart';
import '../features/sync/screens/sync_screen.dart';
import '../features/settings/screens/settings_screen.dart';
import '../features/maps/screens/job_map_screen.dart';
import '../features/safety/screens/safety_timer_screen.dart';
import '../features/templates/screens/template_execution_screen.dart';
import '../core/models/job.dart';

class AppRouter {
  static const String splash = '/';
  static const String login = '/login';
  static const String dashboard = '/dashboard';
  static const String jobList = '/jobs';
  static const String jobDetail = '/jobs/detail';
  static const String jobMap = '/jobs/map';
  static const String routeList = '/routes';
  static const String photoGallery = '/photos';
  static const String signatureCapture = '/signature';
  static const String noteList = '/notes';
  static const String sync = '/sync';
  static const String settings = '/settings';
  static const String safetyTimer = '/safety';
  static const String templateExecution = '/inspection/execute';

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case splash:
        return MaterialPageRoute(builder: (_) => const SplashScreen());

      case login:
        return MaterialPageRoute(builder: (_) => const LoginScreen());
      
      case dashboard:
        return MaterialPageRoute(builder: (_) => const DashboardScreen());
      
      case jobList:
        return MaterialPageRoute(builder: (_) => const JobListScreen());
      
      case jobDetail:
        final args = settings.arguments as Map<String, dynamic>?;
        final jobId = args?['jobId'] as int?;
        return MaterialPageRoute(
          builder: (_) => JobDetailScreen(jobId: jobId ?? 0),
        );

      case jobMap:
        final args = settings.arguments as Map<String, dynamic>?;
        final jobs = args?['jobs'] as List<Job>? ?? [];
        final selectedJob = args?['selectedJob'] as Job?;
        return MaterialPageRoute(
          builder: (_) => JobMapScreen(jobs: jobs, selectedJob: selectedJob),
        );

      case routeList:
        return MaterialPageRoute(builder: (_) => const RouteListScreen());
      
      case photoGallery:
        final args = settings.arguments as Map<String, dynamic>?;
        final jobId = args?['jobId'] as int?;
        return MaterialPageRoute(
          builder: (_) => PhotoGalleryScreen(jobId: jobId ?? 0),
        );
      
      case signatureCapture:
        final args = settings.arguments as Map<String, dynamic>?;
        final jobId = args?['jobId'] as int?;
        return MaterialPageRoute(
          builder: (_) => SignatureCaptureScreen(jobId: jobId ?? 0),
        );
      
      case noteList:
        final args = settings.arguments as Map<String, dynamic>?;
        final jobId = args?['jobId'] as int?;
        return MaterialPageRoute(
          builder: (_) => NoteListScreen(jobId: jobId ?? 0),
        );
      
      case sync:
        return MaterialPageRoute(builder: (_) => const SyncScreen());
      
      case AppRouter.settings:
        return MaterialPageRoute(builder: (_) => const SettingsScreen());

      case safetyTimer:
        final args = settings.arguments as Map<String, dynamic>?;
        final jobId = args?['jobId'] as int?;
        return MaterialPageRoute(
          builder: (_) => SafetyTimerScreen(jobId: jobId),
        );

      case templateExecution:
        final args = settings.arguments as Map<String, dynamic>;
        final jobId = args['jobId'] as int;
        return MaterialPageRoute(
          builder: (_) => TemplateExecutionScreen(jobId: jobId),
        );

      default:
        return MaterialPageRoute(
          builder: (_) => Scaffold(
            body: Center(
              child: Text('No route defined for ${settings.name}'),
            ),
          ),
        );
    }
  }
}

