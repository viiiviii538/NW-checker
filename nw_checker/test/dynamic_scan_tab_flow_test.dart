import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/dynamic_scan_tab.dart';

void main() {
  Widget buildWidget() => const MaterialApp(home: Scaffold(body: DynamicScanTab()));

  testWidgets('button tap shows progress then results', (tester) async {
    await tester.pumpWidget(buildWidget());

    await tester.tap(find.text('スキャン開始'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(seconds: 1));
    expect(find.byType(ListView), findsOneWidget);
  });
}
