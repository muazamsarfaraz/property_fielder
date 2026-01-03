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
      children: [
        Expanded(
          child: Text(title, style: Theme.of(context).textTheme.headlineSmall),
        ),
        Chip(label: Text(status)),
      ],
    );
  }

  Widget _buildInfoCard(String title, List<Widget> children) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 8),
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
                child: ElevatedButton.icon(
                  onPressed: checkinProvider.isLoading ? null : _handleCheckIn,
                  icon: const Icon(Icons.login),
                  label: const Text('Check In'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                ),
              ),
            if (job.canCheckOut) ...[
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: checkinProvider.isLoading ? null : _handleCheckOut,
                  icon: const Icon(Icons.logout),
                  label: const Text('Check Out'),
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.orange),
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
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Actions', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildActionButton(Icons.camera_alt, 'Photos', () {
                  Navigator.pushNamed(context, AppRouter.photoGallery, arguments: {'jobId': widget.jobId});
                }),
                _buildActionButton(Icons.draw, 'Signature', () {
                  Navigator.pushNamed(context, AppRouter.signatureCapture, arguments: {'jobId': widget.jobId});
                }),
                _buildActionButton(Icons.note_add, 'Notes', () {
                  Navigator.pushNamed(context, AppRouter.noteList, arguments: {'jobId': widget.jobId});
                }),
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
}

