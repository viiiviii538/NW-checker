import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/services/dynamic_scan_api.dart';

void main() {
  test('startScan completes', () async {
    await expectLater(DynamicScanApi.startScan(), completes);
  });

  test('stopScan completes', () async {
    await expectLater(DynamicScanApi.stopScan(), completes);
  });

  test('fetchResults emits growing lists', () async {
    final values = await DynamicScanApi.fetchResults().take(2).toList();
    expect(values[0], ['Result line 1']);
    expect(values[1], ['Result line 1', 'Result line 2']);
  });

  test('fetchHistory returns date range lines', () async {
    final from = DateTime(2024, 1, 1);
    final to = DateTime(2024, 1, 2);
    final res = await DynamicScanApi.fetchHistory(from, to);
    expect(res.length, 2);
    expect(res[0], 'History from ' + from.toIso8601String());
    expect(res[1], 'History to ' + to.toIso8601String());
  });
}
