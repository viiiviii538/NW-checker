import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  test('performStaticScan returns summary and findings', () async {
    final result = await performStaticScan();
    expect(result.containsKey('summary'), isTrue);
    expect(result.containsKey('findings'), isTrue);
  });

  testWidgets('port scan tile shows summary and details', (tester) async {
    Future<Map<String, dynamic>> mockScan() async {
      return {
        'summary': [],
        'findings': [
          {
            'category': 'ports',
            'details': {
              'open_ports': [22, 80],
            },
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

    await tester.tap(find.text('Port Scan'));
    await tester.pumpAndSettle();

    expect(find.text('Open ports: 22, 80'), findsOneWidget);
    expect(find.text('ポート 22: open'), findsOneWidget);
    expect(find.text('ポート 80: open'), findsOneWidget);
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
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
            'category': 'dns',
            'details': {
              'warnings': [],
              'servers': ['1.1.1.1'],
              'dnssec_enabled': true,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    expect(find.text('OK'), findsNWidgets(8));
    expect(find.text('警告'), findsNothing);
  });

  testWidgets('no OS info shows error in tile', (tester) async {
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
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
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
            'category': 'dns',
            'details': {
              'warnings': [],
              'servers': ['1.1.1.1'],
              'dnssec_enabled': true,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final osLabel = chips[1].label as Text;
    expect(osLabel.data, 'エラー');
    expect(chips[1].backgroundColor, Colors.red);

    await tester.tap(find.text('OS / Services'));
    await tester.pumpAndSettle();
    expect(find.text('情報取得失敗'), findsOneWidget);
  });

  testWidgets('shows OS and service banners in tile', (tester) async {
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
            'details': {
              'os': 'Linux',
              'banners': {'80': 'http Apache'},
            },
          },
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
            },
          },
          {
            'category': 'dhcp',
            'details': {
              'servers': ['1.1.1.1'],
              'warnings': [],
            },
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final osLabel = chips[1].label as Text;
    expect(osLabel.data, 'OK');

    await tester.tap(find.text('OS / Services'));
    await tester.pumpAndSettle();
    expect(find.text('OS: Linux'), findsOneWidget);
    expect(find.text('ポート 80: http Apache'), findsOneWidget);
  });

  testWidgets('SMBv1 enabled shows warning in tile', (tester) async {
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': true, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
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
            'category': 'dns',
            'details': {
              'warnings': [],
              'servers': ['1.1.1.1'],
              'dnssec_enabled': true,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final smbLabel = chips[2].label as Text;
    expect(smbLabel.data, '警告');
  });

  testWidgets('UPnP responder shows warning in tile', (tester) async {
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
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
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
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
            'category': 'dns',
            'details': {
              'warnings': [],
              'servers': ['1.1.1.1'],
              'dnssec_enabled': true,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final upnpLabel = chips[3].label as Text;
    expect(upnpLabel.data, '警告');
    await tester.tap(find.text('UPnP'));
    await tester.pumpAndSettle();
    expect(find.text('UPnP service responded from 1.1.1.1'), findsOneWidget);
  });

  testWidgets('misconfigured UPnP response shows warning in tile', (
    tester,
  ) async {
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {
              'responders': ['1.1.1.1'],
              'warnings': ['Misconfigured SSDP response from 1.1.1.1'],
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
            'category': 'dns',
            'details': {
              'warnings': [],
              'servers': ['1.1.1.1'],
              'dnssec_enabled': true,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final upnpLabel = chips[3].label as Text;
    expect(upnpLabel.data, '警告');
    await tester.tap(find.text('UPnP'));
    await tester.pumpAndSettle();
    expect(
      find.text('Misconfigured SSDP response from 1.1.1.1'),
      findsOneWidget,
    );

    final arpLabel = chips[4].label as Text;
    expect(arpLabel.data, '警告');
    await tester.tap(find.text('ARP Spoof'));
    await tester.pumpAndSettle();
    expect(find.text('ARP table updated with spoofed entry'), findsOneWidget);
  });

  testWidgets('multiple DHCP servers show warning in tile', (tester) async {
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
            },
          },
          {
            'category': 'dhcp',
            'details': {
              'servers': ['1.1.1.1', '2.2.2.2'],
              'warnings': ['Multiple DHCP servers detected: 1.1.1.1, 2.2.2.2'],
            },
          },
          {
            'category': 'dns',
            'details': {
              'warnings': [],
              'servers': ['1.1.1.1'],
              'dnssec_enabled': true,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final dhcpLabel = chips[5].label as Text;
    expect(dhcpLabel.data, '警告');
    await tester.tap(find.text('DHCP'));
    await tester.pumpAndSettle();
    expect(
      find.text('Multiple DHCP servers detected: 1.1.1.1, 2.2.2.2'),
      findsOneWidget,
    );
  });

  testWidgets('expired SSL certificate shows warning in tile', (tester) async {
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
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
            'category': 'dns',
            'details': {
              'warnings': [],
              'servers': ['1.1.1.1'],
              'dnssec_enabled': true,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': true},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final sslLabel = chips[7].label as Text;
    expect(sslLabel.data, '警告');
    await tester.tap(find.text('SSL証明書'));
    await tester.pumpAndSettle();
    expect(find.text('証明書は期限切れ'), findsOneWidget);
  });

  testWidgets('external DNS shows warning in tile', (tester) async {
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
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
            'category': 'dns',
            'details': {
              'warnings': ['External DNS detected: 8.8.8.8'],
              'servers': ['8.8.8.8'],
              'dnssec_enabled': false,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final dnsLabel = chips[6].label as Text;
    expect(dnsLabel.data, '警告');
    await tester.tap(find.text('DNS'));
    await tester.pumpAndSettle();
    expect(find.text('External DNS detected: 8.8.8.8'), findsOneWidget);
  });

  testWidgets('invalid DNS server shows warning in tile', (tester) async {
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
          {
            'category': 'smb_netbios',
            'details': {'smb1_enabled': false, 'netbios_names': []},
          },
          {
            'category': 'upnp',
            'details': {'responders': [], 'warnings': []},
          },
          {
            'category': 'arp_spoof',
            'details': {
              'vulnerable': false,
              'explanation': 'No ARP poisoning detected',
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
            'category': 'dns',
            'details': {
              'warnings': ['Invalid DNS server IP: bad_ip'],
              'servers': ['bad_ip'],
              'dnssec_enabled': false,
            },
          },
          {
            'category': 'ssl_cert',
            'details': {'host': 'example.com', 'expired': false},
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

    final chips = tester.widgetList<Chip>(find.byType(Chip)).toList();
    final dnsLabel = chips[6].label as Text;
    expect(dnsLabel.data, '警告');
    await tester.tap(find.text('DNS'));
    await tester.pumpAndSettle();
    expect(find.text('Invalid DNS server IP: bad_ip'), findsOneWidget);
  });
}
