import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/services/dynamic_scan_api.dart';

void main() {
  test('startScan completes', () async {
    await expectLater(DynamicScanApi.startScan(), completes);
  });

  test('stopScan completes', () async {
    await expectLater(DynamicScanApi.stopScan(), completes);
  });

  test('fetchResults emits report', () async {
    final reports = await DynamicScanApi.fetchResults().toList();
    expect(reports, hasLength(1));
    final report = reports.first;
    expect(report.riskScore, 1);
    expect(report.categories.first.name, 'protocols');
    expect(report.categories.first.issues, contains('ftp'));
  });

  test('subscribeAlerts emits alerts', () async {
    final alerts = await DynamicScanApi.subscribeAlerts().toList();
    expect(alerts.first, contains('ALERT'));
    expect(alerts, hasLength(2));
  });

  test('fetchDnsHistory returns entries', () async {
    final hist = await DynamicScanApi.fetchDnsHistory(
      DateTime(2025, 1, 1),
      DateTime(2025, 1, 2),
    );
    expect(hist, isNotEmpty);
    expect(hist.first, contains('DNS History'));
  });
}
