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
}
