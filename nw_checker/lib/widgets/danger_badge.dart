import 'package:flutter/material.dart';

/// 危険を示す赤色バッジ
class DangerBadge extends StatelessWidget {
  final EdgeInsetsGeometry padding;
  const DangerBadge({super.key, this.padding = const EdgeInsets.symmetric(horizontal: 8, vertical: 4)});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: padding,
      decoration: BoxDecoration(
        color: Colors.red,
        borderRadius: BorderRadius.circular(4),
      ),
      child: const Text(
        'DANGER',
        style: TextStyle(color: Colors.white),
      ),
    );
  }
}
