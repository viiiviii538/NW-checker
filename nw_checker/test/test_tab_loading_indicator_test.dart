import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:nw_checker/main.dart';

void main() {
  testWidgets('Test tab displays countdown and progress', (tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('testTab')));
    await tester.pumpAndSettle();

    await tester.tap(find.text('テストを実行'));
    await tester.pump();

    expect(find.byKey(const Key('remainingText')), findsOneWidget);
    expect(find.text('残り時間: 30 秒'), findsOneWidget);

    await tester.pump(const Duration(seconds: 5));
    expect(find.text('残り時間: 25 秒'), findsOneWidget);
    final progress = tester
        .widget<LinearProgressIndicator>(find.byType(LinearProgressIndicator))
        .value;
    expect(progress, closeTo(5 / 30, 0.01));

    await tester.pump(const Duration(seconds: 25));
    await tester.pumpAndSettle();
    expect(find.byKey(const ValueKey('report')), findsOneWidget);
  });
}
