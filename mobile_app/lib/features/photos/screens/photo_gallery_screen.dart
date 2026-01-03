import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/photo_provider.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../core/models/photo.dart';

class PhotoGalleryScreen extends StatefulWidget {
  final int jobId;

  const PhotoGalleryScreen({super.key, required this.jobId});

  @override
  State<PhotoGalleryScreen> createState() => _PhotoGalleryScreenState();
}

class _PhotoGalleryScreenState extends State<PhotoGalleryScreen> {
  String _selectedCategory = 'before';

  final List<Map<String, dynamic>> _categories = [
    {'value': 'before', 'label': 'Before', 'icon': Icons.photo_camera_back},
    {'value': 'during', 'label': 'During', 'icon': Icons.camera},
    {'value': 'after', 'label': 'After', 'icon': Icons.photo_camera_front},
    {'value': 'issue', 'label': 'Issue', 'icon': Icons.warning},
    {'value': 'document', 'label': 'Document', 'icon': Icons.description},
  ];

  Future<void> _capturePhoto(ImageSource source) async {
    final photoProvider = context.read<PhotoProvider>();
    final authProvider = context.read<AuthProvider>();

    await photoProvider.capturePhoto(
      jobId: widget.jobId,
      inspectorId: authProvider.inspectorId ?? 0,
      category: _selectedCategory,
      source: source,
    );
  }

  void _showCaptureOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.onSurfaceVariant.withValues(alpha: 0.3),
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Add Photo',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 20),
              Row(
                children: [
                  Expanded(
                    child: _buildCaptureOption(
                      Icons.camera_alt_outlined,
                      'Camera',
                      Theme.of(context).colorScheme.primary,
                      () {
                        Navigator.pop(context);
                        _capturePhoto(ImageSource.camera);
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildCaptureOption(
                      Icons.photo_library_outlined,
                      'Gallery',
                      Theme.of(context).colorScheme.secondary,
                      () {
                        Navigator.pop(context);
                        _capturePhoto(ImageSource.gallery);
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCaptureOption(IconData icon, String label, Color color, VoidCallback onTap) {
    return Material(
      color: color.withValues(alpha: 0.1),
      borderRadius: BorderRadius.circular(16),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
          child: Column(
            children: [
              Icon(icon, size: 40, color: color),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Photos'),
      ),
      body: Column(
        children: [
          _buildCategorySelector(),
          Expanded(child: _buildPhotoGrid()),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showCaptureOptions,
        icon: const Icon(Icons.add_a_photo_outlined),
        label: const Text('Add Photo'),
      ),
    );
  }

  Widget _buildCategorySelector() {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        child: Row(
          children: _categories.map((cat) {
            final isSelected = _selectedCategory == cat['value'];
            final color = Theme.of(context).colorScheme.primary;
            return Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: FilterChip(
                label: Text(cat['label']),
                avatar: Icon(
                  cat['icon'] as IconData,
                  size: 18,
                  color: isSelected ? color : Theme.of(context).colorScheme.onSurfaceVariant,
                ),
                selected: isSelected,
                showCheckmark: false,
                onSelected: (selected) {
                  if (selected) {
                    setState(() => _selectedCategory = cat['value'] as String);
                  }
                },
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildPhotoGrid() {
    return Consumer<PhotoProvider>(
      builder: (context, photoProvider, _) {
        final photos = photoProvider.getPhotosForJob(widget.jobId)
            .where((p) => p.category == _selectedCategory)
            .toList();

        if (photos.isEmpty) {
          return Center(
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
                    Icons.photo_library_outlined,
                    size: 64,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
                const SizedBox(height: 24),
                Text(
                  'No $_selectedCategory photos yet',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Tap the button below to add a photo',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Theme.of(context).colorScheme.onSurfaceVariant.withValues(alpha: 0.7),
                  ),
                ),
              ],
            ),
          );
        }

        return GridView.builder(
          padding: const EdgeInsets.all(12),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 3,
            crossAxisSpacing: 8,
            mainAxisSpacing: 8,
          ),
          itemCount: photos.length,
          itemBuilder: (context, index) {
            final photo = photos[index];
            return _buildPhotoTile(photo);
          },
        );
      },
    );
  }

  Widget _buildPhotoTile(Photo photo) {
    return GestureDetector(
      onTap: () => _showPhotoDetail(photo),
      child: Stack(
        fit: StackFit.expand,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: Image.file(
              File(photo.localPath),
              fit: BoxFit.cover,
            ),
          ),
          if (!photo.synced)
            Positioned(
              top: 6,
              right: 6,
              child: Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.tertiary,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: const Icon(Icons.cloud_off, size: 14, color: Colors.white),
              ),
            ),
        ],
      ),
    );
  }

  void _showPhotoDetail(Photo photo) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => Scaffold(
          backgroundColor: Colors.black,
          appBar: AppBar(
            backgroundColor: Colors.black,
            foregroundColor: Colors.white,
            title: Text(photo.categoryLabel),
          ),
          body: Center(
            child: InteractiveViewer(
              child: Image.file(File(photo.localPath)),
            ),
          ),
        ),
      ),
    );
  }
}

