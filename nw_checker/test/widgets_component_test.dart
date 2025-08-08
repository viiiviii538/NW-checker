import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/widgets/widgets.dart';

void main() {
  testWidgets('ReusableCard displays child', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: ReusableCard(child: Text('hello'))),
    );
    expect(find.text('hello'), findsOneWidget);
  });

  testWidgets('LogTable displays when empty', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: LogTable(rows: const []))),
    );
    expect(find.byType(LogTable), findsOneWidget);
  });

  testWidgets('AlertComponent shows message', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: AlertComponent(message: 'warning')),
    );
    expect(find.text('warning'), findsOneWidget);
  });
}
