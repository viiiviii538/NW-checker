import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/history_page.dart';

void main() {
  testWidgets('HistoryPage loads and displays results', (tester) async {
    await tester.pumpWidget(
        const MaterialApp(home: Scaffold(body: HistoryPage())));
    await tester.enterText(find.byKey(const Key('fromField')), '2024-01-01');
    await tester.enterText(find.byKey(const Key('toField')), '2024-01-02');
    await tester.tap(find.text('検索'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    expect(find.text('History 1'), findsOneWidget);
    expect(find.text('History 2'), findsOneWidget);
  });
}
