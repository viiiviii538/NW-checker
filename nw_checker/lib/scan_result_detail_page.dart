import 'package:flutter/material.dart';

/// スキャン結果の詳細を表示する画面。
class ScanResultDetailPage extends StatelessWidget {
  final String title;
  final String detail;

  const ScanResultDetailPage({super.key, required this.title, required this.detail});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(detail, key: const Key('detailMessage')),
      ),
    );
  }
}
