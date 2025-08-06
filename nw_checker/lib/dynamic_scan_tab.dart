import 'package:flutter/material.dart';
import 'models/scan_category.dart';
import 'models/scan_report.dart';
import 'services/dynamic_scan_api.dart';

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

  Future<void> _startScan() async {
    await DynamicScanApi.startScan();
    setState(() {
      _isScanning = true;
      _resultStream = DynamicScanApi.fetchResults();
    });
  }

  Future<void> _stopScan() async {
    await DynamicScanApi.stopScan();
    setState(() {
      _isScanning = false;
      _resultStream = null;
    });
  }

  void _exportPdf() {
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(const SnackBar(content: Text('PDF export not implemented')));
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
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
                  Expanded(child: _buildCategoryList(report.categories)),
                ],
              );
            },
          ),
        ),
      ],
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

  Widget _buildCategoryList(List<ScanCategory> categories) {
    return ListView(
      children:
          categories.map((cat) {
            return ExpansionTile(
              leading: Icon(
                categoryIcon(cat.name),
                color: severityColor(cat.severity),
              ),
              title: Text(cat.name),
              children:
                  cat.issues.map((e) => ListTile(title: Text(e))).toList(),
            );
          }).toList(),
    );
  }
}
