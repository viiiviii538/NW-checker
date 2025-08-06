import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/dynamic_scan_tab.dart';

Widget _buildWidget() {
  return const MaterialApp(home: Scaffold(body: DynamicScanTab()));
}

void main() {
  testWidgets('DynamicScanTab has start and stop buttons', (tester) async {
    await tester.pumpWidget(_buildWidget());
    expect(find.text('スキャン開始'), findsOneWidget);
    expect(find.text('スキャン停止'), findsOneWidget);
  });

  testWidgets('DynamicScanTab streams results and stops', (tester) async {
    await tester.pumpWidget(_buildWidget());

    await tester.tap(find.text('スキャン開始'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(seconds: 1));
    expect(find.byType(ListView), findsOneWidget);
    expect(find.text('Result line 1'), findsOneWidget);

    await tester.tap(find.text('スキャン停止'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('Result line 1'), findsOneWidget);
  });
}
