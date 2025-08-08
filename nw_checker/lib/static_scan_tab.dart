import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

/// 静的スキャンAPIを呼び出し結果を返す
Future<Map<String, dynamic>> performStaticScan() async {
  try {
    final resp = await http
        .get(Uri.parse('http://localhost:8000/static_scan'))
        .timeout(const Duration(seconds: 5));
    if (resp.statusCode == 200) {
      final decoded = jsonDecode(resp.body) as Map<String, dynamic>;
      return {
        'summary': ['リスクスコア: ${decoded['risk_score'] ?? 0}'],
        'findings': decoded['findings'] ?? [],
      };
    }
  } catch (_) {}
  return {
    'summary': ['スキャン失敗'],
    'findings': [],
  };
}

/// カテゴリごとのスキャン状態。
enum ScanStatus { pending, ok, warning, error }

/// カテゴリタイルのデータモデル。
class CategoryTile {
  CategoryTile({
    required this.title,
    required this.icon,
    this.status = ScanStatus.pending,
    this.details = const [],
  });

  final String title;
  final IconData icon;
  ScanStatus status;
  List<String> details;
}

class StaticScanTab extends StatefulWidget {
  const StaticScanTab({super.key, this.scanner = performStaticScan});

  final Future<Map<String, dynamic>> Function() scanner;

  @override
  State<StaticScanTab> createState() => _StaticScanTabState();
}

class _StaticScanTabState extends State<StaticScanTab> {
  bool _isLoading = false;
  List<String> _summaryLines = [];
  late List<CategoryTile> _categories;

  @override
  void initState() {
    super.initState();
    _categories = [
      CategoryTile(title: 'Port Scan', icon: Icons.router),
      CategoryTile(title: 'SSL証明書', icon: Icons.security),
    ];
  }

  void _startScan() {
    setState(() {
      _isLoading = true;
      _summaryLines = [];
      for (final c in _categories) {
        c.status = ScanStatus.pending;
        c.details = [];
      }
    });

    // Allow progress indicator to render before kicking off scan.
    Future<void>(() async {
      final result = await widget.scanner();
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _summaryLines =
            List<String>.from(result['summary'] as List? ?? const []);

        final findings =
            (result['findings'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final portsFinding = findings.firstWhere(
          (f) => f['category'] == 'ports',
          orElse: () => <String, dynamic>{},
        );
        final openPorts =
            (portsFinding['details']?['open_ports'] as List? ?? []).cast<int>();
        _categories[0]
          ..status =
              openPorts.isEmpty ? ScanStatus.ok : ScanStatus.warning
          ..details =
              openPorts.map((p) => 'ポート $p: open').toList();

        // 既存のSSL証明書タイルはダミー情報を表示
        _categories[1]
          ..status = ScanStatus.warning
          ..details = ['証明書の期限が30日以内です'];
      });
    });
  }

  Color _statusColor(ScanStatus status) {
    switch (status) {
      case ScanStatus.warning:
        return Colors.orange;
      case ScanStatus.error:
        return Colors.red;
      case ScanStatus.ok:
        return Colors.blueGrey;
      case ScanStatus.pending:
      default:
        return Colors.grey;
    }
  }

  String _statusLabel(ScanStatus status) {
    switch (status) {
      case ScanStatus.warning:
        return '警告';
      case ScanStatus.error:
        return 'エラー';
      case ScanStatus.ok:
        return 'OK';
      case ScanStatus.pending:
      default:
        return '未実行';
    }
  }

  Widget _buildSummaryCard() {
    final lines = _summaryLines.isEmpty ? ['スキャン未実施'] : _summaryLines;
    return Card(
      color: Colors.blueGrey[50],
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: lines.map((e) => Text(e)).toList(),
        ),
      ),
    );
  }

  Widget _buildCategoryList() {
    return ListView.builder(
      itemCount: _categories.length,
      itemBuilder: (context, index) {
        final cat = _categories[index];
        return Card(
          color: Colors.blueGrey[50],
          margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: ExpansionTile(
            key: Key('category_$index'),
            leading: Icon(cat.icon, color: Colors.blueGrey),
            title: Text(cat.title),
            trailing: Chip(
              label: Text(_statusLabel(cat.status)),
              backgroundColor: _statusColor(cat.status),
            ),
            children: cat.details.map((d) => ListTile(title: Text(d))).toList(),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildSummaryCard(),
        ElevatedButton(
          key: const Key('staticButton'),
          onPressed: _startScan,
          child: const Text('スキャン開始'),
        ),
        if (_isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else
          Expanded(child: _buildCategoryList()),
      ],
    );
  }
}
