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
        children: [
          _buildSection('Account', [
            Consumer<AuthProvider>(
              builder: (context, auth, _) {
                final name = auth.userName ?? 'Inspector';
                final email = auth.userEmail;
                final hasEmail = email != null && email.isNotEmpty;

                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    child: Text(
                      name[0].toUpperCase(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  title: Text(
                    name,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                  subtitle: hasEmail
                      ? Text(email)
                      : Text(
                          'Logged in as inspector',
                          style: TextStyle(
                            fontStyle: FontStyle.italic,
                            color: Theme.of(context).colorScheme.onSurfaceVariant,
                          ),
                        ),
                );
              },
            ),
            ListTile(
              leading: Icon(Icons.logout, color: Theme.of(context).colorScheme.error),
              title: Text('Logout', style: TextStyle(color: Theme.of(context).colorScheme.error)),
              onTap: _logout,
            ),
          ]),
          _buildSection('Server', [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: TextField(
                controller: _serverUrlController,
                decoration: const InputDecoration(
                  labelText: 'Server URL',
                  hintText: 'https://your-odoo-server.com',
                  border: OutlineInputBorder(),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: ElevatedButton(
                onPressed: _saveServerUrl,
                child: const Text('Save Server URL'),
              ),
            ),
          ]),
          _buildSection('About', [
            ListTile(
              leading: const Icon(Icons.info),
              title: const Text('Version'),
              subtitle: Text(_appVersion),
            ),
            const ListTile(
              leading: Icon(Icons.business),
              title: Text('Property Fielder'),
              subtitle: Text('Field Service Inspector App'),
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
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: Theme.of(context).primaryColor,
            ),
          ),
        ),
        ...children,
        const Divider(),
      ],
    );
  }
}

