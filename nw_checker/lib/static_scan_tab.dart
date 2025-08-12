import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

/// 静的スキャンAPIを呼び出し結果を返す
Future<Map<String, dynamic>> performStaticScan() async {
  try {
    final resp = await http
        .get(Uri.parse('http://localhost:8000/static_scan'))
        .timeout(const Duration(seconds: 5));
    if (resp.statusCode == 200) {
      final decoded = jsonDecode(resp.body) as Map<String, dynamic>;
      return {
        'summary': ['リスクスコア: ${decoded['risk_score'] ?? 0}'],
        'findings': decoded['findings'] ?? [],
      };
    }
  } catch (_) {}
  return {
    'summary': ['スキャン失敗'],
    'findings': [],
  };
}

/// カテゴリごとのスキャン状態。
enum ScanStatus { pending, ok, warning, error }

/// カテゴリタイルのデータモデル。
class CategoryTile {
  CategoryTile({
    required this.title,
    required this.icon,
    this.status = ScanStatus.pending,
    this.details = const [],
  });

  final String title;
  final IconData icon;
  ScanStatus status;
  List<String> details;
}

class StaticScanTab extends StatefulWidget {
  const StaticScanTab({super.key, this.scanner = performStaticScan});

  final Future<Map<String, dynamic>> Function() scanner;

  @override
  State<StaticScanTab> createState() => _StaticScanTabState();
}

class _StaticScanTabState extends State<StaticScanTab> {
  bool _isLoading = false;
  List<String> _summaryLines = [];
  late List<CategoryTile> _categories;

  @override
  void initState() {
    super.initState();
    _categories = [
      CategoryTile(title: 'Port Scan', icon: Icons.router),
      CategoryTile(title: 'OS / Services', icon: Icons.computer),
      CategoryTile(title: 'SMB / NetBIOS', icon: Icons.folder),
      CategoryTile(title: 'UPnP', icon: Icons.cast),
      CategoryTile(title: 'ARP Spoof', icon: Icons.security),
      CategoryTile(title: 'DHCP', icon: Icons.dns),
      CategoryTile(title: 'DNS', icon: Icons.language),
      CategoryTile(title: 'SSL証明書', icon: Icons.lock),
    ];
  }

  void _startScan() {
    setState(() {
      _isLoading = true;
      _summaryLines = [];
      for (final c in _categories) {
        c.status = ScanStatus.pending;
        c.details = [];
      }
    });

    // Allow progress indicator to render before kicking off scan.
    Future<void>(() async {
      final result = await widget.scanner();
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _summaryLines = List<String>.from(
          result['summary'] as List? ?? const [],
        );

        final findings =
            (result['findings'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final portsFinding = findings.firstWhere(
          (f) => f['category'] == 'ports',
          orElse: () => <String, dynamic>{},
        );
        final openPorts =
            (portsFinding['details']?['open_ports'] as List? ?? []).cast<int>();
        _categories[0]
          ..status = openPorts.isEmpty ? ScanStatus.ok : ScanStatus.warning
          ..details = [
            if (openPorts.isEmpty)
              'No open ports detected'
            else
              'Open ports: ${openPorts.join(', ')}',
            ...openPorts.map((p) => 'ポート $p: open'),
          ];

        final osFinding = findings.firstWhere(
          (f) => f['category'] == 'os_banner',
          orElse: () => <String, dynamic>{},
        );
        final osName = osFinding['details']?['os'] as String? ?? '';
        final bannerMap = (osFinding['details']?['banners'] as Map? ?? {})
            .cast<String, dynamic>();
        _categories[1]
          ..status = (osName.isNotEmpty || bannerMap.isNotEmpty)
              ? ScanStatus.ok
              : ScanStatus.error
          ..details = [
            if (osName.isNotEmpty) 'OS: $osName',
            ...bannerMap.entries.map((e) => 'ポート ${e.key}: ${e.value}'),
            if (osName.isEmpty && bannerMap.isEmpty) '情報取得失敗',
          ];

        final smbFinding = findings.firstWhere(
          (f) => f['category'] == 'smb_netbios',
          orElse: () => <String, dynamic>{},
        );
        final smbDetails =
            (smbFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final smb1 = smbDetails['smb1_enabled'] as bool?;
        final smbNames = (smbDetails['netbios_names'] as List? ?? [])
            .cast<String>();
        final smbError = smbDetails['error'] as String?;
        _categories[2]
          ..status = smbError != null
              ? ScanStatus.error
              : (smb1 == true ? ScanStatus.warning : ScanStatus.ok)
          ..details = [
            if (smb1 != null) 'SMBv1: ${smb1 ? '有効' : '無効'}',
            ...smbNames.map((n) => 'NetBIOS: $n'),
            if (smbError != null) '情報取得失敗',
          ];

        final upnpFinding = findings.firstWhere(
          (f) => f['category'] == 'upnp',
          orElse: () => <String, dynamic>{},
        );
        final upnpDetails =
            (upnpFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final upnpWarnings = (upnpDetails['warnings'] as List? ?? [])
            .cast<String>();
        final upnpResponders = (upnpDetails['responders'] as List? ?? [])
            .cast<String>();
        _categories[3]
          ..status = upnpWarnings.isEmpty ? ScanStatus.ok : ScanStatus.warning
          ..details = [
            ...upnpWarnings,
            ...upnpResponders.map((ip) => 'ホスト $ip'),
            if (upnpWarnings.isEmpty && upnpResponders.isEmpty) '応答なし',
          ];

        final arpFinding = findings.firstWhere(
          (f) => f['category'] == 'arp_spoof',
          orElse: () => <String, dynamic>{},
        );
        final arpDetails =
            (arpFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final arpVuln = arpDetails['vulnerable'] as bool?;
        final arpExplain = arpDetails['explanation'] as String?;
        _categories[4]
          ..status = arpVuln == null
              ? ScanStatus.error
              : (arpVuln ? ScanStatus.warning : ScanStatus.ok)
          ..details = [if (arpExplain != null) arpExplain else '情報取得失敗'];

        final dhcpFinding = findings.firstWhere(
          (f) => f['category'] == 'dhcp',
          orElse: () => <String, dynamic>{},
        );
        final dhcpDetails =
            (dhcpFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final dhcpServers = (dhcpDetails['servers'] as List? ?? [])
            .cast<String>();
        final dhcpWarnings = (dhcpDetails['warnings'] as List? ?? [])
            .cast<String>();
        _categories[5]
          ..status = dhcpServers.isEmpty
              ? ScanStatus.error
              : (dhcpWarnings.isEmpty ? ScanStatus.ok : ScanStatus.warning)
          ..details = [
            ...dhcpWarnings,
            ...dhcpServers.map((ip) => 'サーバー $ip'),
            if (dhcpServers.isEmpty) '応答なし',
          ];

        final dnsFinding = findings.firstWhere(
          (f) => f['category'] == 'dns',
          orElse: () => <String, dynamic>{},
        );
        final dnsDetails =
            (dnsFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final dnsWarnings = (dnsDetails['warnings'] as List? ?? [])
            .cast<String>();
        _categories[6]
          ..status = dnsWarnings.isEmpty ? ScanStatus.ok : ScanStatus.warning
          ..details = dnsWarnings.isEmpty ? ['設定に問題なし'] : dnsWarnings;

        final sslFinding = findings.firstWhere(
          (f) => f['category'] == 'ssl_cert',
          orElse: () => <String, dynamic>{},
        );
        final sslDetails =
            (sslFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final sslExpired = sslDetails['expired'] as bool?;
        final sslHost = sslDetails['host'] as String? ?? '';
        _categories[7]
          ..status = sslExpired == null
              ? ScanStatus.error
              : (sslExpired ? ScanStatus.warning : ScanStatus.ok)
          ..details = [
            if (sslHost.isNotEmpty) 'ホスト: $sslHost',
            if (sslExpired == true) '証明書は期限切れ',
            if (sslExpired == false) '証明書は有効',
            if (sslExpired == null) '情報取得失敗',
          ];
      });
    });
  }

  Color _statusColor(ScanStatus status) {
    switch (status) {
      case ScanStatus.warning:
        return Colors.orange;
      case ScanStatus.error:
        return Colors.red;
      case ScanStatus.ok:
        return Colors.blueGrey;
      case ScanStatus.pending:
      default:
        return Colors.grey;
    }
  }

  String _statusLabel(ScanStatus status) {
    switch (status) {
      case ScanStatus.warning:
        return '警告';
      case ScanStatus.error:
        return 'エラー';
      case ScanStatus.ok:
        return 'OK';
      case ScanStatus.pending:
      default:
        return '未実行';
    }
  }

  Widget _buildSummaryCard() {
    final lines = _summaryLines.isEmpty ? ['スキャン未実施'] : _summaryLines;
    return Card(
      color: Colors.blueGrey[50],
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: lines.map((e) => Text(e)).toList(),
        ),
      ),
    );
  }

  Widget _buildCategoryList() {
    return ListView.builder(
      itemCount: _categories.length,
      itemBuilder: (context, index) {
        final cat = _categories[index];
        return Card(
          color: Colors.blueGrey[50],
          margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          child: ExpansionTile(
            key: Key('category_$index'),
            leading: Icon(cat.icon, color: Colors.blueGrey),
            title: Text(cat.title),
            trailing: Chip(
              label: Text(_statusLabel(cat.status)),
              backgroundColor: _statusColor(cat.status),
            ),
            children: cat.details.map((d) => ListTile(title: Text(d))).toList(),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _buildSummaryCard(),
        ElevatedButton(
          key: const Key('staticButton'),
          style: ElevatedButton.styleFrom(backgroundColor: Colors.blueGrey),
          onPressed: _startScan,
          child: const Text('スキャン開始'),
        ),
        if (_isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else
          Expanded(child: _buildCategoryList()),
      ],
    );
  }
}
