import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../routes/app_router.dart';
import '../../../core/services/storage_service.dart';
import '../../../core/di/injection.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _serverUrlController = TextEditingController();
  String _appVersion = '';

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final storageService = getIt<StorageService>();
    _serverUrlController.text = storageService.getServerUrl() ?? 'https://propertyfielder-production.up.railway.app';
    
    final packageInfo = await PackageInfo.fromPlatform();
    setState(() {
      _appVersion = '${packageInfo.version} (${packageInfo.buildNumber})';
    });
  }

  Future<void> _saveServerUrl() async {
    final storageService = getIt<StorageService>();
    await storageService.saveServerUrl(_serverUrlController.text.trim());
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Server URL saved. Please restart the app.')),
      );
    }
  }

  Future<void> _logout() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout? Any unsynced data will be lost.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Logout', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      await context.read<AuthProvider>().logout();
      Navigator.of(context).pushNamedAndRemoveUntil(AppRouter.login, (route) => false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: 8),
        children: [
          _buildSection('Account', [
            Consumer<AuthProvider>(
              builder: (context, auth, _) {
                final name = auth.userName ?? 'Inspector';
                final email = auth.userEmail;
                final hasEmail = email != null && email.isNotEmpty;

                return Card(
                  margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        Container(
                          width: 56,
                          height: 56,
                          decoration: BoxDecoration(
                            gradient: LinearGradient(
                              colors: [
                                Theme.of(context).colorScheme.primary,
                                Theme.of(context).colorScheme.secondary,
                              ],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                            shape: BoxShape.circle,
                          ),
                          child: Center(
                            child: Text(
                              name[0].toUpperCase(),
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 24,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                name,
                                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                hasEmail ? email : 'Logged in as inspector',
                                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: Theme.of(context).colorScheme.onSurfaceVariant,
                                  fontStyle: hasEmail ? FontStyle.normal : FontStyle.italic,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: OutlinedButton.icon(
                onPressed: _logout,
                icon: Icon(Icons.logout, color: Theme.of(context).colorScheme.error),
                label: Text('Logout', style: TextStyle(color: Theme.of(context).colorScheme.error)),
                style: OutlinedButton.styleFrom(
                  side: BorderSide(color: Theme.of(context).colorScheme.error),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  minimumSize: const Size(double.infinity, 48),
                ),
              ),
            ),
          ]),
          _buildSection('Server', [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: TextField(
                controller: _serverUrlController,
                decoration: InputDecoration(
                  labelText: 'Server URL',
                  hintText: 'https://your-odoo-server.com',
                  border: const OutlineInputBorder(),
                  prefixIcon: Icon(
                    Icons.cloud_outlined,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: FilledButton.icon(
                onPressed: _saveServerUrl,
                icon: const Icon(Icons.save_outlined),
                label: const Text('Save Server URL'),
                style: FilledButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  minimumSize: const Size(double.infinity, 48),
                ),
              ),
            ),
          ]),
          _buildSection('About', [
            Card(
              margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Column(
                children: [
                  ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.info_outline,
                        color: Theme.of(context).colorScheme.primary,
                      ),
                    ),
                    title: const Text('Version'),
                    subtitle: Text(_appVersion),
                  ),
                  const Divider(height: 1),
                  ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.secondaryContainer.withValues(alpha: 0.3),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Icon(
                        Icons.business_outlined,
                        color: Theme.of(context).colorScheme.secondary,
                      ),
                    ),
                    title: const Text('Property Fielder'),
                    subtitle: const Text('Field Service Inspector App'),
                  ),
                ],
              ),
            ),
          ]),
        ],
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 20, 16, 8),
          child: Text(
            title.toUpperCase(),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              letterSpacing: 1.2,
              color: Theme.of(context).colorScheme.primary,
            ),
          ),
        ),
        ...children,
        const SizedBox(height: 8),
      ],
    );
  }
}

