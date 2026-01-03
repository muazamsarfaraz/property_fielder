import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/sync_provider.dart';

class SyncScreen extends StatelessWidget {
  const SyncScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Sync Status'),
      ),
      body: Consumer<SyncProvider>(
        builder: (context, syncProvider, _) {
          return Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildStatusCard(context, syncProvider),
                const SizedBox(height: 16),
                _buildPendingCard(context, syncProvider),
                const SizedBox(height: 16),
                if (syncProvider.lastResult != null)
                  _buildLastSyncCard(context, syncProvider),
                const Spacer(),
                FilledButton.icon(
                  onPressed: syncProvider.isSyncing ? null : () => syncProvider.syncAll(),
                  icon: syncProvider.isSyncing
                      ? SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Theme.of(context).colorScheme.onPrimary,
                          ),
                        )
                      : const Icon(Icons.sync),
                  label: Text(syncProvider.isSyncing ? 'Syncing...' : 'Sync Now'),
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildStatusCard(BuildContext context, SyncProvider syncProvider) {
    const isOnline = true; // Would check connectivity here
    final statusColor = isOnline
        ? Theme.of(context).colorScheme.secondary
        : Theme.of(context).colorScheme.tertiary;

    return Card(
      elevation: 0,
      color: statusColor.withValues(alpha: 0.1),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: statusColor.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                isOnline ? Icons.cloud_done : Icons.cloud_off,
                size: 32,
                color: statusColor,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isOnline ? 'Online' : 'Offline',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: statusColor,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    syncProvider.syncStatusText,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  if (syncProvider.lastSyncTime != null)
                    Text(
                      'Last sync: ${_formatDateTime(syncProvider.lastSyncTime!)}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurfaceVariant,
                      ),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPendingCard(BuildContext context, SyncProvider syncProvider) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Pending Items',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            _buildPendingRow(context, Icons.login_outlined, 'Check-ins', 0),
            _buildPendingRow(context, Icons.photo_outlined, 'Photos', 0),
            _buildPendingRow(context, Icons.draw_outlined, 'Signatures', 0),
            _buildPendingRow(context, Icons.note_outlined, 'Notes', 0),
            const Divider(height: 24),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.5),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Total',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: Theme.of(context).colorScheme.onPrimaryContainer,
                    ),
                  ),
                  Text(
                    '${syncProvider.pendingCount}',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPendingRow(BuildContext context, IconData icon, String label, int count) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(
            icon,
            size: 20,
            color: Theme.of(context).colorScheme.onSurfaceVariant,
          ),
          const SizedBox(width: 12),
          Expanded(child: Text(label)),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 2),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '$count',
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLastSyncCard(BuildContext context, SyncProvider syncProvider) {
    final result = syncProvider.lastResult!;
    final resultColor = result.success
        ? Theme.of(context).colorScheme.secondary
        : Theme.of(context).colorScheme.error;

    return Card(
      elevation: 0,
      color: resultColor.withValues(alpha: 0.1),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  result.success ? Icons.check_circle : Icons.error,
                  color: resultColor,
                ),
                const SizedBox(width: 8),
                Text(
                  'Last Sync Result',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Synced: ${result.totalSynced} items',
              style: TextStyle(color: Theme.of(context).colorScheme.onSurfaceVariant),
            ),
            if (result.totalFailed > 0)
              Text(
                'Failed: ${result.totalFailed} items',
                style: TextStyle(color: Theme.of(context).colorScheme.error),
              ),
            if (result.hasErrors)
              ...result.errors.take(3).map((e) => Padding(
                padding: const EdgeInsets.only(top: 4),
                child: Text(
                  e,
                  style: TextStyle(
                    fontSize: 12,
                    color: Theme.of(context).colorScheme.error,
                  ),
                ),
              )),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }
}

