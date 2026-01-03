import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:geolocator/geolocator.dart';
import 'package:path_provider/path_provider.dart';
import 'package:uuid/uuid.dart';
import '../../../core/models/signature.dart';
import '../../../core/services/storage_service.dart';

class SignatureProvider extends ChangeNotifier {
  final StorageService _storageService;
  final Uuid _uuid = const Uuid();

  List<Signature> _signatures = [];
  bool _isLoading = false;
  String? _errorMessage;

  SignatureProvider({
    required StorageService storageService,
  }) : _storageService = storageService;

  List<Signature> get signatures => _signatures;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<Signature> getSignaturesForJob(int jobId) {
    return _storageService.getSignaturesForJob(jobId);
  }

  Future<Signature?> captureSignature({
    required int jobId,
    required int inspectorId,
    required String signerName,
    required Uint8List signatureBytes,
    String? signerRole,
    String? signerEmail,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Get location
      Position? position;
      try {
        position = await Geolocator.getCurrentPosition(
          desiredAccuracy: LocationAccuracy.high,
        );
      } catch (e) {
        // Location not available
      }

      // Save signature image to app directory
      final appDir = await getApplicationDocumentsDirectory();
      final signaturesDir = Directory('${appDir.path}/signatures');
      if (!await signaturesDir.exists()) {
        await signaturesDir.create(recursive: true);
      }

      final localId = _uuid.v4();
      final localPath = '${signaturesDir.path}/$localId.png';
      
      await File(localPath).writeAsBytes(signatureBytes);

      final signature = Signature(
        localId: localId,
        jobId: jobId,
        inspectorId: inspectorId,
        signerName: signerName,
        signerRole: signerRole,
        signerEmail: signerEmail,
        localPath: localPath,
        signedAt: DateTime.now().toIso8601String(),
        latitude: position?.latitude,
        longitude: position?.longitude,
        synced: false,
      );

      await _storageService.saveSignature(signature);
      _signatures = _storageService.getSignatures();
      
      _isLoading = false;
      notifyListeners();
      return signature;
    } catch (e) {
      _errorMessage = 'Failed to capture signature: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  bool hasSignatureForJob(int jobId) {
    return _storageService.getSignaturesForJob(jobId).isNotEmpty;
  }

  int getUnsyncedCount() {
    return _storageService.getUnsyncedSignatures().length;
  }
}

