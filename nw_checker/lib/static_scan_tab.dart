import 'package:flutter/material.dart';
import 'services/static_scan_api.dart';

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
          _riskScore = result['risk_score'] as int?;
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
                        ElevatedButton(
                          onPressed: _startScan,
                          child: const Text('再試行'),
                        ),
                      ],
                    ),
                  )
                : _findings.isEmpty
                ? const Center(child: Text('結果なし'))
                : ListView.builder(
                    itemCount: _findings.length + 1,
                    itemBuilder: (context, index) {
                      if (index == 0) {
                        final score = _riskScore ?? 0;
                        return ListTile(title: Text('リスクスコア: $score'));
                      }
                      final f = _findings[index - 1];
                      final category = f['category']?.toString() ?? '';
                      final score = f['score']?.toString() ?? '0';
                      return ListTile(
                        title: Text(category),
                        trailing: Text(score),
                      );
                    },
                  ),
          ),
      ],
    );
  }
}
