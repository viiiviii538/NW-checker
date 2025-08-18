import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'api_config.dart';

/// 静的スキャンAPIを呼び出し結果を返す
Future<Map<String, dynamic>> performStaticScan({http.Client? client}) async {
  final created = client == null;
  final c = client ?? http.Client();
  try {
    final resp = await c
        .get(Uri.parse('${baseUrl()}/static_scan'))
        .timeout(const Duration(seconds: 5));
    if (resp.statusCode == 200) {
      final decoded = jsonDecode(resp.body) as Map<String, dynamic>;
      return {
        'summary': ['リスクスコア: ${decoded['risk_score'] ?? 0}'],
        'findings': decoded['findings'] ?? [],
      };
    } else {
      // 200以外の応答はエラーとして扱う
      String message;
      try {
        final err = jsonDecode(resp.body);
        if (err is Map && err['detail'] != null) {
          message = 'HTTP ${resp.statusCode}: ${err['detail']}';
        } else {
          message = 'HTTP ${resp.statusCode}';
        }
      } catch (_) {
        message = 'HTTP ${resp.statusCode}';
      }
      return {
        'summary': ['スキャン失敗: $message'],
        'findings': [],
      };
    }
  } catch (e) {
    // 例外発生時は例外メッセージを返す
    final msg = e.toString();
    return {
      'summary': ['スキャン失敗: $msg'],
      'findings': [],
    };
  } finally {
    if (created) {
      c.close();
    }
  }
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
  late List<CategoryTile> _categories;
  List<String> _summary = [];

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
      _summary = [];
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
    });

    // Allow progress indicator to render before kicking off scan.
    Future<void>(() async {
      final result = await widget.scanner();
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _summary = (result['summary'] as List? ?? []).cast<String>();
        final findings =
            (result['findings'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final knownCats = <String>{
          'ports',
          'os_banner',
          'smb_netbios',
          'upnp',
          'arp_spoof',
          'dhcp',
          'dns',
          'ssl_cert',
        };

        final portsFinding = findings.firstWhere(
          (f) => f['category'] == 'ports',
          orElse: () => <String, dynamic>{},
        );
        final portDetails =
            (portsFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final openPorts = (portDetails['open_ports'] as List? ?? [])
            .cast<int>();
        final portError = portDetails['error'] as String?;
        _categories[0]
          ..status = portError != null
              ? ScanStatus.error
              : (openPorts.isEmpty ? ScanStatus.ok : ScanStatus.warning)
          ..details = [
            if (openPorts.isEmpty)
              'No open ports detected'
            else
              'Open ports: ${openPorts.join(', ')}',
            ...openPorts.map((p) => 'ポート $p: open'),
            if (portError != null) portError,
          ];

        final osFinding = findings.firstWhere(
          (f) => f['category'] == 'os_banner',
          orElse: () => <String, dynamic>{},
        );
        final osDetails =
            (osFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final osName = osDetails['os'] as String? ?? '';
        final bannerMap = (osDetails['banners'] as Map? ?? {})
            .cast<String, dynamic>();
        final osError = osDetails['error'] as String?;
        _categories[1]
          ..status = osError != null
              ? ScanStatus.error
              : ((osName.isNotEmpty || bannerMap.isNotEmpty)
                    ? ScanStatus.ok
                    : ScanStatus.error)
          ..details = [
            if (osName.isNotEmpty) 'OS: $osName',
            ...bannerMap.entries.map((e) => 'ポート ${e.key}: ${e.value}'),
            if (osName.isEmpty && bannerMap.isEmpty && osError == null)
              '情報取得失敗',
            if (osError != null) osError,
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
            if (smbError != null) smbError,
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
        final upnpError = upnpDetails['error'] as String?;
        _categories[3]
          ..status = upnpError != null
              ? ScanStatus.error
              : (upnpWarnings.isEmpty ? ScanStatus.ok : ScanStatus.warning)
          ..details = [
            ...upnpWarnings,
            ...upnpResponders.map((ip) => 'ホスト $ip'),
            if (upnpWarnings.isEmpty &&
                upnpResponders.isEmpty &&
                upnpError == null)
              '応答なし',
            if (upnpError != null) upnpError,
          ];

        final arpFinding = findings.firstWhere(
          (f) => f['category'] == 'arp_spoof',
          orElse: () => <String, dynamic>{},
        );
        final arpDetails =
            (arpFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final arpVuln = arpDetails['vulnerable'] as bool?;
        final arpExplain = arpDetails['explanation'] as String?;
        final arpError = arpDetails['error'] as String?;
        _categories[4]
          ..status = arpError != null
              ? ScanStatus.error
              : (arpVuln == null
                    ? ScanStatus.error
                    : (arpVuln ? ScanStatus.warning : ScanStatus.ok))
          ..details = [
            if (arpExplain != null)
              arpExplain
            else if (arpError == null)
              '情報取得失敗',
            if (arpError != null) arpError,
          ];

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
        final dhcpError = dhcpDetails['error'] as String?;
        _categories[5]
          ..status = dhcpError != null
              ? ScanStatus.error
              : (dhcpServers.isEmpty
                    ? ScanStatus.error
                    : (dhcpWarnings.isEmpty
                          ? ScanStatus.ok
                          : ScanStatus.warning))
          ..details = [
            ...dhcpWarnings,
            ...dhcpServers.map((ip) => 'サーバー $ip'),
            if (dhcpServers.isEmpty && dhcpError == null) '応答なし',
            if (dhcpError != null) dhcpError,
          ];

        final dnsFinding = findings.firstWhere(
          (f) => f['category'] == 'dns',
          orElse: () => <String, dynamic>{},
        );
        final dnsDetails =
            (dnsFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final dnsWarnings = (dnsDetails['warnings'] as List? ?? [])
            .cast<String>();
        final dnsError = dnsDetails['error'] as String?;
        _categories[6]
          ..status = dnsError != null
              ? ScanStatus.error
              : (dnsWarnings.isEmpty ? ScanStatus.ok : ScanStatus.warning)
          ..details = [
            if (dnsWarnings.isEmpty && dnsError == null)
              '設定に問題なし'
            else
              ...dnsWarnings,
            if (dnsError != null) dnsError,
          ];

        final sslFinding = findings.firstWhere(
          (f) => f['category'] == 'ssl_cert',
          orElse: () => <String, dynamic>{},
        );
        final sslDetails =
            (sslFinding['details'] as Map?)?.cast<String, dynamic>() ?? {};
        final sslExpired = sslDetails['expired'] as bool?;
        final sslHost = sslDetails['host'] as String? ?? '';
        final sslIssuer = sslDetails['issuer'] as String? ?? '';
        final sslDays = sslDetails['days_remaining'] as int?;
        final sslError = sslDetails['error'] as String?;
        _categories[7]
          ..status = sslError != null
              ? ScanStatus.error
              : (sslExpired == null
                    ? ScanStatus.error
                    : (sslExpired ? ScanStatus.warning : ScanStatus.ok))
          ..details = [
            if (sslHost.isNotEmpty) 'ホスト: $sslHost',
            if (sslIssuer.isNotEmpty) '発行者: $sslIssuer',
            if (sslDays != null && sslDays >= 0) '有効期限まで $sslDays 日',
            if (sslExpired == true) '証明書は期限切れ',
            if (sslExpired == false && (sslDays == null || sslDays >= 0))
              '証明書は有効',
            if (sslExpired == null && sslError == null) '情報取得失敗',
            if (sslError != null) sslError,
          ];

        for (final f in findings) {
          final cat = f['category'] as String? ?? '';
          if (!knownCats.contains(cat)) {
            final detailsMap =
                (f['details'] as Map?)?.cast<String, dynamic>() ?? {};
            final detailLines = detailsMap.entries
                .map((e) => '${e.key}: ${e.value}')
                .toList();
            final status = detailsMap['error'] != null
                ? ScanStatus.error
                : ScanStatus.ok;
            _categories.add(
              CategoryTile(
                title: cat,
                icon: Icons.help,
                status: status,
                details: detailLines,
              ),
            );
          }
        }
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
        return '未実行';
    }
  }

  Widget _buildSummary() {
    if (_summary.isEmpty) {
      return const SizedBox.shrink();
    }
    return Card(
      margin: const EdgeInsets.all(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: _summary.map((s) => Text(s)).toList(),
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
        ElevatedButton(
          key: const Key('staticButton'),
          style: ElevatedButton.styleFrom(backgroundColor: Colors.blueGrey),
          onPressed: _startScan,
          child: const Text('スキャン開始'),
        ),
        if (_isLoading)
          const Expanded(child: Center(child: CircularProgressIndicator()))
        else
          Expanded(
            child: Column(
              children: [
                _buildSummary(),
                Expanded(child: _buildCategoryList()),
              ],
            ),
          ),
      ],
    );
  }
}
