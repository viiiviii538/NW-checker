import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/network_scan.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('reads generated files when present', () async {
    final hostsFile = File('hosts.json');
    final svgFile = File('topology.svg');
    await hostsFile.writeAsString(
        '{"nodes":[{"id":"x","ip":"1","vendor":"v","hostname":"h","x":0,"y":0}]}'
    );
    await svgFile.writeAsString('<svg/>');
    final json = await NetworkScan.fetchHostsJson();
    final svg = await NetworkScan.fetchTopologySvg();
    expect(json['nodes'][0]['id'], 'x');
    expect(svg, contains('<svg'));
    await hostsFile.delete();
    await svgFile.delete();
  });

  test('falls back to bundled assets when script fails', () async {
    final assetJsonStr = await rootBundle.loadString('assets/hosts.json');
    final assetJson = json.decode(assetJsonStr) as Map<String, dynamic>;
    final jsonRes = await NetworkScan.fetchHostsJson();
    expect(jsonRes, assetJson);

    final assetSvg = await rootBundle.loadString('assets/topology.svg');
    final svgRes = await NetworkScan.fetchTopologySvg();
    expect(svgRes, assetSvg);
  });
}
