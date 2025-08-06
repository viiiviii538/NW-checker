import 'package:flutter/material.dart';
import 'services/dynamic_scan_api.dart';

/// 動的スキャンタブのウィジェット。
class DynamicScanTab extends StatefulWidget {
  const DynamicScanTab({super.key});

  @override
  State<DynamicScanTab> createState() => _DynamicScanTabState();
}

class _DynamicScanTabState extends State<DynamicScanTab> {
  Stream<List<String>>? _resultStream;
  bool _isScanning = false;

  Future<void> _startScan() async {
    await DynamicScanApi.startScan();
    setState(() {
      _isScanning = true;
      _resultStream = DynamicScanApi.fetchResults();
    });
  }

  Future<void> _stopScan() async {
    await DynamicScanApi.stopScan();
    setState(() {
      _isScanning = false;
      _resultStream = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            ElevatedButton(
              onPressed: _isScanning ? null : _startScan,
              child: const Text('スキャン開始'),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: _isScanning ? _stopScan : null,
              child: const Text('スキャン停止'),
            ),
          ],
        ),
        if (_isScanning)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 16),
            child: CircularProgressIndicator(),
          ),
        Expanded(
          child: StreamBuilder<List<String>>(
            stream: _resultStream,
            builder: (context, snapshot) {
              final results = snapshot.data ?? [];
              if (results.isEmpty) {
                return const SizedBox.shrink();
              }
              return ListView.builder(
                itemCount: results.length,
                itemBuilder:
                    (context, index) => ListTile(title: Text(results[index])),
              );
            },
          ),
        ),
      ],
    );
  }
}
