import 'package:flutter/material.dart';

/// アラート表示コンポーネント
class AlertComponent extends StatelessWidget {
  final String message;

  const AlertComponent({super.key, required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.red[100],
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          const Icon(Icons.warning, color: Colors.red),
          const SizedBox(width: 8),
          Expanded(child: Text(message)),
        ],
      ),
    );
  }
}
