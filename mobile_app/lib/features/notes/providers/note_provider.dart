import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:path_provider/path_provider.dart';
import 'package:uuid/uuid.dart';
import '../../../core/models/note.dart';
import '../../../core/services/storage_service.dart';

class NoteProvider extends ChangeNotifier {
  final StorageService _storageService;
  final Uuid _uuid = const Uuid();

  List<Note> _notes = [];
  bool _isLoading = false;
  String? _errorMessage;

  NoteProvider({
    required StorageService storageService,
  }) : _storageService = storageService;

  List<Note> get notes => _notes;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;

  List<Note> getNotesForJob(int jobId) {
    return _storageService.getNotesForJob(jobId);
  }

  Future<Note?> addNote({
    required int jobId,
    required int inspectorId,
    required String content,
    required String category,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final localId = _uuid.v4();

      final note = Note(
        localId: localId,
        jobId: jobId,
        inspectorId: inspectorId,
        content: content,
        category: category,
        isVoiceNote: false,
        createdAt: DateTime.now().toIso8601String(),
        synced: false,
      );

      await _storageService.saveNote(note);
      _notes = _storageService.getNotes();
      
      _isLoading = false;
      notifyListeners();
      return note;
    } catch (e) {
      _errorMessage = 'Failed to add note: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  Future<Note?> addVoiceNote({
    required int jobId,
    required int inspectorId,
    required String audioPath,
    required int audioDuration,
    required String category,
    String? transcription,
  }) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      // Copy audio file to app directory
      final appDir = await getApplicationDocumentsDirectory();
      final audioDir = Directory('${appDir.path}/audio');
      if (!await audioDir.exists()) {
        await audioDir.create(recursive: true);
      }

      final localId = _uuid.v4();
      final extension = audioPath.split('.').last;
      final localPath = '${audioDir.path}/$localId.$extension';
      
      await File(audioPath).copy(localPath);

      final note = Note(
        localId: localId,
        jobId: jobId,
        inspectorId: inspectorId,
        content: transcription ?? 'Voice note',
        category: category,
        isVoiceNote: true,
        audioPath: localPath,
        audioDuration: audioDuration,
        createdAt: DateTime.now().toIso8601String(),
        synced: false,
      );

      await _storageService.saveNote(note);
      _notes = _storageService.getNotes();
      
      _isLoading = false;
      notifyListeners();
      return note;
    } catch (e) {
      _errorMessage = 'Failed to add voice note: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  int getUnsyncedCount() {
    return _storageService.getUnsyncedNotes().length;
  }
}

