import 'package:flutter/material.dart';
import '../../../core/models/inspection_template.dart';

/// Section progress indicator for template execution
class SectionProgressIndicator extends StatelessWidget {
  final List<TemplateSection> sections;
  final int currentIndex;
  final Function(int) onSectionTap;
  final bool Function(int) isSectionComplete;

  const SectionProgressIndicator({
    super.key,
    required this.sections,
    required this.currentIndex,
    required this.onSectionTap,
    required this.isSectionComplete,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 80,
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(26),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 12),
        itemCount: sections.length,
        itemBuilder: (context, index) {
          final section = sections[index];
          final isCurrent = index == currentIndex;
          final isComplete = isSectionComplete(index);

          return GestureDetector(
            onTap: () => onSectionTap(index),
            child: Container(
              margin: const EdgeInsets.symmetric(horizontal: 4),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: isCurrent
                    ? Theme.of(context).primaryColor
                    : isComplete
                        ? Colors.green.withAlpha(51)
                        : Colors.grey.withAlpha(26),
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isCurrent
                      ? Theme.of(context).primaryColor
                      : isComplete
                          ? Colors.green
                          : Colors.grey.withAlpha(77),
                  width: isCurrent ? 2 : 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (isComplete)
                    const Icon(Icons.check_circle, color: Colors.green, size: 20)
                  else
                    Container(
                      width: 20,
                      height: 20,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isCurrent ? Colors.white : Colors.grey.withAlpha(77),
                      ),
                      child: Center(
                        child: Text(
                          '${index + 1}',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: isCurrent ? Theme.of(context).primaryColor : Colors.grey,
                          ),
                        ),
                      ),
                    ),
                  const SizedBox(width: 8),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        section.name,
                        style: TextStyle(
                          fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                          color: isCurrent ? Colors.white : null,
                        ),
                      ),
                      Text(
                        '${section.items.length} items',
                        style: TextStyle(
                          fontSize: 12,
                          color: isCurrent ? Colors.white70 : Colors.grey,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

