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
        ],
      };
    }

    await tester.pumpWidget(
      MaterialApp(home: StaticScanTab(scanner: mockScan)),
    );

    await tester.tap(find.byKey(const Key('staticButton')));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(find.text('OK'), findsNWidgets(5));
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
  });
}
