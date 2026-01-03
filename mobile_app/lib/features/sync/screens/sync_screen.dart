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
                ElevatedButton.icon(
                  onPressed: syncProvider.isSyncing ? null : () => syncProvider.syncAll(),
                  icon: syncProvider.isSyncing
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.sync),
                  label: Text(syncProvider.isSyncing ? 'Syncing...' : 'Sync Now'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
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
    final isOnline = true; // Would check connectivity here
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(
              isOnline ? Icons.cloud_done : Icons.cloud_off,
              size: 48,
              color: isOnline ? Colors.green : Colors.orange,
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isOnline ? 'Online' : 'Offline',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  Text(
                    syncProvider.syncStatusText,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  if (syncProvider.lastSyncTime != null)
                    Text(
                      'Last sync: ${_formatDateTime(syncProvider.lastSyncTime!)}',
                      style: Theme.of(context).textTheme.bodySmall,
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
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Pending Items', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 16),
            _buildPendingRow(context, Icons.login, 'Check-ins', 0),
            _buildPendingRow(context, Icons.photo, 'Photos', 0),
            _buildPendingRow(context, Icons.draw, 'Signatures', 0),
            _buildPendingRow(context, Icons.note, 'Notes', 0),
            const Divider(),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Total', style: TextStyle(fontWeight: FontWeight.bold)),
                Text(
                  '${syncProvider.pendingCount}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPendingRow(BuildContext context, IconData icon, String label, int count) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Expanded(child: Text(label)),
          Text('$count'),
        ],
      ),
    );
  }

  Widget _buildLastSyncCard(BuildContext context, SyncProvider syncProvider) {
    final result = syncProvider.lastResult!;
    
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  result.success ? Icons.check_circle : Icons.error,
                  color: result.success ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text('Last Sync Result', style: Theme.of(context).textTheme.titleMedium),
              ],
            ),
            const SizedBox(height: 8),
            Text('Synced: ${result.totalSynced} items'),
            if (result.totalFailed > 0)
              Text(
                'Failed: ${result.totalFailed} items',
                style: const TextStyle(color: Colors.red),
              ),
            if (result.hasErrors)
              ...result.errors.take(3).map((e) => Text(
                e,
                style: const TextStyle(fontSize: 12, color: Colors.red),
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

