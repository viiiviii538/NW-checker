import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  Future<Map<String, dynamic>> mockScan() async {
    await Future.delayed(const Duration(milliseconds: 10));
    return {
      'summary': ['=== STATIC SCAN REPORT ===', 'No issues detected.'],
      'findings': [
        {
          'category': 'ports',
          'details': {
            'open_ports': [22, 80],
          },
        },
        {
          'category': 'os_banner',
          'details': {
            'os': 'Linux',
            'banners': {'22': 'ssh', '80': 'http'},
          },
        },
        {
          'category': 'smb_netbios',
          'details': {
            'smb1_enabled': false,
            'netbios_names': ['HOST'],
          },
        },
        {
          'category': 'upnp',
          'details': {
            'responders': ['1.1.1.1'],
            'warnings': ['UPnP service responded from 1.1.1.1'],
          },
        },
        {
          'category': 'arp_spoof',
          'details': {
            'vulnerable': true,
            'explanation': 'ARP table updated with spoofed entry',
          },
        },
        {
          'category': 'dhcp',
          'details': {
            'servers': ['1.1.1.1'],
            'warnings': [],
          },
        },
        {
          'category': 'ssl_cert',
          'details': {'host': 'example.com', 'expired': false},
        },
      ],
    };
  }

  Widget buildWidget() => MaterialApp(
    home: Scaffold(body: StaticScanTab(scanner: mockScan)),
  );

  testWidgets('button tap shows progress then results and categories', (
    tester,
  ) async {
    await tester.pumpWidget(buildWidget());

    // Initial summary and status badges
    expect(find.text('スキャン未実施'), findsOneWidget);
    expect(find.byType(ListView), findsOneWidget);
    final initialChips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    expect(initialChips, hasLength(7));
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
    final osDy = tester.getTopLeft(find.text('OS / Services')).dy;
    final smbDy = tester.getTopLeft(find.text('SMB / NetBIOS')).dy;
    final upnpDy = tester.getTopLeft(find.text('UPnP')).dy;
    final arpDy = tester.getTopLeft(find.text('ARP Spoof')).dy;
    final dhcpDy = tester.getTopLeft(find.text('DHCP')).dy;
    final sslDy = tester.getTopLeft(find.text('SSL証明書')).dy;
    expect(portDy < osDy, isTrue);
    expect(osDy < smbDy, isTrue);
    expect(smbDy < upnpDy, isTrue);
    expect(upnpDy < arpDy, isTrue);
    expect(arpDy < dhcpDy, isTrue);
    expect(dhcpDy < sslDy, isTrue);

    // ステータスバッジと色
    final chipsAfter = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final firstLabel = chipsAfter[0].label as Text;
    final secondLabel = chipsAfter[1].label as Text;
    final thirdLabel = chipsAfter[2].label as Text;
    final fourthLabel = chipsAfter[3].label as Text;
    final fifthLabel = chipsAfter[4].label as Text;
    final sixthLabel = chipsAfter[5].label as Text;
    final seventhLabel = chipsAfter[6].label as Text;
    expect(firstLabel.data, '警告');
    expect(chipsAfter[0].backgroundColor, Colors.orange);
    expect(secondLabel.data, 'OK');
    expect(chipsAfter[1].backgroundColor, Colors.blueGrey);
    expect(thirdLabel.data, 'OK');
    expect(chipsAfter[2].backgroundColor, Colors.blueGrey);
    expect(fourthLabel.data, '警告');
    expect(chipsAfter[3].backgroundColor, Colors.orange);
    expect(fifthLabel.data, '警告');
    expect(chipsAfter[4].backgroundColor, Colors.orange);
    expect(sixthLabel.data, 'OK');
    expect(chipsAfter[5].backgroundColor, Colors.blueGrey);
    expect(seventhLabel.data, 'OK');
    expect(chipsAfter[6].backgroundColor, Colors.blueGrey);

    // 警告ラベルが3つあること
    expect(find.text('警告'), findsNWidgets(3));

    // ポートスキャン結果の表示確認
    await tester.tap(find.text('Port Scan'));
    await tester.pumpAndSettle();
    expect(find.text('ポート 22: open'), findsOneWidget);
    expect(find.text('ポート 80: open'), findsOneWidget);
    // 折りたたんで他カテゴリを表示可能にする
    await tester.tap(find.text('Port Scan'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('OS / Services'));
    await tester.pumpAndSettle();
    expect(find.text('OS: Linux'), findsOneWidget);
    expect(find.text('ポート 22: ssh'), findsOneWidget);
    expect(find.text('ポート 80: http'), findsOneWidget);
    await tester.tap(find.text('OS / Services'));
    await tester.pumpAndSettle();

    await tester.tap(find.text('SMB / NetBIOS'));
    await tester.pumpAndSettle();
    expect(find.text('SMBv1: 無効'), findsOneWidget);
    expect(find.text('NetBIOS: HOST'), findsOneWidget);

    await tester.drag(find.byType(ListView), const Offset(0, -300));
    await tester.pumpAndSettle();
    await tester.tap(find.text('UPnP'));
    await tester.pumpAndSettle();
    expect(find.text('UPnP service responded from 1.1.1.1'), findsOneWidget);

    await tester.drag(find.byType(ListView), const Offset(0, -300));
    await tester.pumpAndSettle();
    await tester.tap(find.text('ARP Spoof'));
    await tester.pumpAndSettle();
    expect(find.text('ARP table updated with spoofed entry'), findsOneWidget);
  });
}
