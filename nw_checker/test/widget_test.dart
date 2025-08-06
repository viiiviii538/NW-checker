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
    expect(
      tester.widget<Tab>(find.byKey(const Key('staticTab'))).text,
      '静的スキャン',
    );
    expect(find.byKey(const Key('dynamicTab')), findsOneWidget);
    expect(
      tester.widget<Tab>(find.byKey(const Key('dynamicTab'))).text,
      '動的スキャン',
    );
    expect(find.byKey(const Key('networkTab')), findsOneWidget);
    expect(
      tester.widget<Tab>(find.byKey(const Key('networkTab'))).text,
      'ネットワーク図',
    );
    expect(find.byKey(const Key('testTab')), findsOneWidget);
    expect(tester.widget<Tab>(find.byKey(const Key('testTab'))).text, 'テスト');
  });

  testWidgets('Each tab shows expected content', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    // 静的スキャン tab is selected by default
    expect(find.byKey(const Key('staticButton')), findsOneWidget);

    await tester.tap(find.byKey(const Key('dynamicTab')));
    await tester.pumpAndSettle();
    expect(find.text('スキャン開始'), findsOneWidget);
    expect(find.text('スキャン停止'), findsOneWidget);

    await tester.tap(find.byKey(const Key('networkTab')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('networkButton')), findsOneWidget);

    await tester.tap(find.byKey(const Key('testTab')));
    await tester.pumpAndSettle();
    expect(find.text('テストを実行'), findsOneWidget);
    expect(find.byType(SelectableText), findsNothing);
    await tester.tap(find.text('テストを実行'));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.byType(SelectableText), findsNothing);
    await tester.pump(const Duration(seconds: 90));
    expect(find.byType(SelectableText), findsOneWidget);
    final selectable = tester.widget<SelectableText>(
      find.byType(SelectableText),
    );
    final text = selectable.textSpan!.toPlainText();
    expect(text.contains('[SCAN] TCP 3389 OPEN'), isTrue);
  });

  testWidgets('Static button shows a SnackBar', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.text('テストを実行しました'), findsOneWidget);
  });

  testWidgets('Dynamic scan tab starts and stops', (WidgetTester tester) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('dynamicTab')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('スキャン開始'));
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pump(const Duration(seconds: 1));
    expect(find.byType(ListView), findsOneWidget);
    await tester.tap(find.text('スキャン停止'));
    await tester.pump(const Duration(milliseconds: 500));
    expect(find.byType(CircularProgressIndicator), findsNothing);
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
    expect(selectable.style?.fontFamily, 'Courier New');
    final text = selectable.textSpan!.toPlainText();
    expect(text.contains('RISK SCORE: 97/100'), isTrue);

    bool hasWarnSpan = false;
    (selectable.textSpan as TextSpan).visitChildren((span) {
      if (span is TextSpan &&
          span.text == '[WARN]' &&
          span.style?.color == const Color(0xFFB71C1C) &&
          span.style?.backgroundColor == const Color(0xFFFFEBEE)) {
        hasWarnSpan = true;
        return false;
      }
      return true;
    });
    expect(hasWarnSpan, isTrue);

    final Container container = tester.widget(
      find
          .ancestor(
            of: find.byType(SelectableText),
            matching: find.byType(Container),
          )
          .first,
    );
    final BoxDecoration deco = container.decoration as BoxDecoration;
    expect(deco.color, Colors.white);
    expect(deco.boxShadow?.isNotEmpty ?? false, isTrue);
  });
}
