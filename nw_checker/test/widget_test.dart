import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:nw_checker/main.dart';

void main() {
  testWidgets('Tab bar contains four tabs with correct labels', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.byType(Tab), findsNWidgets(4));
    expect(find.byKey(const Key('tab-static')), findsOneWidget);
    expect(
      tester.widget<Tab>(find.byKey(const Key('tab-static'))).text,
      '静的スキャン',
    );
    expect(find.byKey(const Key('tab-dynamic')), findsOneWidget);
    expect(
      tester.widget<Tab>(find.byKey(const Key('tab-dynamic'))).text,
      '動的スキャン',
    );
    expect(find.byKey(const Key('tab-network')), findsOneWidget);
    expect(
      tester.widget<Tab>(find.byKey(const Key('tab-network'))).text,
      'ネットワーク図',
    );
    expect(find.byKey(const Key('tab-test')), findsOneWidget);
    expect(tester.widget<Tab>(find.byKey(const Key('tab-test'))).text, 'テスト');
  });

  testWidgets('Each tab shows its button', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // 静的スキャン tab is selected by default
    expect(find.byKey(const Key('btn-static')), findsOneWidget);

    await tester.tap(find.byKey(const Key('tab-dynamic')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('btn-dynamic')), findsOneWidget);

    await tester.tap(find.byKey(const Key('tab-network')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('btn-network')), findsOneWidget);

    await tester.tap(find.byKey(const Key('tab-test')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('btn-test')), findsOneWidget);
  });

  testWidgets('Pressing each button shows a SnackBar', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());
    final scaffold = tester.element(find.byType(Scaffold));

    await tester.tap(find.byKey(const Key('btn-static')));
    await tester.pump();
    expect(find.text('静的スキャンを実行しました'), findsOneWidget);
    ScaffoldMessenger.of(scaffold).clearSnackBars();
    await tester.pump();

    await tester.tap(find.byKey(const Key('tab-dynamic')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('btn-dynamic')));
    await tester.pump();
    expect(find.text('動的スキャンを実行しました'), findsOneWidget);
    ScaffoldMessenger.of(scaffold).clearSnackBars();
    await tester.pump();

    await tester.tap(find.byKey(const Key('tab-network')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('btn-network')));
    await tester.pump();
    expect(find.text('ネットワーク図を表示しました'), findsOneWidget);
    ScaffoldMessenger.of(scaffold).clearSnackBars();
    await tester.pump();

    await tester.tap(find.byKey(const Key('tab-test')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('btn-test')));
    await tester.pump();
    expect(find.text('テストを開始しました'), findsOneWidget);
  });
}
