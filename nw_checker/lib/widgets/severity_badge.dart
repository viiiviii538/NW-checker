import 'package:flutter/material.dart';

/// ログの重大度を示すバッジコンポーネントの雛形。
///
/// 使用色の詳細は `docs/ui/style_guide.md` を参照。
class SeverityBadge extends StatelessWidget {
  final String severity; // 'low', 'medium', 'high'

  const SeverityBadge({super.key, required this.severity});

  Color _color() {
    switch (severity.toLowerCase()) {
      case 'high':
        return Colors.red;
      case 'medium':
        return Colors.orange;
      default:
        return Colors.green;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _color(),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        severity.toUpperCase(),
        style: const TextStyle(color: Colors.white),
      ),
    );
  }
}
