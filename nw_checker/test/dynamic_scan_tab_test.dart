import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/dynamic_scan_tab.dart';

void main() {
  testWidgets('DynamicScanTab has start and stop buttons', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: DynamicScanTab()));
    expect(find.text('スキャン開始'), findsOneWidget);
    expect(find.text('スキャン停止'), findsOneWidget);
  });
}
