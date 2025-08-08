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
    expect(find.text('動的スキャンを実行'), findsOneWidget);

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
    await tester.pump(const Duration(seconds: 30));
    await tester.pumpAndSettle();
    expect(find.byType(SelectableText), findsOneWidget);
    final selectable = tester.widget<SelectableText>(
      find.byType(SelectableText),
    );
    final text = selectable.textSpan!.toPlainText();
    expect(text.contains('[SCAN] TCP 3389 OPEN'), isTrue);
  });

  testWidgets('Static scan button shows progress and results', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pump(const Duration(seconds: 90));
    expect(find.text('=== STATIC SCAN REPORT ==='), findsOneWidget);
  });

  testWidgets('Dynamic scan tab runs and displays JSON', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('dynamicTab')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('動的スキャンを実行'));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pump(const Duration(seconds: 2));
    await tester.pump();
    expect(find.textContaining('dynamic'), findsOneWidget);
  });

  testWidgets('Network tab runs and displays JSON', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('networkTab')));
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('networkButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pump(const Duration(seconds: 2));
    await tester.pump();
    expect(find.textContaining('network'), findsOneWidget);
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
    await tester.pump(const Duration(seconds: 30));
    await tester.pumpAndSettle();

    expect(find.byType(Scrollbar), findsOneWidget);
    final selectable = tester.widget<SelectableText>(
      find.byType(SelectableText),
    );
    expect(selectable.style?.fontFamily, 'Courier New');
    final text = selectable.textSpan!.toPlainText();
    expect(text.contains('RISK SCORE: 97/100'), isTrue);
    expect(text.contains('[INFO]'), isTrue);

    bool hasWarnSpan = false;
    bool hasInfoSpan = false;
    bool hasNoteSpan = false;
    (selectable.textSpan as TextSpan).visitChildren((span) {
      if (span is TextSpan) {
        if (span.text == '[WARN]' &&
            span.style?.color == const Color(0xFFB71C1C) &&
            span.style?.backgroundColor == const Color(0xFFFFEBEE)) {
          hasWarnSpan = true;
        } else if (span.text == '[INFO]' &&
            span.style?.color == const Color(0xFF0D47A1) &&
            span.style?.backgroundColor == const Color(0xFFE3F2FD)) {
          hasInfoSpan = true;
        } else if (span.text != null &&
            span.text!.startsWith('NOTE:') &&
            span.style?.fontStyle == FontStyle.italic) {
          hasNoteSpan = true;
        }
      }
      return true;
    });
    expect(hasWarnSpan, isTrue);
    expect(hasInfoSpan, isTrue);
    expect(hasNoteSpan, isTrue);

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

  testWidgets('Test tab shows loading text before report', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    await tester.tap(find.byKey(const Key('testTab')));
    await tester.pumpAndSettle();

    await tester.tap(find.text('テストを実行'));
    await tester.pump();

    expect(find.text('Running security scan...'), findsOneWidget);
    await tester.pump(const Duration(seconds: 30));
    await tester.pumpAndSettle();
    expect(find.text('Running security scan...'), findsNothing);
    expect(find.byType(SelectableText), findsOneWidget);
  });
}
