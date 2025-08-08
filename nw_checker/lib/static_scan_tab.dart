import 'package:flutter/material.dart';

/// ダミーの静的スキャン処理（後でPython側へ接続予定）
Future<List<String>> performStaticScan() async {
  // 擬似的に時間のかかる処理を再現
  await Future.delayed(const Duration(seconds: 90));
  return ['=== STATIC SCAN REPORT ===', 'No issues detected.'];
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

  final Future<List<String>> Function() scanner;

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
      CategoryTile(title: 'OS/Service', icon: Icons.computer),
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
      final lines = await widget.scanner();
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _summaryLines = lines;
        _categories[0]
          ..status = ScanStatus.ok
          ..details = ['ポート 22: open', 'ポート 80: open'];
        _categories[1]
          ..status = ScanStatus.ok
          ..details = ['OS: Linux', 'サービス: sshd 8.2'];
        _categories[2]
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
