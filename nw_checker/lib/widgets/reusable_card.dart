import 'package:flutter/material.dart';

/// 再利用可能なカードコンポーネントの雛形
class ReusableCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry margin;
  final double elevation;
  final EdgeInsetsGeometry padding;

  const ReusableCard({
    super.key,
    required this.child,
    this.margin = const EdgeInsets.all(8),
    this.elevation = 2,
    this.padding = const EdgeInsets.all(16),
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: elevation,
      margin: margin,
      child: Padding(padding: padding, child: child),
    );
  }
}
