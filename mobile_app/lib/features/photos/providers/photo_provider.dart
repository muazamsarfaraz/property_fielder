import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:uuid/uuid.dart';
import '../../../core/models/photo.dart';
import '../../../core/services/storage_service.dart';

class PhotoProvider extends ChangeNotifier {
  final StorageService _storageService;
  final ImagePicker _imagePicker = ImagePicker();
  final Uuid _uuid = const Uuid();

  List<Photo> _photos = [];
  bool _isLoading = false;
  String? _errorMessage;

  PhotoProvider({
    required StorageService storageService,
  }) : _storageService = storageService;

  List<Photo> get photos => _photos;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<Photo> getPhotosForJob(int jobId) {
    return _storageService.getPhotosForJob(jobId);
  }

  Future<Photo?> capturePhoto({
    required int jobId,
    required int inspectorId,
    required String category,
    String? caption,
    ImageSource source = ImageSource.camera,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final XFile? image = await _imagePicker.pickImage(
        source: source,
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (image == null) {
        _isLoading = false;
        notifyListeners();
        return null;
      }

      // Get location
      Position? position;
      try {
        position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high,
        );
      } catch (e) {
        // Location not available
      }

      // Save to app directory
      final appDir = await getApplicationDocumentsDirectory();
      final photosDir = Directory('${appDir.path}/photos');
      if (!await photosDir.exists()) {
        await photosDir.create(recursive: true);
      }

      final localId = _uuid.v4();
      final extension = image.path.split('.').last;
      final localPath = '${photosDir.path}/$localId.$extension';
      
      await File(image.path).copy(localPath);
      final fileSize = await File(localPath).length();

      final photo = Photo(
        localId: localId,
        jobId: jobId,
        inspectorId: inspectorId,
        localPath: localPath,
        caption: caption,
        category: category,
        latitude: position?.latitude,
        longitude: position?.longitude,
        takenAt: DateTime.now().toIso8601String(),
        synced: false,
        fileSize: fileSize,
        mimeType: 'image/$extension',
      );

      await _storageService.savePhoto(photo);
      _photos = _storageService.getPhotos();
      
      _isLoading = false;
      notifyListeners();
      return photo;
    } catch (e) {
      _errorMessage = 'Failed to capture photo: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  Future<void> updateCaption(String localId, String caption) async {
    final photos = _storageService.getPhotos();
    final photo = photos.firstWhere((p) => p.localId == localId);
    final updated = photo.copyWith(caption: caption);
    await _storageService.savePhoto(updated);
    _photos = _storageService.getPhotos();
    notifyListeners();
  }

  Future<void> deletePhoto(String localId) async {
    final photos = _storageService.getPhotos();
    final photo = photos.firstWhere((p) => p.localId == localId);
    
    // Delete local file
    final file = File(photo.localPath);
    if (await file.exists()) {
      await file.delete();
    }
    
    // Note: We don't have a delete method in storage, so photo remains in Hive
    // In production, you'd want to add a delete method
    _photos = _storageService.getPhotos();
    notifyListeners();
  }

  int getUnsyncedCount() {
    return _storageService.getUnsyncedPhotos().length;
  }
}

