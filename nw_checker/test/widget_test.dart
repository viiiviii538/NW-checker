import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:nw_checker/main.dart';

void main() {
  testWidgets('Tab bar contains four tabs with correct labels', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.byType(Tab), findsNWidgets(4));
    expect(find.byKey(const Key('staticTab')), findsOneWidget);
    expect(tester.widget<Tab>(find.byKey(const Key('staticTab'))).text,
        '静的スキャン');
    expect(find.byKey(const Key('dynamicTab')), findsOneWidget);
    expect(tester.widget<Tab>(find.byKey(const Key('dynamicTab'))).text,
        '動的スキャン');
    expect(find.byKey(const Key('networkTab')), findsOneWidget);
    expect(tester.widget<Tab>(find.byKey(const Key('networkTab'))).text,
        'ネットワーク図');
    expect(find.byKey(const Key('testTab')), findsOneWidget);
    expect(
        tester.widget<Tab>(find.byKey(const Key('testTab'))).text, 'テスト');
  });

  testWidgets('Each tab shows expected content', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // 静的スキャン tab is selected by default
    expect(find.byKey(const Key('staticButton')), findsOneWidget);

    await tester.tap(find.byKey(const Key('dynamicTab')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('dynamicButton')), findsOneWidget);

    await tester.tap(find.byKey(const Key('networkTab')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('networkButton')), findsOneWidget);

    await tester.tap(find.byKey(const Key('testTab')));
    await tester.pumpAndSettle();
    expect(find.byType(SelectableText), findsOneWidget);
    final selectable =
        tester.widget<SelectableText>(find.byType(SelectableText));
    expect(selectable.data!.contains('[SCAN] TCP 3389 OPEN'), isTrue);
  });

  testWidgets('Static button shows a SnackBar', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.text('静的スキャンを実行しました'), findsOneWidget);
  });

  testWidgets('Dynamic button shows a SnackBar', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('dynamicTab')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('dynamicButton')));
    await tester.pump();
    expect(find.text('動的スキャンを実行しました'), findsOneWidget);
  });

  testWidgets('Network button shows a SnackBar', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('networkTab')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('networkButton')));
    await tester.pump();
    expect(find.text('ネットワーク図を表示しました'), findsOneWidget);
  });

  testWidgets('Test tab shows monospaced diagnostic text', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('testTab')));
    await tester.pumpAndSettle();

    expect(find.byType(Scrollbar), findsOneWidget);
    final selectable = tester.widget<SelectableText>(
      find.byType(SelectableText),
    );
    expect(selectable.style?.fontFamily, 'monospace');
    expect(selectable.data!.contains('RISK SCORE: 92/100'), isTrue);
  });
}
