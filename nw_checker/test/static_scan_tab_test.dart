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
}
