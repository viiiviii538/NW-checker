import 'dart:async';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nw_checker/services/static_scan_api.dart';

void main() {
  test('fetchScan returns findings and score', () async {
    final client = MockClient((request) async {
      return http.Response(
        '{"risk_score": 3, "findings": [{"category": "ports", "score": 1}]}',
        200,
      );
    });
    final result = await StaticScanApi.fetchScan(client: client);
    expect(result['risk_score'], 3);
    expect(result['findings'], isNotEmpty);
  });

  test('fetchScan throws on non-200 response', () async {
    final client = MockClient((request) async {
      return http.Response('{"detail": "fail"}', 500);
    });
    expect(StaticScanApi.fetchScan(client: client), throwsA(isA<Exception>()));
  });

  test('fetchScan throws on timeout', () async {
    final client = MockClient((request) async {
      await Future.delayed(const Duration(seconds: 10));
      return http.Response('slow', 200);
    });
    expect(
      StaticScanApi.fetchScan(client: client),
      throwsA(isA<TimeoutException>()),
    );
    client.close();
  });
}
