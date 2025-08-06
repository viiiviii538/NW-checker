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

  testWidgets('DynamicScanTab streams report and stops', (tester) async {
    await tester.pumpWidget(_buildWidget());

    await tester.tap(find.text('スキャン開始'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(seconds: 1));
    expect(find.text('Risk Score: 87'), findsOneWidget);
    expect(find.text('Ports'), findsOneWidget);

    await tester.tap(find.text('スキャン停止'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('Risk Score: 87'), findsOneWidget);
  });

  testWidgets('summary shows export button and snackbar', (tester) async {
    await tester.pumpWidget(_buildWidget());

    await tester.tap(find.text('スキャン開始'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));
    await tester.pump();

    final pdfButton = find.text('Export PDF');
    expect(pdfButton, findsOneWidget);

    await tester.tap(pdfButton);
    await tester.pump();
    expect(find.text('PDF export not implemented'), findsOneWidget);
  });

  testWidgets('category icons use severity color and expand', (tester) async {
    await tester.pumpWidget(_buildWidget());

    await tester.tap(find.text('スキャン開始'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));
    await tester.pump();

    final iconFinder = find.byIcon(Icons.router);
    expect(iconFinder, findsOneWidget);
    final icon = tester.widget<Icon>(iconFinder);
    expect(icon.color, Colors.red);

    await tester.tap(find.text('Ports'));
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('22/tcp open'), findsOneWidget);
  });

  testWidgets('shows snackbar on alert and navigates to detail', (tester) async {
    await tester.pumpWidget(_buildWidget());

    await tester.tap(find.text('スキャン開始'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    // wait for alert
    await tester.pump(const Duration(seconds: 2));
    await tester.pump();
    expect(find.text('ALERT: Port scan detected'), findsOneWidget);

    // navigation to detail page is handled elsewhere
  });
}
