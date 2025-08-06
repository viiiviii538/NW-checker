import 'scan_category.dart';

/// スキャンレポート全体。
class ScanReport {
  final int riskScore;
  final List<ScanCategory> categories;

  ScanReport({required this.riskScore, required this.categories});

  factory ScanReport.fromJson(Map<String, dynamic> json) {
    final cats =
        (json['categories'] as List<dynamic>? ?? [])
            .map((e) => ScanCategory.fromJson(e as Map<String, dynamic>))
            .toList();
    return ScanReport(
      riskScore: json['riskScore'] as int? ?? 0,
      categories: cats,
    );
  }
}
