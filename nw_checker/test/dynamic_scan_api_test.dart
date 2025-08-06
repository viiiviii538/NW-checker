import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/models/scan_report.dart';
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
    expect(report.riskScore, 87);
    expect(report.categories.first.name, 'Ports');
    expect(report.categories.first.issues, contains('22/tcp open'));
  });
}
