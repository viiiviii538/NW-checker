import 'package:flutter/material.dart';
import 'static_scan_api.dart';

/// 静的スキャンタブ。
/// ボタン押下で `/static_scan` を呼び出し結果を表示する。
class StaticScanTab extends StatefulWidget {
  const StaticScanTab({
    super.key,
    Future<Map<String, dynamic>> Function()? fetcher,
    Future<String> Function()? reportFetcher,
  }) : fetcher = fetcher ?? StaticScanApi.fetchScan,
       reportFetcher = reportFetcher ?? StaticScanApi.fetchReport;

  final Future<Map<String, dynamic>> Function() fetcher;
  final Future<String> Function() reportFetcher;

  @override
  State<StaticScanTab> createState() => _StaticScanTabState();
}

class _StaticScanTabState extends State<StaticScanTab> {
  bool _isLoading = false;
  String? _error;
  List<Map<String, dynamic>> _findings = [];
  int? _riskScore;
  String? _reportPath;

  void _startScan() {
    setState(() {
      _isLoading = true;
      _error = null;
      _findings = [];
      _riskScore = null;
      _reportPath = null;
    });

    // UI が進捗表示を描画できるように次フレームで実行
    Future<void>(() async {
      try {
        final result = await widget.fetcher();
        if (!mounted) return;
        setState(() {
          _isLoading = false;
          _findings =
              (result['findings'] as List?)?.cast<Map<String, dynamic>>() ?? [];
          _riskScore = result['risk_score'] as int? ?? 0;
        });
      } catch (e) {
        if (!mounted) return;
        setState(() {
          _isLoading = false;
          _error = e.toString();
        });
      }
    });
  }

  void _generateReport() async {
    // Scan結果とは独立してレポートのみ生成する
    setState(() {
      _reportPath = null;
    });
    try {
      final path = await widget.reportFetcher();
      if (!mounted) return;
      setState(() {
        _reportPath = path;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _reportPath = 'error';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          children: [
            ElevatedButton(
              key: const Key('staticButton'),
              onPressed: _isLoading ? null : _startScan,
              child: const Text('スキャン開始'),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              key: const Key('reportButton'),
              onPressed: _generateReport,
              child: const Text('PDF生成'),
            ),
          ],
        ),
        if (_isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else
          Expanded(
            child: _error != null
                ? Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text('スキャン失敗: $_error'),
                        const SizedBox(height: 8),
                        // エラーが発生した場合は再試行ボタンを表示
                        ElevatedButton(
                          onPressed: _startScan,
                          child: const Text('再試行'),
                        ),
                      ],
                    ),
                  )
                : _findings.isEmpty
                ? const Center(child: Text('結果なし'))
                : Column(
                    children: [
                      if (_riskScore != null)
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Card(
                            color: _colorForScore(_riskScore!),
                            child: ListTile(
                              title: Text('リスクスコア: ${_riskScore ?? 0}'),
                            ),
                          ),
                        ),
                      Expanded(
                        child: ListView.builder(
                          itemCount: _findings.length,
                          itemBuilder: (context, index) {
                            final f = _findings[index];
                            final category = f['category']?.toString() ?? '';
                            final score = f['score'] as int? ?? 0;
                            return Card(
                              color: _colorForScore(score),
                              child: ListTile(
                                title: Text(category),
                                trailing: Text(score.toString()),
                              ),
                            );
                          },
                        ),
                      ),
                      if (_reportPath != null)
                        Padding(
                          padding: const EdgeInsets.all(8.0),
                          child: Text('PDF: $_reportPath'),
                        ),
                    ],
                  ),
          ),
      ],
    );
  }

  Color _colorForScore(int score) {
    if (score >= 5) return Colors.red.shade100;
    if (score >= 1) return Colors.yellow.shade100;
    return Colors.green.shade100;
  }
}
