import 'package:flutter/foundation.dart';
import 'package:uuid/uuid.dart';
import '../../../core/api/api_client.dart';
import '../../../core/models/inspection_template.dart';
import '../../../core/models/inspection_response.dart';
import '../../../core/services/storage_service.dart';

/// Provider for Inspection Template execution and response capture.
class TemplateProvider extends ChangeNotifier {
  final ApiClient _apiClient;
  final StorageService _storageService;
  final _uuid = const Uuid();

  List<InspectionTemplate> _templates = [];
  InspectionTemplate? _activeTemplate;
  ActiveInspection? _activeInspection;
  Map<int, InspectionResponse> _responses = {}; // keyed by templateItemId
  bool _isLoading = false;
  String? _errorMessage;
  int _currentSectionIndex = 0;

  TemplateProvider({
    required ApiClient apiClient,
    required StorageService storageService,
  })  : _apiClient = apiClient,
        _storageService = storageService;

  List<InspectionTemplate> get templates => _templates;
  InspectionTemplate? get activeTemplate => _activeTemplate;
  ActiveInspection? get activeInspection => _activeInspection;
  Map<int, InspectionResponse> get responses => _responses;
  bool get isLoading => _isLoading;
  String? get errorMessage => _errorMessage;
  int get currentSectionIndex => _currentSectionIndex;

  TemplateSection? get currentSection {
    if (_activeTemplate == null || _activeTemplate!.sections.isEmpty) return null;
    if (_currentSectionIndex >= _activeTemplate!.sections.length) return null;
    return _activeTemplate!.sections[_currentSectionIndex];
  }

  bool get isLastSection {
    if (_activeTemplate == null) return true;
    return _currentSectionIndex >= _activeTemplate!.sections.length - 1;
  }

  double get completionPercentage {
    if (_activeTemplate == null) return 0.0;
    final total = _activeTemplate!.totalItems;
    if (total == 0) return 0.0;
    return _responses.length / total;
  }

  /// Fetch all templates from server
  Future<void> fetchTemplates() async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.getTemplates();
      if (response['success'] == true) {
        final templateList = response['templates'] as List<dynamic>? ?? [];
        _templates = templateList
            .map((t) => InspectionTemplate.fromJson(t as Map<String, dynamic>))
            .toList();
      }
    } catch (e) {
      _errorMessage = 'Failed to fetch templates: $e';
    }

    _isLoading = false;
    notifyListeners();
  }

  /// Load template detail for execution
  Future<bool> loadTemplate(int templateId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.getTemplateDetail(templateId);
      if (response['success'] == true && response['template'] != null) {
        _activeTemplate = InspectionTemplate.fromJson(
          response['template'] as Map<String, dynamic>,
        );
        _currentSectionIndex = 0;
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      _errorMessage = 'Failed to load template: $e';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  /// Start inspection for a job
  Future<bool> startInspection(int jobId) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final response = await _apiClient.getJobInspection(jobId);
      if (response['success'] == true && response['inspection'] != null) {
        _activeInspection = ActiveInspection.fromJson(
          response['inspection'] as Map<String, dynamic>,
        );
        
        // Load the template
        if (_activeInspection != null) {
          await loadTemplate(_activeInspection!.templateId);
        }
        
        // Load existing responses if any
        if (response['responses'] != null) {
          final responseList = response['responses'] as List<dynamic>;
          for (final r in responseList) {
            final resp = InspectionResponse.fromJson(r as Map<String, dynamic>);
            _responses[resp.templateItemId] = resp;
          }
        }
        
        _isLoading = false;
        notifyListeners();
        return true;
      }
    } catch (e) {
      _errorMessage = 'Failed to start inspection: $e';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  /// Record a response for a template item
  void recordResponse({
    required int templateItemId,
    required int sectionId,
    String? value,
    double? numericValue,
    String? notes,
    List<String>? photoIds,
    bool hasDefect = false,
    String? defectSeverity,
  }) {
    if (_activeInspection == null) return;

    final response = InspectionResponse(
      localId: _uuid.v4(),
      inspectionId: _activeInspection!.id,
      templateItemId: templateItemId,
      sectionId: sectionId,
      value: value,
      numericValue: numericValue,
      notes: notes,
      photoIds: photoIds,
      hasDefect: hasDefect,
      defectSeverity: defectSeverity,
      respondedAt: DateTime.now().toIso8601String(),
    );

    _responses[templateItemId] = response;
    _saveResponsesLocally();
    notifyListeners();
  }

  /// Navigate to next section
  void nextSection() {
    if (!isLastSection) {
      _currentSectionIndex++;
      notifyListeners();
    }
  }

  /// Navigate to previous section
  void previousSection() {
    if (_currentSectionIndex > 0) {
      _currentSectionIndex--;
      notifyListeners();
    }
  }

  /// Go to specific section
  void goToSection(int index) {
    if (_activeTemplate != null && index >= 0 && index < _activeTemplate!.sections.length) {
      _currentSectionIndex = index;
      notifyListeners();
    }
  }

  /// Check if section is complete
  bool isSectionComplete(int sectionIndex) {
    if (_activeTemplate == null) return false;
    final section = _activeTemplate!.sections[sectionIndex];
    for (final item in section.items) {
      if (item.isMandatory && !_responses.containsKey(item.id)) {
        return false;
      }
    }
    return true;
  }

  /// Get response for a specific item
  InspectionResponse? getResponse(int templateItemId) {
    return _responses[templateItemId];
  }

  /// Submit all responses to server
  Future<bool> submitResponses() async {
    if (_activeInspection == null) return false;

    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final responseData = _responses.values.map((r) => r.toJson()).toList();
      final response = await _apiClient.submitResponses(
        _activeInspection!.id,
        {'responses': responseData},
      );

      if (response['success'] == true) {
        // Mark responses as synced
        _responses = _responses.map((key, value) => MapEntry(key, value.copyWith(synced: true)));
        _saveResponsesLocally();
        _isLoading = false;
        notifyListeners();
        return true;
      }

      _errorMessage = response['error'] as String? ?? 'Failed to submit responses';
    } catch (e) {
      _errorMessage = 'Connection error: $e';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  /// Save responses locally for offline support
  Future<void> _saveResponsesLocally() async {
    if (_activeInspection == null) return;
    final key = 'inspection_responses_${_activeInspection!.id}';
    final data = _responses.map((k, v) => MapEntry(k.toString(), v.toJson()));
    await _storageService.setSetting(key, data);
  }

  /// Load responses from local storage
  Future<void> loadLocalResponses(int inspectionId) async {
    final key = 'inspection_responses_$inspectionId';
    final data = _storageService.getSetting<Map<String, dynamic>>(key);
    if (data != null) {
      _responses = data.map((k, v) => MapEntry(
        int.parse(k),
        InspectionResponse.fromJson(v as Map<String, dynamic>),
      ));
      notifyListeners();
    }
  }

  /// Clear current inspection state
  void clearInspection() {
    _activeTemplate = null;
    _activeInspection = null;
    _responses = {};
    _currentSectionIndex = 0;
    notifyListeners();
  }
}

