import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/job_provider.dart';
import '../../checkin/providers/checkin_provider.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../routes/app_router.dart';

class JobDetailScreen extends StatefulWidget {
  final int jobId;

  const JobDetailScreen({super.key, required this.jobId});

  @override
  State<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends State<JobDetailScreen> {
  @override
  void initState() {
    super.initState();
    context.read<JobProvider>().fetchJobDetail(widget.jobId);
  }

  Future<void> _openMaps() async {
    final job = context.read<JobProvider>().selectedJob;
    if (job == null) return;

    final lat = job.latitude;
    final lng = job.longitude;
    if (lat != null && lng != null) {
      final url = Uri.parse('https://www.google.com/maps/dir/?api=1&destination=$lat,$lng');
      if (await canLaunchUrl(url)) {
        await launchUrl(url, mode: LaunchMode.externalApplication);
      }
    }
  }

  Future<void> _handleCheckIn() async {
    final checkinProvider = context.read<CheckinProvider>();
    final authProvider = context.read<AuthProvider>();
    
    final success = await checkinProvider.checkIn(
      widget.jobId,
      authProvider.inspectorId ?? 0,
    );

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'Checked in successfully' : 'Check-in failed'),
          backgroundColor: success ? Colors.green : Colors.red,
        ),
      );
    }
  }

  Future<void> _handleCheckOut() async {
    final checkinProvider = context.read<CheckinProvider>();
    
    final success = await checkinProvider.checkOut(widget.jobId);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'Checked out successfully' : 'Check-out failed'),
          backgroundColor: success ? Colors.green : Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Details'),
        actions: [
          IconButton(
            icon: const Icon(Icons.directions),
            onPressed: _openMaps,
            tooltip: 'Navigate',
          ),
        ],
      ),
      body: Consumer<JobProvider>(
        builder: (context, jobProvider, _) {
          if (jobProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          final job = jobProvider.selectedJob;
          if (job == null) {
            return const Center(child: Text('Job not found'));
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildHeader(job.name, job.statusLabel),
                const SizedBox(height: 16),
                _buildInfoCard('Property', [
                  _buildInfoRow(Icons.location_on, job.fullAddress),
                  if (job.propertyName != null)
                    _buildInfoRow(Icons.home, job.propertyName!),
                ]),
                const SizedBox(height: 16),
                _buildInfoCard('Schedule', [
                  _buildInfoRow(Icons.calendar_today, job.scheduledDate ?? 'Not scheduled'),
                  _buildInfoRow(Icons.access_time, job.scheduledTime ?? 'No time set'),
                  _buildInfoRow(Icons.timer, '${job.estimatedDuration ?? 60} minutes'),
                ]),
                const SizedBox(height: 16),
                _buildInfoCard('Job Type', [
                  _buildInfoRow(Icons.work, job.jobType ?? 'Not specified'),
                  _buildInfoRow(Icons.flag, 'Priority: ${job.priority}'),
                ]),
                const SizedBox(height: 16),
                _buildActionButtons(),
                const SizedBox(height: 16),
                _buildQuickActions(),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildHeader(String title, String status) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Expanded(
          child: Text(
            title,
            style: Theme.of(context).textTheme.headlineSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(width: 12),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(
            status,
            style: TextStyle(
              fontWeight: FontWeight.w600,
              color: Theme.of(context).colorScheme.onPrimaryContainer,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInfoCard(String title, List<Widget> children) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(6),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Icon(
              icon,
              size: 18,
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(child: Text(text)),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Consumer<CheckinProvider>(
      builder: (context, checkinProvider, _) {
        final job = context.read<JobProvider>().selectedJob;
        if (job == null) return const SizedBox.shrink();

        return Row(
          children: [
            if (job.canCheckIn)
              Expanded(
                child: FilledButton.icon(
                  onPressed: checkinProvider.isLoading ? null : _handleCheckIn,
                  icon: const Icon(Icons.login),
                  label: const Text('Check In'),
                  style: FilledButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.secondary,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            if (job.canCheckOut) ...[
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton.icon(
                  onPressed: checkinProvider.isLoading ? null : _handleCheckOut,
                  icon: const Icon(Icons.logout),
                  label: const Text('Check Out'),
                  style: FilledButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.tertiary,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                ),
              ),
            ],
          ],
        );
      },
    );
  }

  Widget _buildQuickActions() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Actions',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildActionButton(
                    Icons.camera_alt_outlined,
                    'Photos',
                    () => Navigator.pushNamed(context, AppRouter.photoGallery, arguments: {'jobId': widget.jobId}),
                    Theme.of(context).colorScheme.primary,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionButton(
                    Icons.draw_outlined,
                    'Signature',
                    () => Navigator.pushNamed(context, AppRouter.signatureCapture, arguments: {'jobId': widget.jobId}),
                    Theme.of(context).colorScheme.secondary,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildActionButton(
                    Icons.note_add_outlined,
                    'Notes',
                    () => Navigator.pushNamed(context, AppRouter.noteList, arguments: {'jobId': widget.jobId}),
                    Theme.of(context).colorScheme.tertiary,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionButton(IconData icon, String label, VoidCallback onTap, Color color) {
    return Material(
      color: color.withValues(alpha: 0.1),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
          child: Column(
            children: [
              Icon(icon, size: 28, color: color),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  fontSize: 12,
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

