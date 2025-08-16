import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  testWidgets('chips reflect status colors and labels', (tester) async {
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
            'details': {'os': '', 'banners': {}},
          },
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': true, 'netbios_names': []},
          },
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(home: StaticScanTab(scanner: mockScan)),
    );

    final initialChip = tester.widget<Chip>(find.byType(Chip).first);
    expect((initialChip.label as Text).data, '未実行');
    expect(initialChip.backgroundColor, Colors.grey);

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    await tester.pumpAndSettle();

    final portChip = tester.widget<Chip>(find.byType(Chip).at(0));
    expect((portChip.label as Text).data, 'OK');
    expect(portChip.backgroundColor, Colors.blueGrey);

    final osChip = tester.widget<Chip>(find.byType(Chip).at(1));
    expect((osChip.label as Text).data, 'エラー');
    expect(osChip.backgroundColor, Colors.red);

    final smbChip = tester.widget<Chip>(find.byType(Chip).at(2));
    expect((smbChip.label as Text).data, '警告');
    expect(smbChip.backgroundColor, Colors.orange);
  });
}
