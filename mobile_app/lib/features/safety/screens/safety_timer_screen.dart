import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/safety_provider.dart';
import '../widgets/panic_button.dart';

/// Safety Timer Screen - Lone Worker Protection (HSE Compliance)
/// 
/// Displays countdown timer, extend/cancel buttons, and PANIC button.
class SafetyTimerScreen extends StatefulWidget {
  final int? jobId;

  const SafetyTimerScreen({super.key, this.jobId});

  @override
  State<SafetyTimerScreen> createState() => _SafetyTimerScreenState();
}

class _SafetyTimerScreenState extends State<SafetyTimerScreen> {
  int _selectedDuration = 60; // Default 60 minutes

  @override
  void initState() {
    super.initState();
    context.read<SafetyProvider>().fetchStatus();
  }

  Future<void> _startTimer() async {
    final success = await context.read<SafetyProvider>().startTimer(
      jobId: widget.jobId,
      durationMinutes: _selectedDuration,
    );
    if (mounted && success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Safety timer started for $_selectedDuration minutes'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  Future<void> _extendTimer() async {
    final success = await context.read<SafetyProvider>().extendTimer(minutes: 30);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success ? 'Timer extended by 30 minutes' : 'Failed to extend timer'),
          backgroundColor: success ? Colors.green : Colors.red,
        ),
      );
    }
  }

  Future<void> _cancelTimer() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Complete Timer?'),
        content: const Text('Confirm you are safe and no longer need the safety timer.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: const Text("I'm Safe"),
          ),
        ],
      ),
    );

    if (confirm == true && mounted) {
      final success = await context.read<SafetyProvider>().cancelTimer();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(success ? 'Safety timer completed' : 'Failed to complete timer'),
            backgroundColor: success ? Colors.green : Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Safety Timer'),
        backgroundColor: Colors.deepOrange,
        foregroundColor: Colors.white,
      ),
      body: Consumer<SafetyProvider>(
        builder: (context, provider, _) {
          if (provider.hasActiveTimer) {
            return _buildActiveTimer(provider);
          }
          return _buildStartTimer(provider);
        },
      ),
    );
  }

  Widget _buildStartTimer(SafetyProvider provider) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Icon(Icons.timer, size: 80, color: Colors.deepOrange),
          const SizedBox(height: 24),
          Text(
            'Lone Worker Protection',
            style: Theme.of(context).textTheme.headlineSmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'Start a safety timer when working alone. If the timer expires without being cancelled, emergency contacts will be notified.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          _buildDurationSelector(),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: provider.isLoading ? null : _startTimer,
            icon: const Icon(Icons.play_arrow),
            label: Text(provider.isLoading ? 'Starting...' : 'Start Safety Timer'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.deepOrange,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              textStyle: const TextStyle(fontSize: 18),
            ),
          ),
          const Spacer(),
          const PanicButton(),
        ],
      ),
    );
  }

  Widget _buildDurationSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Timer Duration', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          children: [30, 60, 90, 120].map((mins) {
            final isSelected = _selectedDuration == mins;
            return ChoiceChip(
              label: Text('$mins min'),
              selected: isSelected,
              onSelected: (sel) => setState(() => _selectedDuration = mins),
              selectedColor: Colors.deepOrange,
              labelStyle: TextStyle(color: isSelected ? Colors.white : null),
            );
          }).toList(),
        ),
      ],
    );
  }

  Widget _buildActiveTimer(SafetyProvider provider) {
    final timer = provider.activeTimer!;
    final isOverdue = timer.isOverdue;

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildTimerDisplay(timer, isOverdue),
          const SizedBox(height: 32),
          if (!isOverdue) ...[
            ElevatedButton.icon(
              onPressed: provider.isLoading ? null : _extendTimer,
              icon: const Icon(Icons.add_alarm),
              label: const Text('Extend +30 min'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
            const SizedBox(height: 12),
          ],
          ElevatedButton.icon(
            onPressed: provider.isLoading ? null : _cancelTimer,
            icon: const Icon(Icons.check_circle),
            label: const Text("I'm Safe - Complete Timer"),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
            ),
          ),
          if (timer.extendedCount > 0)
            Padding(
              padding: const EdgeInsets.only(top: 16),
              child: Text(
                'Extended ${timer.extendedCount} time(s)',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey[600]),
              ),
            ),
          const Spacer(),
          const PanicButton(),
        ],
      ),
    );
  }

  Widget _buildTimerDisplay(timer, bool isOverdue) {
    return Container(
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: isOverdue ? Colors.red.shade50 : Colors.orange.shade50,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isOverdue ? Colors.red : Colors.deepOrange,
          width: 3,
        ),
      ),
      child: Column(
        children: [
          Icon(
            isOverdue ? Icons.warning : Icons.timer,
            size: 48,
            color: isOverdue ? Colors.red : Colors.deepOrange,
          ),
          const SizedBox(height: 16),
          Text(
            timer.formattedRemaining,
            style: TextStyle(
              fontSize: 56,
              fontWeight: FontWeight.bold,
              color: isOverdue ? Colors.red : Colors.deepOrange,
              fontFeatures: const [FontFeature.tabularFigures()],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            isOverdue ? '⚠️ TIMER EXPIRED - CHECK IN NOW!' : 'Time Remaining',
            style: TextStyle(
              fontSize: 16,
              fontWeight: isOverdue ? FontWeight.bold : FontWeight.normal,
              color: isOverdue ? Colors.red : Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
}

