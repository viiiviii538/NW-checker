import 'dart:convert';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nw_checker/network_scan.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('fetches topology data from network when available', () async {
    final client = MockClient((request) async {
      if (request.url.path.endsWith('topology.json')) {
        return http.Response('{"remote": true}', 200);
      }
      if (request.url.path.endsWith('topology.svg')) {
        return http.Response('<svg><remote/></svg>', 200);
      }
      return http.Response('', 404);
    });
    final json = await NetworkScan.fetchTopologyJson(client: client);
    final svg = await NetworkScan.fetchTopologySvg(client: client);
    expect(json['remote'], isTrue);
    expect(svg, contains('<remote/>'));
  });

  test('falls back to bundled assets on network failure', () async {
    final assetJsonStr = await rootBundle.loadString('assets/topology.json');
    final assetJson = json.decode(assetJsonStr) as Map<String, dynamic>;
    final failClient = MockClient((request) async => http.Response('err', 500));
    final jsonRes = await NetworkScan.fetchTopologyJson(client: failClient);
    expect(jsonRes, assetJson);

    final assetSvg = await rootBundle.loadString('assets/topology.svg');
    final svgRes = await NetworkScan.fetchTopologySvg(client: failClient);
    expect(svgRes, assetSvg);
  });
}
