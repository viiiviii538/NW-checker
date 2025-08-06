import 'package:flutter/material.dart';
import 'services/dynamic_scan_api.dart';

class DynamicScanTab extends StatefulWidget {
  const DynamicScanTab({super.key});

  @override
  State<DynamicScanTab> createState() => _DynamicScanTabState();
}

class _DynamicScanTabState extends State<DynamicScanTab> {
  Stream<List<String>>? _resultStream;
  bool _isScanning = false;

  Future<void> _start() async {
    await startScan();
    setState(() {
      _isScanning = true;
      _resultStream = fetchResults();
    });
  }

  Future<void> _stop() async {
    await stopScan();
    setState(() {
      _isScanning = false;
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
              key: const Key('startScanButton'),
              onPressed: _isScanning ? null : _start,
              child: const Text('スキャン開始'),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              key: const Key('stopScanButton'),
              onPressed: _isScanning ? _stop : null,
              child: const Text('スキャン停止'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Expanded(
          child: _resultStream == null
              ? const Center(child: Text('スキャン結果はありません'))
              : StreamBuilder<List<String>>(
                  stream: _resultStream,
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting ||
                        (_isScanning && !snapshot.hasData)) {
                      return const Center(child: CircularProgressIndicator());
                    }
                    final lines = snapshot.data ?? [];
                    if (lines.isEmpty) {
                      return const Center(child: Text('結果がありません'));
                    }
                    return ListView.builder(
                      itemCount: lines.length,
                      itemBuilder: (context, index) {
                        return SelectableText(lines[index]);
                      },
                    );
                  },
                ),
        ),
      ],
    );
  }
}

