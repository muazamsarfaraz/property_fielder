import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../providers/safety_provider.dart';

/// PANIC BUTTON Widget - Immediate Emergency Response
/// 
/// HSE Compliance: Large, prominent button for lone workers to trigger
/// immediate help when in danger. Includes confirmation dialog and
/// haptic feedback.
class PanicButton extends StatelessWidget {
  const PanicButton({super.key});

  Future<void> _triggerPanic(BuildContext context) async {
    // Haptic feedback for urgency
    HapticFeedback.heavyImpact();

    // Show confirmation dialog with reason input
    final result = await showDialog<String?>(
      context: context,
      barrierDismissible: false,
      builder: (context) => _PanicConfirmDialog(),
    );

    if (result != null && context.mounted) {
      final provider = context.read<SafetyProvider>();
      final success = await provider.triggerPanic(reason: result);

      if (context.mounted) {
        if (success) {
          showDialog(
            context: context,
            barrierDismissible: false,
            builder: (context) => AlertDialog(
              backgroundColor: Colors.red,
              title: const Row(
                children: [
                  Icon(Icons.warning, color: Colors.white, size: 32),
                  SizedBox(width: 8),
                  Text('ALERT SENT', style: TextStyle(color: Colors.white)),
                ],
              ),
              content: const Text(
                '🚨 Emergency alert has been sent.\n\n'
                'Help is on the way. Stay calm and stay safe.\n\n'
                'Your location has been shared with emergency contacts.',
                style: TextStyle(color: Colors.white, fontSize: 16),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('OK', style: TextStyle(color: Colors.white, fontSize: 18)),
                ),
              ],
            ),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to send alert: ${provider.errorMessage}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<SafetyProvider>(
      builder: (context, provider, _) {
        return GestureDetector(
          onLongPress: () => _triggerPanic(context),
          child: Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(vertical: 20),
            decoration: BoxDecoration(
              color: Colors.red,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.red.withAlpha(128),
                  blurRadius: 10,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.warning_rounded, color: Colors.white, size: 40),
                const SizedBox(height: 8),
                const Text(
                  '🚨 PANIC BUTTON',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Long press for emergency',
                  style: TextStyle(
                    color: Colors.white.withAlpha(204),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _PanicConfirmDialog extends StatefulWidget {
  @override
  State<_PanicConfirmDialog> createState() => _PanicConfirmDialogState();
}

class _PanicConfirmDialogState extends State<_PanicConfirmDialog> {
  final _reasonController = TextEditingController();

  @override
  void dispose() {
    _reasonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: Colors.red.shade50,
      title: const Row(
        children: [
          Icon(Icons.warning, color: Colors.red, size: 28),
          SizedBox(width: 8),
          Text('TRIGGER PANIC?', style: TextStyle(color: Colors.red)),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'This will immediately alert your emergency contacts with your location.',
            style: TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _reasonController,
            decoration: const InputDecoration(
              labelText: 'Reason (optional)',
              hintText: 'e.g., Feeling unsafe, Medical emergency',
              border: OutlineInputBorder(),
            ),
            maxLines: 2,
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('CANCEL'),
        ),
        ElevatedButton(
          onPressed: () => Navigator.pop(context, _reasonController.text),
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.red,
            foregroundColor: Colors.white,
          ),
          child: const Text('SEND ALERT'),
        ),
      ],
    );
  }
}

