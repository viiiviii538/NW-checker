import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  testWidgets('shows findings after successful scan', (tester) async {
    Future<Map<String, dynamic>> mockFetch() async {
      await Future.delayed(const Duration(milliseconds: 10));
      return {
        'risk_score': 2,
        'findings': [
          {'category': 'a', 'score': 1},
          {'category': 'b', 'score': 1},
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: StaticScanTab(fetcher: mockFetch)),
      ),
    );

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle();

    expect(find.text('リスクスコア: 2'), findsOneWidget);
    expect(find.text('a'), findsOneWidget);
    expect(find.text('b'), findsOneWidget);
    expect(find.text('1'), findsNWidgets(2));
  });

  testWidgets('shows error and allows retry', (tester) async {
    int calls = 0;
    Future<Map<String, dynamic>> mockFetch() async {
      calls++;
      if (calls == 1) {
        throw Exception('network');
      }
      return {
        'risk_score': 0,
        'findings': [
          {'category': 'ok', 'score': 0},
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: StaticScanTab(fetcher: mockFetch)),
      ),
    );

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pumpAndSettle();

    expect(find.textContaining('network'), findsOneWidget);
    expect(find.text('再試行'), findsOneWidget);

    await tester.tap(find.text('再試行'));
    await tester.pumpAndSettle();

    expect(find.text('ok'), findsOneWidget);
  });

  testWidgets('shows placeholder when no findings', (tester) async {
    Future<Map<String, dynamic>> mockFetch() async {
      return {'risk_score': 0, 'findings': []};
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: StaticScanTab(fetcher: mockFetch)),
      ),
    );

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pumpAndSettle();

    expect(find.text('結果なし'), findsOneWidget);
    expect(find.textContaining('リスクスコア'), findsNothing);
  });
  testWidgets('disables button while loading', (tester) async {
    final completer = Completer<Map<String, dynamic>>();
    var calls = 0;

    Future<Map<String, dynamic>> mockFetch() {
      calls++;
      return completer.future;
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: StaticScanTab(fetcher: mockFetch)),
      ),
    );

    final button = find.byKey(const Key('staticButton'));

    // ボタンが初期状態で有効か確認
    expect(tester.widget<ElevatedButton>(button).onPressed, isNotNull);

    await tester.tap(button);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 1));

    // 読み込み中はボタンが無効化されている
    expect(tester.widget<ElevatedButton>(button).onPressed, isNull);

    // 読み込み中に再度タップしても呼び出し回数は増えない
    await tester.tap(button);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 1));
    expect(calls, 1);

    completer.complete({'risk_score': 0, 'findings': []});
    await tester.pumpAndSettle();

    // 完了後はボタンが再び有効になる
    expect(tester.widget<ElevatedButton>(button).onPressed, isNotNull);

    await tester.tap(button);
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 1));
    expect(calls, 2);
  });
  testWidgets('defaults risk score to 0 when missing', (tester) async {
    Future<Map<String, dynamic>> mockFetch() async {
      return {
        'findings': [
          {'category': 'c', 'score': 1},
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: StaticScanTab(fetcher: mockFetch)),
      ),
    );

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pumpAndSettle();

    expect(find.text('リスクスコア: 0'), findsOneWidget);
    expect(find.text('c'), findsOneWidget);
  });

  testWidgets('tiles are color coded by score', (tester) async {
    Future<Map<String, dynamic>> mockFetch() async {
      return {
        'risk_score': 7,
        'findings': [
          {'category': 'ok', 'score': 0},
          {'category': 'warn', 'score': 2},
          {'category': 'bad', 'score': 5},
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: StaticScanTab(fetcher: mockFetch)),
      ),
    );

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pumpAndSettle();

    final okCard = tester.widget<Card>(
      find.ancestor(of: find.text('ok'), matching: find.byType(Card)),
    );
    final warnCard = tester.widget<Card>(
      find.ancestor(of: find.text('warn'), matching: find.byType(Card)),
    );
    final badCard = tester.widget<Card>(
      find.ancestor(of: find.text('bad'), matching: find.byType(Card)),
    );

    expect(okCard.color, Colors.green.shade100);
    expect(warnCard.color, Colors.yellow.shade100);
    expect(badCard.color, Colors.red.shade100);
  });

  testWidgets('risk score card reflects severity colors', (tester) async {
    Future<Map<String, dynamic>> mockFetch(int total) async {
      return {
        'risk_score': total,
        'findings': [
          {'category': 'dummy', 'score': 0},
        ],
      };
    }

    Future<void> verify(int score, Color color) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(body: StaticScanTab(fetcher: () => mockFetch(score))),
        ),
      );

      await tester.tap(find.byKey(const Key('staticButton')));
      await tester.pumpAndSettle();

      final card = tester.widget<Card>(
        find.ancestor(
          of: find.text('リスクスコア: $score'),
          matching: find.byType(Card),
        ),
      );
      expect(card.color, color);

      await tester.pumpWidget(const SizedBox.shrink());
    }

    await verify(0, Colors.green.shade100);
    await verify(3, Colors.yellow.shade100);
    await verify(6, Colors.red.shade100);
  });

  testWidgets('generates report and shows path', (tester) async {
    bool called = false;
    Future<String> mockReport() async {
      called = true;
      return '/tmp/report.pdf';
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: StaticScanTab(
            fetcher: () async => {'risk_score': 0, 'findings': []},
            reportFetcher: mockReport,
          ),
        ),
      ),
    );

    await tester.tap(find.byKey(const Key('reportButton')));
    await tester.pump();
    await tester.pump();
    await tester.pump();

    expect(called, isTrue);
  });
}
