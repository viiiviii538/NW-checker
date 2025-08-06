import 'package:flutter/material.dart';
import 'services/dynamic_scan_api.dart';

/// 保存済みスキャン結果を期間指定で表示するページ。
class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  final _fromController = TextEditingController();
  final _toController = TextEditingController();
  List<String> _results = [];
  bool _loading = false;

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final from = DateTime.parse(_fromController.text);
      final to = DateTime.parse(_toController.text);
      _results = await DynamicScanApi.fetchHistory(from, to);
    } catch (_) {
      _results = [];
    }
    if (mounted) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('履歴')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              key: const Key('fromField'),
              controller: _fromController,
              decoration: const InputDecoration(labelText: 'from (YYYY-MM-DD)'),
            ),
            TextField(
              key: const Key('toField'),
              controller: _toController,
              decoration: const InputDecoration(labelText: 'to (YYYY-MM-DD)'),
            ),
            const SizedBox(height: 8),
            ElevatedButton(
              key: const Key('loadButton'),
              onPressed: _load,
              child: const Text('読み込み'),
            ),
            if (_loading) const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: CircularProgressIndicator(),
            ),
            Expanded(
              child: ListView.builder(
                itemCount: _results.length,
                itemBuilder: (context, index) => ListTile(title: Text(_results[index])),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
