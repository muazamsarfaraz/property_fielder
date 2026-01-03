import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../auth/providers/auth_provider.dart';
import '../../jobs/providers/job_provider.dart';
import '../../routes/providers/route_provider.dart';
import '../../sync/providers/sync_provider.dart';
import '../../../routes/app_router.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final jobProvider = context.read<JobProvider>();
    final routeProvider = context.read<RouteProvider>();
    await Future.wait([
      jobProvider.fetchJobs(),
      routeProvider.fetchRoutes(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Property Fielder'),
        actions: [
          Consumer<SyncProvider>(
            builder: (context, syncProvider, _) {
              return IconButton(
                icon: syncProvider.isSyncing
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : Badge(
                        isLabelVisible: syncProvider.hasPendingData,
                        label: Text('${syncProvider.pendingCount}'),
                        child: const Icon(Icons.sync),
                      ),
                onPressed: syncProvider.isSyncing ? null : () => syncProvider.syncAll(),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.pushNamed(context, AppRouter.settings),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildWelcomeCard(),
              const SizedBox(height: 16),
              _buildTodayStats(),
              const SizedBox(height: 16),
              _buildQuickActions(),
              const SizedBox(height: 16),
              _buildUpcomingJobs(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeCard() {
    return Consumer<AuthProvider>(
      builder: (context, auth, _) {
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  child: Text(
                    (auth.userName ?? 'U')[0].toUpperCase(),
                    style: const TextStyle(fontSize: 24),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome back,',
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                      Text(
                        auth.userName ?? 'Inspector',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildTodayStats() {
    return Consumer<JobProvider>(
      builder: (context, jobProvider, _) {
        final today = jobProvider.todayJobs;
        final completed = today.where((j) => j.isCompleted).length;
        final inProgress = today.where((j) => j.isInProgress).length;
        final pending = today.length - completed - inProgress;

        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("Today's Progress", style: Theme.of(context).textTheme.titleMedium),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildStatItem('Pending', pending, Colors.orange),
                    _buildStatItem('In Progress', inProgress, Colors.blue),
                    _buildStatItem('Completed', completed, Colors.green),
                  ],
                ),
                const SizedBox(height: 16),
                LinearProgressIndicator(
                  value: today.isEmpty ? 0 : completed / today.length,
                  backgroundColor: Colors.grey[200],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatItem(String label, int count, Color color) {
    return Column(
      children: [
        Text(
          '$count',
          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: color),
        ),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Quick Actions', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildActionButton(Icons.list_alt, 'Jobs', () => Navigator.pushNamed(context, AppRouter.jobList)),
                _buildActionButton(Icons.route, 'Routes', () => Navigator.pushNamed(context, AppRouter.routeList)),
                _buildActionButton(Icons.sync, 'Sync', () => Navigator.pushNamed(context, AppRouter.sync)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(IconData icon, String label, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, size: 32, color: Theme.of(context).primaryColor),
            const SizedBox(height: 4),
            Text(label),
          ],
        ),
      ),
    );
  }

  Widget _buildUpcomingJobs() {
    return Consumer<JobProvider>(
      builder: (context, jobProvider, _) {
        final upcoming = jobProvider.pendingJobs.take(3).toList();
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Upcoming Jobs', style: Theme.of(context).textTheme.titleMedium),
                    TextButton(
                      onPressed: () => Navigator.pushNamed(context, AppRouter.jobList),
                      child: const Text('View All'),
                    ),
                  ],
                ),
                if (upcoming.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('No upcoming jobs'),
                  )
                else
                  ...upcoming.map((job) => ListTile(
                    leading: const Icon(Icons.work_outline),
                    title: Text(job.name),
                    subtitle: Text(job.fullAddress),
                    trailing: Text(job.scheduledTime ?? ''),
                    onTap: () => Navigator.pushNamed(
                      context,
                      AppRouter.jobDetail,
                      arguments: {'jobId': job.id},
                    ),
                  )),
              ],
            ),
          ),
        );
      },
    );
  }
}

