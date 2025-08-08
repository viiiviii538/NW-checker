import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/widgets/widgets.dart';

void main() {
group('ReusableCard', () {
  testWidgets('displays child', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: ReusableCard(child: Text('hello'))),
    );
    expect(find.text('hello'), findsOneWidget);
  });

  testWidgets('has default style', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: ReusableCard(child: Text('x'))),
    );
    final card = tester.widget<Card>(find.byType(Card));
    expect(card.elevation, 2);
    expect(card.margin, const EdgeInsets.all(8));
  });
});

group('LogTable', () {
  testWidgets('shows placeholder when empty', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: LogTable(rows: []))),
    );
    expect(find.text('No logs'), findsOneWidget);
  });

  testWidgets('renders provided rows', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LogTable(
            rows: const [
              DataRow(cells: [DataCell(Text('entry1'))]),
            ],
          ),
        ),
      ),
    );
    expect(find.text('entry1'), findsOneWidget);
  });
});

group('AlertComponent', () {
  testWidgets('shows icon and message', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: AlertComponent(message: 'warning')),
    );
    expect(find.byIcon(Icons.warning), findsOneWidget);
    expect(find.text('warning'), findsOneWidget);
  });
});
}
