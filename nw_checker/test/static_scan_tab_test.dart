import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  test('performStaticScan returns summary and findings', () async {
    final result = await performStaticScan();
    expect(result.containsKey('summary'), isTrue);
    expect(result.containsKey('findings'), isTrue);
  });

  testWidgets('no open ports marks port tile OK', (tester) async {
    Future<Map<String, dynamic>> mockScan() async {
      return {
        'summary': [],
        'findings': [
          {
            'category': 'ports',
            'details': {'open_ports': []},
          },
          {
            'category': 'os_banner',
            'details': {'os': 'Linux', 'banners': {}},
          },
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(home: StaticScanTab(scanner: mockScan)),
    );

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(find.text('OK'), findsNWidgets(2));
    expect(find.text('警告'), findsOneWidget);
  });
}
