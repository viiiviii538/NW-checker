import 'package:flutter/material.dart';
import 'services/dynamic_scan_api.dart';

class HistoryPage extends StatefulWidget {
  const HistoryPage({super.key});

  @override
  State<HistoryPage> createState() => _HistoryPageState();
}

class _HistoryPageState extends State<HistoryPage> {
  DateTime _from = DateTime.now();
  DateTime _to = DateTime.now();
  List<String> _results = [];

  Future<void> _pickFrom() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _from,
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() => _from = picked);
    }
  }

  Future<void> _pickTo() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _to,
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (picked != null) {
      setState(() => _to = picked);
    }
  }

  Future<void> _load() async {
    final data = await DynamicScanApi.fetchHistory(_from, _to);
    setState(() => _results = data);
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextButton(onPressed: _pickFrom, child: Text(_from.toIso8601String().split('T').first)),
            const Text('〜'),
            TextButton(onPressed: _pickTo, child: Text(_to.toIso8601String().split('T').first)),
            ElevatedButton(onPressed: _load, child: const Text('読み込み')),
          ],
        ),
        Expanded(
          child: ListView.builder(
            itemCount: _results.length,
            itemBuilder: (context, index) => ListTile(title: Text(_results[index])),
          ),
        ),
      ],
    );
  }
}
