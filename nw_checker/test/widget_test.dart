import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

import 'package:nw_checker/main.dart';

void main() {
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
}
