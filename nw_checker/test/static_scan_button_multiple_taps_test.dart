import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  testWidgets('static scan can be re-run showing loading and new results', (tester) async {
    var call = 0;
    Future<Map<String, dynamic>> mockFetch() async {
      call += 1;
      await Future.delayed(const Duration(milliseconds: 10));
      return {
        'risk_score': call,
        'findings': [
          {'category': 'demo$call', 'score': 1},
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(body: StaticScanTab(fetcher: mockFetch)),
      ),
    );

    // First tap
    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pumpAndSettle();
    expect(find.text('リスクスコア: 1'), findsOneWidget);
    expect(find.text('demo1'), findsOneWidget);

    // Second tap should show loading again and update results
    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    await tester.pumpAndSettle();
    expect(find.text('リスクスコア: 2'), findsOneWidget);
    expect(find.text('demo2'), findsOneWidget);
  });
}
