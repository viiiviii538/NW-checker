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
    final badge = tester.widget<SeverityBadge>(find.byType(SeverityBadge));
    expect(badge.severity.toLowerCase(), 'high');
  });

  testWidgets('SeverityBadge is red for high severity', (tester) async {
    final categories = [
      ScanCategory(name: 'protocols', severity: Severity.high, issues: ['ftp']),
    ];
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: DynamicScanResults(categories: categories)),
      ),
    );
    await tester.tap(find.text('protocols'));
    await tester.pumpAndSettle();
    final container = tester.widget<Container>(
      find.descendant(
        of: find.byType(SeverityBadge),
        matching: find.byType(Container),
      ),
    );
    final decoration = container.decoration as BoxDecoration;
    expect(decoration.color, Colors.red);
  });

  testWidgets('shows Traffic category card', (tester) async {
    final categories = [
      ScanCategory(
        name: 'traffic',
        severity: Severity.low,
        issues: ['1.1.1.1'],
      ),
    ];
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: DynamicScanResults(categories: categories)),
      ),
    );
    expect(find.text('traffic'), findsOneWidget);
    await tester.tap(find.text('traffic'));
    await tester.pumpAndSettle();
    expect(find.text('1.1.1.1'), findsOneWidget);
  });
}
