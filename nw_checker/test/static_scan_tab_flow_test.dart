import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  Future<Map<String, dynamic>> mockScan() async {
    await Future.delayed(const Duration(milliseconds: 10));
    return {
      'summary': ['=== STATIC SCAN REPORT ===', 'No issues detected.'],
      'findings': [
        {
          'category': 'ports',
          'details': {
            'open_ports': [22, 80],
          },
        },
      ],
    };
  }

  Widget buildWidget() =>
      MaterialApp(home: Scaffold(body: StaticScanTab(scanner: mockScan)));

  testWidgets('button tap shows progress then results and categories', (
    tester,
  ) async {
    await tester.pumpWidget(buildWidget());

    // Initial status badges
    expect(find.text('未実行'), findsNWidgets(2));

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('=== STATIC SCAN REPORT ==='), findsOneWidget);
    expect(find.text('No issues detected.'), findsOneWidget);

    // Category order
    final portDy = tester.getTopLeft(find.text('Port Scan')).dy;
    final sslDy = tester.getTopLeft(find.text('SSL証明書')).dy;
    expect(portDy < sslDy, isTrue);

    // Status badges after scan
    expect(find.text('警告'), findsNWidgets(2));

    await tester.tap(find.text('Port Scan'));
    await tester.pumpAndSettle();
    expect(find.text('ポート 22: open'), findsOneWidget);
    expect(find.text('ポート 80: open'), findsOneWidget);

    await tester.tap(find.text('SSL証明書'));
    await tester.pumpAndSettle();
    expect(find.text('証明書の期限が30日以内です'), findsOneWidget);
  });
}
