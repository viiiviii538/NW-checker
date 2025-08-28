import 'package:flutter/material.dart';
import '../models/scan_category.dart';
import '../scan_result_detail_page.dart';
import 'severity_badge.dart';

/// 動的スキャン結果一覧ウィジェット。
class DynamicScanResults extends StatelessWidget {
  final List<ScanCategory> categories;
  const DynamicScanResults({super.key, required this.categories});

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: categories.map((cat) {
        return ExpansionTile(
          leading: Icon(
            categoryIcon(cat.name),
            color: severityColor(cat.severity),
          ),
          title: Text(cat.name),
          children: cat.issues
              .map(
                (e) => ListTile(
                  title: Row(
                    children: [
                      SeverityBadge(severity: cat.severity.name),
                      const SizedBox(width: 8),
                      // 長いメッセージでも折り返せるようにする
                      Expanded(child: Text(e)),
                    ],
                  ),
                  onTap: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(
                        builder: (_) =>
                            ScanResultDetailPage(title: cat.name, detail: e),
                      ),
                    );
                  },
                ),
              )
              .toList(),
        );
      }).toList(),
    );
  }
}
