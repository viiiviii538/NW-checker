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
      final padding = tester.widget<Padding>(
        find.ancestor(of: find.text('x'), matching: find.byType(Padding)).first,
      );
      expect(padding.padding, const EdgeInsets.all(16));
    });

    testWidgets('accepts custom style', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: ReusableCard(
            margin: EdgeInsets.zero,
            elevation: 0,
            padding: EdgeInsets.zero,
            child: SizedBox(),
          ),
        ),
      );
      final card = tester.widget<Card>(find.byType(Card));
      expect(card.elevation, 0);
      expect(card.margin, EdgeInsets.zero);
      final paddingFinder = find
          .descendant(of: find.byType(Card), matching: find.byType(Padding))
          .first;
      final padding = tester.widget<Padding>(paddingFinder);
      expect(padding.padding, EdgeInsets.zero);
    });
  });

  group('LogTable', () {
    testWidgets('shows placeholder when empty', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(body: LogTable(rows: [])),
        ),
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

    testWidgets('supports custom columns and placeholder', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: LogTable(
              columns: const [
                DataColumn(label: Text('Time')),
                DataColumn(label: Text('Msg')),
              ],
              rows: const [],
              placeholder: 'none',
            ),
          ),
        ),
      );
      expect(find.text('Time'), findsOneWidget);
      expect(find.text('none'), findsOneWidget);
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

    testWidgets('uses default background color', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: AlertComponent(message: 'warn')),
      );
      final container = tester.widget<Container>(find.byType(Container));
      expect(container.color, Colors.red[100]);
    });

    testWidgets('supports custom icon and color', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: AlertComponent(
            message: 'ok',
            icon: Icons.check,
            iconColor: Colors.green,
            backgroundColor: Colors.green,
          ),
        ),
      );
      expect(find.byIcon(Icons.check), findsOneWidget);
    });
  });
}
