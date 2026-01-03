import 'package:flutter/material.dart';
import '../../../core/models/inspection_template.dart';
import '../../../core/models/inspection_response.dart';

/// Widget for rendering different checklist item types
class ChecklistItemWidget extends StatefulWidget {
  final TemplateItem item;
  final InspectionResponse? response;
  final Function(String?, {String? notes, bool? hasDefect, String? defectSeverity}) onResponseChanged;

  const ChecklistItemWidget({
    super.key,
    required this.item,
    this.response,
    required this.onResponseChanged,
  });

  @override
  State<ChecklistItemWidget> createState() => _ChecklistItemWidgetState();
}

class _ChecklistItemWidgetState extends State<ChecklistItemWidget> {
  final _notesController = TextEditingController();
  bool _showNotes = false;

  @override
  void initState() {
    super.initState();
    _notesController.text = widget.response?.notes ?? '';
    _showNotes = widget.response?.notes?.isNotEmpty ?? false;
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          if (widget.item.isMandatory)
                            const Text('* ', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                          Expanded(
                            child: Text(
                              widget.item.question,
                              style: Theme.of(context).textTheme.titleMedium,
                            ),
                          ),
                        ],
                      ),
                      if (widget.item.helpText != null) ...[
                        const SizedBox(height: 4),
                        Text(
                          widget.item.helpText!,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(color: Colors.grey[600]),
                        ),
                      ],
                    ],
                  ),
                ),
                IconButton(
                  icon: Icon(_showNotes ? Icons.note : Icons.note_add_outlined),
                  onPressed: () => setState(() => _showNotes = !_showNotes),
                  tooltip: 'Add notes',
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildResponseInput(),
            if (_showNotes) ...[
              const SizedBox(height: 12),
              TextField(
                controller: _notesController,
                decoration: const InputDecoration(
                  labelText: 'Notes',
                  border: OutlineInputBorder(),
                  hintText: 'Add any additional notes...',
                ),
                maxLines: 2,
                onChanged: (value) {
                  widget.onResponseChanged(
                    widget.response?.value,
                    notes: value,
                    hasDefect: widget.response?.hasDefect,
                    defectSeverity: widget.response?.defectSeverity,
                  );
                },
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResponseInput() {
    switch (widget.item.responseType) {
      case 'yes_no':
        return _buildYesNoInput();
      case 'severity':
        return _buildSeverityInput();
      case 'numeric':
        return _buildNumericInput();
      case 'text':
        return _buildTextInput();
      default:
        return _buildYesNoInput();
    }
  }

  Widget _buildYesNoInput() {
    final value = widget.response?.value;
    return Row(
      children: [
        Expanded(
          child: _buildChoiceButton('Yes', value == 'yes', Colors.green, () {
            widget.onResponseChanged('yes', notes: _notesController.text);
          }),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildChoiceButton('No', value == 'no', Colors.red, () {
            widget.onResponseChanged('no', notes: _notesController.text, hasDefect: true);
          }),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildChoiceButton('N/A', value == 'na', Colors.grey, () {
            widget.onResponseChanged('na', notes: _notesController.text);
          }),
        ),
      ],
    );
  }

  Widget _buildSeverityInput() {
    final value = widget.response?.value;
    return Wrap(
      spacing: 8,
      children: [
        _buildSeverityChip('Good', value == 'good', Colors.green),
        _buildSeverityChip('Minor', value == 'minor', Colors.orange),
        _buildSeverityChip('Major', value == 'major', Colors.deepOrange),
        _buildSeverityChip('Critical', value == 'critical', Colors.red),
      ],
    );
  }

  Widget _buildSeverityChip(String label, bool selected, Color color) {
    return ChoiceChip(
      label: Text(label),
      selected: selected,
      selectedColor: color.withAlpha(51),
      labelStyle: TextStyle(color: selected ? color : null, fontWeight: selected ? FontWeight.bold : null),
      onSelected: (_) {
        final hasDefect = label != 'Good';
        widget.onResponseChanged(label.toLowerCase(), notes: _notesController.text, hasDefect: hasDefect, defectSeverity: hasDefect ? label.toLowerCase() : null);
      },
    );
  }

  Widget _buildNumericInput() {
    return TextField(
      keyboardType: TextInputType.number,
      decoration: const InputDecoration(labelText: 'Enter value', border: OutlineInputBorder()),
      onChanged: (value) => widget.onResponseChanged(value, notes: _notesController.text),
    );
  }

  Widget _buildTextInput() {
    return TextField(
      decoration: const InputDecoration(labelText: 'Enter response', border: OutlineInputBorder()),
      maxLines: 2,
      onChanged: (value) => widget.onResponseChanged(value, notes: _notesController.text),
    );
  }

  Widget _buildChoiceButton(String label, bool selected, Color color, VoidCallback onTap) {
    return OutlinedButton(
      onPressed: onTap,
      style: OutlinedButton.styleFrom(
        backgroundColor: selected ? color.withAlpha(51) : null,
        side: BorderSide(color: selected ? color : Colors.grey),
        padding: const EdgeInsets.symmetric(vertical: 12),
      ),
      child: Text(label, style: TextStyle(color: selected ? color : null, fontWeight: selected ? FontWeight.bold : null)),
    );
  }
}

