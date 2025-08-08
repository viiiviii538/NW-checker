import 'package:flutter/material.dart';

/// 再利用可能なカードコンポーネント
class ReusableCard extends StatelessWidget {
  final Widget child;

  const ReusableCard({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.all(8),
      child: Padding(padding: const EdgeInsets.all(16), child: child),
    );
  }
}
