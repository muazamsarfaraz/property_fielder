import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:signature/signature.dart';
import '../providers/signature_provider.dart';
import '../../auth/providers/auth_provider.dart';

class SignatureCaptureScreen extends StatefulWidget {
  final int jobId;

  const SignatureCaptureScreen({super.key, required this.jobId});

  @override
  State<SignatureCaptureScreen> createState() => _SignatureCaptureScreenState();
}

class _SignatureCaptureScreenState extends State<SignatureCaptureScreen> {
  final SignatureController _signatureController = SignatureController(
    penStrokeWidth: 3,
    penColor: Colors.black,
    exportBackgroundColor: Colors.white,
  );

  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _roleController = TextEditingController();
  final _emailController = TextEditingController();

  @override
  void dispose() {
    _signatureController.dispose();
    _nameController.dispose();
    _roleController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _saveSignature() async {
    if (!_formKey.currentState!.validate()) return;
    if (_signatureController.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please provide a signature')),
      );
      return;
    }

    final signatureProvider = context.read<SignatureProvider>();
    final authProvider = context.read<AuthProvider>();

    final Uint8List? signatureBytes = await _signatureController.toPngBytes();
    if (signatureBytes == null) return;

    final signature = await signatureProvider.captureSignature(
      jobId: widget.jobId,
      inspectorId: authProvider.inspectorId ?? 0,
      signerName: _nameController.text.trim(),
      signatureBytes: signatureBytes,
      signerRole: _roleController.text.trim().isEmpty ? null : _roleController.text.trim(),
      signerEmail: _emailController.text.trim().isEmpty ? null : _emailController.text.trim(),
    );

    if (mounted) {
      if (signature != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Signature saved'), backgroundColor: Colors.green),
        );
        Navigator.pop(context);
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(signatureProvider.errorMessage ?? 'Failed to save signature'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Capture Signature'),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.refresh),
            label: const Text('Clear'),
            onPressed: () => _signatureController.clear(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Signer Details',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _nameController,
                        decoration: InputDecoration(
                          labelText: 'Signer Name *',
                          border: const OutlineInputBorder(),
                          prefixIcon: Icon(
                            Icons.person_outline,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                        validator: (value) {
                          if (value == null || value.trim().isEmpty) {
                            return 'Please enter the signer name';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _roleController,
                        decoration: InputDecoration(
                          labelText: 'Role (optional)',
                          border: const OutlineInputBorder(),
                          prefixIcon: Icon(
                            Icons.work_outline,
                            color: Theme.of(context).colorScheme.secondary,
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextFormField(
                        controller: _emailController,
                        decoration: InputDecoration(
                          labelText: 'Email (optional)',
                          border: const OutlineInputBorder(),
                          prefixIcon: Icon(
                            Icons.email_outlined,
                            color: Theme.of(context).colorScheme.tertiary,
                          ),
                        ),
                        keyboardType: TextInputType.emailAddress,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            Icons.draw_outlined,
                            color: Theme.of(context).colorScheme.primary,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Signature',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Container(
                        height: 200,
                        decoration: BoxDecoration(
                          border: Border.all(
                            color: Theme.of(context).colorScheme.outline,
                            width: 2,
                          ),
                          borderRadius: BorderRadius.circular(12),
                          color: Colors.white,
                        ),
                        child: ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: Signature(
                            controller: _signatureController,
                            backgroundColor: Colors.white,
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.gesture,
                            size: 16,
                            color: Theme.of(context).colorScheme.onSurfaceVariant,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'Sign in the box above',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: Theme.of(context).colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              Consumer<SignatureProvider>(
                builder: (context, provider, _) {
                  return FilledButton.icon(
                    onPressed: provider.isLoading ? null : _saveSignature,
                    icon: provider.isLoading
                        ? SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: Theme.of(context).colorScheme.onPrimary,
                            ),
                          )
                        : const Icon(Icons.save_outlined),
                    label: const Text('Save Signature'),
                    style: FilledButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      minimumSize: const Size(double.infinity, 52),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}

