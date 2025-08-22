import 'package:flutter/material.dart';

/// メトリクス表示用カードコンポーネントの雛形
class MetricCard extends StatelessWidget {
  final String label; // 指標名
  final String value; // 指標値
  final IconData? icon; // 任意のアイコン
  final Color? backgroundColor; // 背景色

  const MetricCard({
    super.key,
    required this.label,
    required this.value,
    this.icon,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(8),
      color: backgroundColor,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            if (icon != null) ...[
              Icon(icon, size: 32),
              const SizedBox(width: 12),
            ],
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(value, style: Theme.of(context).textTheme.headlineSmall),
                Text(label),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
