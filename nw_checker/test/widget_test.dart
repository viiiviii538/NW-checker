import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:nw_checker/main.dart';

void main() {
  testWidgets('Tab bar contains four tabs with correct labels',
      (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.byType(Tab), findsNWidgets(4));
    expect(find.text('静的スキャン'), findsOneWidget);
    expect(find.text('動的スキャン'), findsOneWidget);
    expect(find.text('ネットワーク図'), findsOneWidget);
    expect(find.text('テスト'), findsOneWidget);
  });

  testWidgets('Each tab shows its button', (WidgetTester tester) async {
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
    expect(find.text('テストを開始'), findsOneWidget);
  });

  testWidgets('Pressing each button shows a SnackBar',
      (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.text('静的スキャンを実行'));
    await tester.pump();
    expect(find.text('静的スキャンを実行しました'), findsOneWidget);
    await tester.pump(const Duration(seconds: 4));

    await tester.tap(find.text('動的スキャン'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('動的スキャンを実行'));
    await tester.pump();
    expect(find.text('動的スキャンを実行しました'), findsOneWidget);
    await tester.pump(const Duration(seconds: 4));

    await tester.tap(find.text('ネットワーク図'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('ネットワーク図を表示'));
    await tester.pump();
    expect(find.text('ネットワーク図を表示しました'), findsOneWidget);
    await tester.pump(const Duration(seconds: 4));

    await tester.tap(find.text('テスト'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('テストを開始'));
    await tester.pump();
    expect(find.text('テストを開始しました'), findsOneWidget);
  });
}
