import 'package:flutter/material.dart';
import 'services/dynamic_scan_api.dart';

/// 動的スキャン結果の履歴を表示するページ。
class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  final _fromController = TextEditingController();
  final _toController = TextEditingController();
  List<String> _results = [];

  Future<void> _search() async {
    final from = DateTime.tryParse(_fromController.text);
    final to = DateTime.tryParse(_toController.text);
    if (from == null || to == null) return;
    final res = await DynamicScanApi.fetchHistory(from, to);
    setState(() {
      _results = res;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        TextField(key: const Key('fromField'), controller: _fromController),
        TextField(key: const Key('toField'), controller: _toController),
        ElevatedButton(onPressed: _search, child: const Text('検索')),
        Expanded(
          child: ListView.builder(
            itemCount: _results.length,
            itemBuilder: (context, index) => ListTile(
              title: Text(_results[index]),
            ),
          ),
        ),
      ],
    );
  }
}
