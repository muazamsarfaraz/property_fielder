import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/route_provider.dart';
import '../../../core/models/route.dart';

class RouteListScreen extends StatefulWidget {
  const RouteListScreen({super.key});

  @override
  State<RouteListScreen> createState() => _RouteListScreenState();
}

class _RouteListScreenState extends State<RouteListScreen> {
  @override
  void initState() {
    super.initState();
    context.read<RouteProvider>().fetchRoutes();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Routes'),
      ),
      body: Consumer<RouteProvider>(
        builder: (context, routeProvider, _) {
          if (routeProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final routes = routeProvider.routes;
          if (routes.isEmpty) {
            return RefreshIndicator(
              onRefresh: () => routeProvider.refresh(),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                child: SizedBox(
                  height: MediaQuery.of(context).size.height * 0.7,
                  child: Center(
                    child: Padding(
                      padding: const EdgeInsets.all(32),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(24),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.3),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              Icons.route_outlined,
                              size: 64,
                              color: Theme.of(context).colorScheme.primary,
                            ),
                          ),
                          const SizedBox(height: 24),
                          Text(
                            'No Routes Yet',
                            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            'Optimized routes for your jobs will appear here.\nPull down to refresh.',
                            textAlign: TextAlign.center,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context).colorScheme.onSurfaceVariant,
                            ),
                          ),
                          const SizedBox(height: 24),
                          OutlinedButton.icon(
                            onPressed: () => routeProvider.refresh(),
                            icon: const Icon(Icons.refresh),
                            label: const Text('Refresh'),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            );
          }

          return RefreshIndicator(
            onRefresh: () => routeProvider.refresh(),
            child: ListView.builder(
              itemCount: routes.length,
              itemBuilder: (context, index) {
                final route = routes[index];
                return _buildRouteCard(route);
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildRouteCard(RouteModel route) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  route.name,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
                Chip(
                  label: Text(route.statusLabel),
                  backgroundColor: _getStatusColor(route.status).withValues(alpha: 0.2),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.calendar_today, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(route.routeDate),
                const SizedBox(width: 16),
                Icon(Icons.work, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text('${route.completedCount}/${route.jobCount} jobs'),
              ],
            ),
            const SizedBox(height: 8),
            LinearProgressIndicator(
              value: route.progressPercent / 100,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(_getStatusColor(route.status)),
            ),
            const SizedBox(height: 4),
            Text(
              '${route.progressPercent.toStringAsFixed(0)}% complete',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            if (route.totalDistance != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.straighten, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text('${route.totalDistance!.toStringAsFixed(1)} km'),
                  if (route.totalDuration != null) ...[
                    const SizedBox(width: 16),
                    Icon(Icons.timer, size: 16, color: Colors.grey[600]),
                    const SizedBox(width: 4),
                    Text('${route.totalDuration} min'),
                  ],
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(String status) {
    switch (status) {
      case 'planned':
        return Colors.orange;
      case 'in_progress':
        return Colors.blue;
      case 'completed':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }
}

