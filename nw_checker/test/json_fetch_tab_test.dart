import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/json_fetch_tab.dart';

void main() {
  testWidgets('shows message when fetcher fails', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(
        home: JsonFetchTab(
          buttonText: 'run',
          fetcher: _failingFetcher,
          buttonKey: Key('runButton'),
        ),
      ),
    );

    await tester.tap(find.byKey(const Key('runButton')));
    await tester.pump();
    await tester.pump();
    await tester.pumpAndSettle();

    expect(find.text('結果がありません'), findsOneWidget);
  });
}

Future<Map<String, dynamic>> _failingFetcher() async {
  throw Exception('fail');
}
