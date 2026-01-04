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
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Take Photo'),
              onTap: () {
                Navigator.pop(context);
                _capturePhoto(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Choose from Gallery'),
              onTap: () {
                Navigator.pop(context);
                _capturePhoto(ImageSource.gallery);
              },
            ),
          ],
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
      floatingActionButton: FloatingActionButton(
        onPressed: _showCaptureOptions,
        child: const Icon(Icons.add_a_photo),
      ),
    );
  }

  Widget _buildCategorySelector() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.all(8),
      child: Row(
        children: _categories.map((cat) {
          final isSelected = _selectedCategory == cat['value'];
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: ChoiceChip(
              label: Text(cat['label']),
              avatar: Icon(cat['icon'], size: 18),
              selected: isSelected,
              onSelected: (selected) {
                if (selected) {
                  setState(() => _selectedCategory = cat['value']);
                }
              },
            ),
          );
        }).toList(),
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
                Icon(Icons.photo_library, size: 64, color: Colors.grey[400]),
                const SizedBox(height: 16),
                Text(
                  'No ${_selectedCategory} photos yet',
                  style: TextStyle(color: Colors.grey[600]),
                ),
                const SizedBox(height: 8),
                ElevatedButton.icon(
                  onPressed: _showCaptureOptions,
                  icon: const Icon(Icons.add_a_photo),
                  label: const Text('Add Photo'),
                ),
              ],
            ),
          );
        }

        return GridView.builder(
          padding: const EdgeInsets.all(8),
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
            borderRadius: BorderRadius.circular(8),
            child: Image.file(
              File(photo.localPath),
              fit: BoxFit.cover,
            ),
          ),
          if (!photo.synced)
            Positioned(
              top: 4,
              right: 4,
              child: Container(
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: Colors.orange,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: const Icon(Icons.cloud_off, size: 12, color: Colors.white),
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
          appBar: AppBar(title: Text(photo.categoryLabel)),
          body: Center(
            child: Image.file(File(photo.localPath)),
          ),
        ),
      ),
    );
  }
}

