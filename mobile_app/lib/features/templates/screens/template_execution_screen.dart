import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/template_provider.dart';
import '../widgets/checklist_item_widget.dart';
import '../widgets/section_progress_indicator.dart';

/// Template Execution Screen - Execute inspection checklists
class TemplateExecutionScreen extends StatefulWidget {
  final int jobId;

  const TemplateExecutionScreen({super.key, required this.jobId});

  @override
  State<TemplateExecutionScreen> createState() => _TemplateExecutionScreenState();
}

class _TemplateExecutionScreenState extends State<TemplateExecutionScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<TemplateProvider>().startInspection(widget.jobId);
    });
  }

  Future<void> _submitInspection() async {
    final provider = context.read<TemplateProvider>();
    
    // Check if all mandatory items are complete
    final template = provider.activeTemplate;
    if (template != null) {
      for (int i = 0; i < template.sections.length; i++) {
        if (!provider.isSectionComplete(i)) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Please complete all mandatory items in ${template.sections[i].name}'),
              backgroundColor: Colors.orange,
            ),
          );
          provider.goToSection(i);
          return;
        }
      }
    }

    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Submit Inspection?'),
        content: const Text('Are you sure you want to submit this inspection? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
            child: const Text('Submit'),
          ),
        ],
      ),
    );

    if (confirm == true && mounted) {
      final success = await provider.submitResponses();
      if (mounted) {
        if (success) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Inspection submitted successfully'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.pop(context, true);
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('Failed to submit: ${provider.errorMessage}'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<TemplateProvider>(
      builder: (context, provider, _) {
        if (provider.isLoading && provider.activeTemplate == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('Loading...')),
            body: const Center(child: CircularProgressIndicator()),
          );
        }

        final template = provider.activeTemplate;
        if (template == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('Inspection')),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.errorContainer.withValues(alpha: 0.3),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      Icons.error_outline,
                      size: 64,
                      color: Theme.of(context).colorScheme.error,
                    ),
                  ),
                  const SizedBox(height: 24),
                  Text(
                    provider.errorMessage ?? 'No template found',
                    style: Theme.of(context).textTheme.titleMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 24),
                  FilledButton.icon(
                    onPressed: () => provider.startInspection(widget.jobId),
                    icon: const Icon(Icons.refresh),
                    label: const Text('Retry'),
                  ),
                ],
              ),
            ),
          );
        }

        final currentSection = provider.currentSection;

        return Scaffold(
          appBar: AppBar(
            title: Text(template.name),
            actions: [
              IconButton(
                icon: const Icon(Icons.save),
                onPressed: provider.isLoading ? null : _submitInspection,
                tooltip: 'Submit Inspection',
              ),
            ],
          ),
          body: Column(
            children: [
              SectionProgressIndicator(
                sections: template.sections,
                currentIndex: provider.currentSectionIndex,
                onSectionTap: provider.goToSection,
                isSectionComplete: provider.isSectionComplete,
              ),
              Expanded(
                child: currentSection != null
                    ? _buildSectionContent(provider, currentSection)
                    : const Center(child: Text('No sections available')),
              ),
              _buildNavigationBar(provider),
            ],
          ),
        );
      },
    );
  }

  Widget _buildSectionContent(TemplateProvider provider, section) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: section.items.length,
      itemBuilder: (context, index) {
        final item = section.items[index];
        final response = provider.getResponse(item.id);
        
        return ChecklistItemWidget(
          item: item,
          response: response,
          onResponseChanged: (value, {notes, hasDefect, defectSeverity}) {
            provider.recordResponse(
              templateItemId: item.id,
              sectionId: section.id,
              value: value,
              notes: notes,
              hasDefect: hasDefect ?? false,
              defectSeverity: defectSeverity,
            );
          },
        );
      },
    );
  }

  Widget _buildNavigationBar(TemplateProvider provider) {
    final percentage = (provider.completionPercentage * 100).toInt();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Progress bar
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: provider.completionPercentage,
              backgroundColor: Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.3),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              if (provider.currentSectionIndex > 0)
                OutlinedButton.icon(
                  onPressed: provider.previousSection,
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('Previous'),
                )
              else
                const SizedBox(width: 100),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.5),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '$percentage% Complete',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                ),
              ),
              const Spacer(),
              if (!provider.isLastSection)
                FilledButton.icon(
                  onPressed: provider.nextSection,
                  icon: const Icon(Icons.arrow_forward),
                  label: const Text('Next'),
                )
              else
                FilledButton.icon(
                  onPressed: provider.isLoading ? null : _submitInspection,
                  icon: const Icon(Icons.check),
                  label: const Text('Submit'),
                  style: FilledButton.styleFrom(
                    backgroundColor: Theme.of(context).colorScheme.secondary,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }
}

