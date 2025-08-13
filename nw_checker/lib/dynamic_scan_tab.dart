import 'package:flutter/material.dart';
import 'history_page.dart';
import 'models/scan_report.dart';
import 'services/dynamic_scan_api.dart';
import 'widgets/alert_component.dart';
import 'widgets/dynamic_scan_results.dart';

/// 動的スキャンタブのウィジェット。
class DynamicScanTab extends StatefulWidget {
  const DynamicScanTab({super.key});

  @override
  State<DynamicScanTab> createState() => _DynamicScanTabState();
}

class _DynamicScanTabState extends State<DynamicScanTab> {
  Stream<ScanReport>? _resultStream;
  ScanReport? _latestReport;
  bool _isScanning = false;
  Stream<String>? _alertStream;

  Future<void> _startScan() async {
    await DynamicScanApi.startScan();
    setState(() {
      _isScanning = true;
      _resultStream = DynamicScanApi.fetchResults();
      _alertStream = DynamicScanApi.subscribeAlerts();
    });
  }

  Future<void> _stopScan() async {
    await DynamicScanApi.stopScan();
    setState(() {
      _isScanning = false;
      _resultStream = null;
      _alertStream = null;
    });
  }

  void _exportPdf() {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('PDF export not implemented')));
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<String>(
      stream: _alertStream,
      builder: (context, alertSnapshot) {
        Widget? alertWidget;
        if (alertSnapshot.hasData) {
          final msg = alertSnapshot.data!;
          if (msg.startsWith('CRITICAL')) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              showDialog(
                context: context,
                builder: (_) => AlertDialog(
                  key: const Key('criticalAlertDialog'),
                  title: const Text('Critical Alert'),
                  content: Text(msg),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.of(context).pop(),
                      child: const Text('OK'),
                    ),
                  ],
                ),
              );
            });
          } else {
            alertWidget = AlertComponent(message: msg);
          }
        }
        return Column(
          children: [
            if (alertWidget != null) alertWidget!,
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: _isScanning ? null : _startScan,
                  child: const Text('スキャン開始'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: _isScanning ? _stopScan : null,
                  child: const Text('スキャン停止'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  key: const Key('historyButton'),
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const HistoryPage()),
                    );
                  },
                  child: const Text('履歴'),
                ),
              ],
            ),
            if (_isScanning)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 16),
                child: CircularProgressIndicator(),
              ),
            Expanded(
              child: StreamBuilder<ScanReport>(
                stream: _resultStream,
                builder: (context, snapshot) {
                  if (snapshot.hasData) {
                    _latestReport = snapshot.data;
                  }
                  final report = _latestReport;
                  if (report == null) {
                    return const SizedBox.shrink();
                  }
                  return Column(
                    children: [
                      _buildSummary(report),
                      Expanded(
                        child: DynamicScanResults(
                          categories: report.categories,
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSummary(ScanReport report) {
    return Card(
      margin: const EdgeInsets.all(8),
      child: ListTile(
        title: Text('Risk Score: ${report.riskScore}'),
        trailing: ElevatedButton.icon(
          onPressed: _exportPdf,
          icon: const Icon(Icons.picture_as_pdf),
          label: const Text('Export PDF'),
        ),
      ),
    );
  }
}
