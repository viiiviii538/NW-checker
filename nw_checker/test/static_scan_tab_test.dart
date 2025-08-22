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
}
