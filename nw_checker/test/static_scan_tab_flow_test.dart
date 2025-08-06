import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  Widget buildWidget() =>
      const MaterialApp(home: Scaffold(body: StaticScanTab()));

  testWidgets('button tap shows progress then results', (tester) async {
    await tester.pumpWidget(buildWidget());

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(seconds: 90));
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('=== STATIC SCAN REPORT ==='), findsOneWidget);
    expect(find.text('No issues detected.'), findsOneWidget);
  });
}
