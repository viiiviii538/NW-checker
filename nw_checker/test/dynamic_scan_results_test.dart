import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/models/scan_category.dart';
import 'package:nw_checker/widgets/dynamic_scan_results.dart';
import 'package:nw_checker/widgets/severity_badge.dart';

void main() {
  testWidgets('DynamicScanResults expands categories and shows issues', (
    tester,
  ) async {
    final categories = [
      ScanCategory(name: 'protocols', severity: Severity.high, issues: ['ftp']),
    ];
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: DynamicScanResults(categories: categories)),
      ),
    );
    expect(find.text('protocols'), findsOneWidget);
    await tester.tap(find.text('protocols'));
    await tester.pumpAndSettle();
    expect(find.text('ftp'), findsOneWidget);
    expect(find.byType(SeverityBadge), findsOneWidget);
  });
}
