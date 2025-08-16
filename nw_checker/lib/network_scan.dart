import 'dart:convert';
import 'package:flutter/services.dart' show rootBundle;
import 'package:http/http.dart' as http;

/// ネットワーク図データを読み込むユーティリティ。
class NetworkScan {
  static const _jsonUrl = 'http://localhost:8000/topology.json';
  static const _svgUrl = 'http://localhost:8000/topology.svg';

  /// トポロジJSONを取得。
  static Future<Map<String, dynamic>> fetchTopologyJson({
    http.Client? client,
  }) async {
    final http.Client c = client ?? http.Client();
    try {
      final res = await c
          .get(Uri.parse(_jsonUrl))
          .timeout(const Duration(milliseconds: 200));
      if (res.statusCode == 200) {
        return json.decode(res.body) as Map<String, dynamic>;
      }
    } catch (_) {
      // ネットワーク取得失敗時はアセットを利用
    } finally {
      if (client == null) {
        c.close();
      }
    }
    final jsonStr = await rootBundle.loadString('assets/topology.json');
    return json.decode(jsonStr) as Map<String, dynamic>;
  }

  /// トポロジSVGを取得。
  static Future<String> fetchTopologySvg({http.Client? client}) async {
    final http.Client c = client ?? http.Client();
    try {
      final res = await c
          .get(Uri.parse(_svgUrl))
          .timeout(const Duration(milliseconds: 200));
      if (res.statusCode == 200) {
        return res.body;
      }
    } catch (_) {
      // ネットワーク取得失敗時はアセットを利用
    } finally {
      if (client == null) {
        c.close();
      }
    }
    return rootBundle.loadString('assets/topology.svg');
  }
}
