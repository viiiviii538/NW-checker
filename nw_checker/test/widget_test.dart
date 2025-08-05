import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:nw_checker/main.dart';

void main() {
  testWidgets('Tab bar contains four tabs with correct labels', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.byType(Tab), findsNWidgets(4));
    expect(find.text('静的スキャン'), findsOneWidget);
    expect(find.text('動的スキャン'), findsOneWidget);
    expect(find.text('ネットワーク図'), findsOneWidget);
    expect(find.text('テスト'), findsOneWidget);
  });

  testWidgets('Each tab shows expected content', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // 静的スキャン tab is selected by default
    expect(find.text('静的スキャンを実行'), findsOneWidget);

    await tester.tap(find.text('動的スキャン'));
    await tester.pumpAndSettle();
    expect(find.text('動的スキャンを実行'), findsOneWidget);

    await tester.tap(find.text('ネットワーク図'));
    await tester.pumpAndSettle();
    expect(find.text('ネットワーク図を表示'), findsOneWidget);

    await tester.tap(find.text('テスト'));
    await tester.pumpAndSettle();
    expect(find.text('テストを実行'), findsOneWidget);
    expect(find.byType(SelectableText), findsNothing);
    await tester.tap(find.text('テストを実行'));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.byType(SelectableText), findsNothing);
    await tester.pump(const Duration(seconds: 90));
    expect(find.byType(SelectableText), findsOneWidget);
    expect(find.textContaining('[SCAN] TCP 3389 OPEN'), findsOneWidget);
  });

  testWidgets('Static button shows a SnackBar', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('静的スキャンを実行'));
    await tester.pump();
    expect(find.text('静的スキャンを実行しました'), findsOneWidget);
  });

  testWidgets('Dynamic button shows a SnackBar', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('動的スキャン'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('動的スキャンを実行'));
    await tester.pump();
    expect(find.text('動的スキャンを実行しました'), findsOneWidget);
  });

  testWidgets('Network button shows a SnackBar', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('ネットワーク図'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('ネットワーク図を表示'));
    await tester.pump();
    expect(find.text('ネットワーク図を表示しました'), findsOneWidget);
  });

  testWidgets('Test tab shows monospaced diagnostic text', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('テスト'));
    await tester.pumpAndSettle();

    // Initially no output is shown
    expect(find.byType(SelectableText), findsNothing);

    await tester.tap(find.text('テストを実行'));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pump(const Duration(seconds: 90));

    expect(find.byType(Scrollbar), findsOneWidget);
    final selectable = tester.widget<SelectableText>(
      find.byType(SelectableText),
    );
    expect(selectable.style?.fontFamily, 'monospace');
    expect(selectable.data!.contains('RISK SCORE: 92/100'), isTrue);
  });
}
