import 'package:flutter/material.dart';

/// アラート表示コンポーネントの雛形
class AlertComponent extends StatelessWidget {
  final String message;
  final IconData icon;
  final Color iconColor;
  final Color? backgroundColor;

  const AlertComponent({
    super.key,
    required this.message,
    this.icon = Icons.warning,
    this.iconColor = Colors.red,
    this.backgroundColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: backgroundColor ?? Colors.red[100],
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Icon(icon, color: iconColor),
          const SizedBox(width: 8),
          Expanded(child: Text(message)),
        ],
      ),
    );
  }
}
