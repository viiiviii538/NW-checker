import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  testWidgets('static scan button shows loading and results', (tester) async {
    Future<Map<String, dynamic>> mockFetch() async {
      await Future.delayed(const Duration(milliseconds: 10));
      return {
        'risk_score': 1,
        'findings': [
          {'category': 'demo', 'score': 1},
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

    expect(find.text('リスクスコア: 1'), findsOneWidget);
    expect(find.text('demo'), findsOneWidget);
  });
}
