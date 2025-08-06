import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  Future<List<String>> mockScan() async =>
      ['=== STATIC SCAN REPORT ===', 'No issues detected.'];

  Widget buildWidget() => MaterialApp(
        home: Scaffold(body: StaticScanTab(scanner: mockScan)),
      );

  testWidgets('button tap shows progress then results', (tester) async {
    await tester.pumpWidget(buildWidget());

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('=== STATIC SCAN REPORT ==='), findsOneWidget);
    expect(find.text('No issues detected.'), findsOneWidget);
  });
}
