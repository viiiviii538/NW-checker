import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  Future<List<String>> mockScan() async {
    await Future.delayed(const Duration(milliseconds: 10));
    return ['=== STATIC SCAN REPORT ===', 'No issues detected.'];
  }

  Widget buildWidget() =>
      MaterialApp(home: Scaffold(body: StaticScanTab(scanner: mockScan)));

  testWidgets('button tap shows progress then results and categories', (
    tester,
  ) async {
    await tester.pumpWidget(buildWidget());

    // Initial summary and status badges
    expect(find.text('スキャン未実施'), findsOneWidget);
    expect(find.byType(ListView), findsOneWidget);
    final initialChips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    expect(initialChips, hasLength(3));
    expect(initialChips.every((c) => c.backgroundColor == Colors.grey), isTrue);

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    expect(find.byType(CircularProgressIndicator), findsOneWidget);

    await tester.pumpAndSettle();

    expect(find.byType(CircularProgressIndicator), findsNothing);
    expect(find.text('=== STATIC SCAN REPORT ==='), findsOneWidget);
    expect(find.text('No issues detected.'), findsOneWidget);

    // Category order
    final portDy = tester.getTopLeft(find.text('Port Scan')).dy;
    final osDy = tester.getTopLeft(find.text('OS/Service')).dy;
    final sslDy = tester.getTopLeft(find.text('SSL証明書')).dy;
    expect(portDy < osDy && osDy < sslDy, isTrue);

    // Status badges and colors after scan
    final chipsAfter = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final firstLabel = chipsAfter[0].label as Text;
    final secondLabel = chipsAfter[1].label as Text;
    final thirdLabel = chipsAfter[2].label as Text;
    expect(firstLabel.data, 'OK');
    expect(chipsAfter[0].backgroundColor, Colors.blueGrey);
    expect(secondLabel.data, 'OK');
    expect(chipsAfter[1].backgroundColor, Colors.blueGrey);
    expect(thirdLabel.data, '警告');
    expect(chipsAfter[2].backgroundColor, Colors.orange);

    await tester.tap(find.text('OS/Service'));
    await tester.pumpAndSettle();
    expect(find.text('OS: Linux'), findsOneWidget);

    await tester.tap(find.text('SSL証明書'));
    await tester.pumpAndSettle();
    expect(find.text('証明書の期限が30日以内です'), findsOneWidget);
  });
}
