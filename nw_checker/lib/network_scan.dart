import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;

/// ネットワーク図データを読み込むユーティリティ。
class NetworkScan {
  /// トポロジJSONを取得。
  static Future<Map<String, dynamic>> fetchTopologyJson() async {
    final jsonStr = await rootBundle.loadString('assets/topology.json');
    return json.decode(jsonStr) as Map<String, dynamic>;
  }

  /// トポロジSVGを取得。
  static Future<String> fetchTopologySvg() {
    return rootBundle.loadString('assets/topology.svg');
  }
}
