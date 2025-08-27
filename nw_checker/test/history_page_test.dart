import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/history_page.dart';

void main() {
  testWidgets('HistoryPage fetches and displays results', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: HistoryPage()));
    await tester.enterText(find.byKey(const Key('fromField')), '2025-01-01');
    await tester.enterText(find.byKey(const Key('toField')), '2025-01-02');
    await tester.tap(find.byKey(const Key('loadButton')));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 300));
    expect(
      find.text(
        'History 2025-01-01T00:00:00.000 - 2025-01-02T00:00:00.000',
      ),
      findsOneWidget,
    );
    expect(
      find.text(
        'DNS History 2025-01-01T00:00:00.000 - 2025-01-02T00:00:00.000',
      ),
      findsOneWidget,
    );
  });
}
