import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nw_checker/api_config.dart';
import 'package:nw_checker/services/dynamic_scan_api.dart';

void main() {
  tearDown(() {
    DynamicScanApi.client = http.Client();
    resetEnvApiBaseUrlForTest();
  });

  test('fetchDnsHistory parses and formats response', () async {
    setEnvApiBaseUrlForTest(() => 'http://mock');
    DynamicScanApi.client = MockClient((request) async {
      expect(
        request.url.toString(),
        'http://mock/dynamic-scan/dns-history?start=2025-01-01&end=2025-01-02',
      );
      return http.Response(
        jsonEncode({
          'history': [
            {
              'timestamp': '2025-01-01T00:00:00',
              'ip': '1.1.1.1',
              'hostname': 'host.example',
              'blacklisted': false,
            },
            {
              'timestamp': '2025-01-01T00:00:01',
              'ip': '2.2.2.2',
              'hostname': 'bad.example',
              'blacklisted': true,
            },
          ],
        }),
        200,
      );
    });

    final from = DateTime.parse('2025-01-01');
    final to = DateTime.parse('2025-01-02');
    final list = await DynamicScanApi.fetchDnsHistory(from, to);
    expect(list, [
      '2025-01-01T00:00:00 1.1.1.1 host.example',
      '2025-01-01T00:00:01 2.2.2.2 bad.example [BLACKLISTED]',
    ]);
  });
}
