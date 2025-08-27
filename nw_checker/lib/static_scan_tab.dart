import 'package:flutter/material.dart';
import 'static_scan_api.dart';

/// 静的スキャンタブ。
/// ボタン押下で `/static_scan` を呼び出し結果を表示する。
class StaticScanTab extends StatefulWidget {
  const StaticScanTab({
    super.key,
    Future<Map<String, dynamic>> Function()? fetcher,
  }) : fetcher = fetcher ?? StaticScanApi.fetchScan;

  final Future<Map<String, dynamic>> Function() fetcher;

  @override
  State<StaticScanTab> createState() => _StaticScanTabState();
}

class _StaticScanTabState extends State<StaticScanTab> {
  bool _isLoading = false;
  String? _error;
  List<Map<String, dynamic>> _findings = [];
  int? _riskScore;

  void _startScan() {
    setState(() {
      _isLoading = true;
      _error = null;
      _findings = [];
      _riskScore = null;
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

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          key: const Key('staticButton'),
          onPressed: _isLoading ? null : _startScan,
          child: const Text('スキャン開始'),
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
