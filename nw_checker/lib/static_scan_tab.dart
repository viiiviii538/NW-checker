import 'package:flutter/material.dart';

/// ダミーの静的スキャン処理（後でPython側へ接続予定）
Future<List<String>> performStaticScan() async {
  // 擬似的に時間のかかる処理を再現
  await Future.delayed(const Duration(seconds: 90));
  return [
    '=== STATIC SCAN REPORT ===',
    'No issues detected.',
  ];
}

class StaticScanTab extends StatefulWidget {
  const StaticScanTab({super.key, this.scanner = performStaticScan});

  final Future<List<String>> Function() scanner;

  @override
  State<StaticScanTab> createState() => _StaticScanTabState();
}

class _StaticScanTabState extends State<StaticScanTab> {
  bool _isLoading = false;
  bool _showOutput = false;
  List<String> _outputLines = [];

  void _startScan() async {
    setState(() {
      _isLoading = true;
      _showOutput = false;
    });

// Allow the progress indicator to render for at least one frame before
// kicking off the (potentially long) scan. Schedule the scan on the event
// queue without adding any frame time so tests can advance virtual time
// exactly to the scan duration without accounting for an extra delay.
Future<void>(() async {
  final lines = await widget.scanner();
  if (!mounted) return;
  setState(() {
    _isLoading = false;
    _showOutput = true;
    _outputLines = lines;
  });
});

    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          key: const Key('staticButton'),
          onPressed: _startScan,
          child: const Text('静的スキャンを実行'),
        ),
        if (_isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else if (_showOutput)
          Expanded(
            child: ListView(
              children: _outputLines.map((e) => Text(e)).toList(),
            ),
          ),
      ],
    );
  }
}

