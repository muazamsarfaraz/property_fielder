import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/note_provider.dart';
import '../../auth/providers/auth_provider.dart';
import '../../../core/models/note.dart';

class NoteListScreen extends StatefulWidget {
  final int jobId;

  const NoteListScreen({super.key, required this.jobId});

  @override
  State<NoteListScreen> createState() => _NoteListScreenState();
}

class _NoteListScreenState extends State<NoteListScreen> {
  final _noteController = TextEditingController();
  String _selectedCategory = 'general';

  final List<Map<String, dynamic>> _categories = [
    {'value': 'general', 'label': 'General', 'icon': Icons.note},
    {'value': 'issue', 'label': 'Issue', 'icon': Icons.warning},
    {'value': 'follow_up', 'label': 'Follow-up', 'icon': Icons.schedule},
    {'value': 'customer', 'label': 'Customer', 'icon': Icons.person},
    {'value': 'internal', 'label': 'Internal', 'icon': Icons.lock},
  ];

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }

  Future<void> _addNote() async {
    if (_noteController.text.trim().isEmpty) return;

    final noteProvider = context.read<NoteProvider>();
    final authProvider = context.read<AuthProvider>();

    await noteProvider.addNote(
      jobId: widget.jobId,
      inspectorId: authProvider.inspectorId ?? 0,
      content: _noteController.text.trim(),
      category: _selectedCategory,
    );

    _noteController.clear();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notes'),
      ),
      body: Column(
        children: [
          Expanded(child: _buildNoteList()),
          _buildNoteInput(),
        ],
      ),
    );
  }

  Widget _buildNoteList() {
    return Consumer<NoteProvider>(
      builder: (context, noteProvider, _) {
        final notes = noteProvider.getNotesForJob(widget.jobId);

        if (notes.isEmpty) {
          return const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.note, size: 64, color: Colors.grey),
                SizedBox(height: 16),
                Text('No notes yet', style: TextStyle(color: Colors.grey)),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16),
          itemCount: notes.length,
          itemBuilder: (context, index) {
            final note = notes[index];
            return _buildNoteCard(note);
          },
        );
      },
    );
  }

  Widget _buildNoteCard(Note note) {
    final category = _categories.firstWhere(
      (c) => c['value'] == note.category,
      orElse: () => _categories.first,
    );

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(category['icon'], size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  category['label'],
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                    fontWeight: FontWeight.w500,
                  ),
                ),
                const Spacer(),
                if (!note.synced)
                  const Icon(Icons.cloud_off, size: 14, color: Colors.orange),
                const SizedBox(width: 4),
                Text(
                  _formatDate(note.createdAt),
                  style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(note.content),
            if (note.isVoiceNote) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.mic, size: 16, color: Colors.blue),
                  const SizedBox(width: 4),
                  Text(
                    'Voice note (${note.audioDuration ?? 0}s)',
                    style: const TextStyle(fontSize: 12, color: Colors.blue),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildNoteInput() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.1),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: _categories.map((cat) {
                final isSelected = _selectedCategory == cat['value'];
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(cat['label']),
                    selected: isSelected,
                    onSelected: (selected) {
                      if (selected) setState(() => _selectedCategory = cat['value']);
                    },
                  ),
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _noteController,
                  decoration: const InputDecoration(
                    hintText: 'Add a note...',
                    border: OutlineInputBorder(),
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                  maxLines: 2,
                  minLines: 1,
                ),
              ),
              const SizedBox(width: 8),
              IconButton(
                onPressed: _addNote,
                icon: const Icon(Icons.send),
                color: Theme.of(context).primaryColor,
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _formatDate(String isoDate) {
    try {
      final date = DateTime.parse(isoDate);
      return '${date.day}/${date.month} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return isoDate;
    }
  }
}

