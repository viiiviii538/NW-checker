import 'dart:convert';
import '../api_config.dart';
import 'package:http/http.dart' as http;

/// 静的スキャンAPIへの通信を担当するサービス。
/// `/static_scan` エンドポイントを呼び出し結果を返す。
class StaticScanApi {
  static String get _baseUrl => baseUrl();
  static const String _token = String.fromEnvironment(
    'API_TOKEN',
    defaultValue: '',
  );

  static Map<String, String> _headers() => _token.isEmpty
      ? {'Content-Type': 'application/json'}
      : {'Content-Type': 'application/json', 'Authorization': 'Bearer $_token'};

  /// 静的スキャンを実行し結果を取得する。
  /// 成功時は `findings` と `risk_score` を含むマップを返す。
  /// 失敗時は例外を投げる。
  static Future<Map<String, dynamic>> fetchScan({http.Client? client}) async {
    final created = client == null;
    final c = client ?? http.Client();
    try {
      final resp = await c
          .get(Uri.parse('$_baseUrl/static_scan'), headers: _headers())
          .timeout(const Duration(seconds: 5));
      if (resp.statusCode == 200) {
        final decoded = jsonDecode(resp.body) as Map<String, dynamic>;
        final findings =
            (decoded['findings'] as List?)?.cast<Map<String, dynamic>>() ?? [];
        final riskScore = decoded['risk_score'] ?? 0;
        return {'findings': findings, 'risk_score': riskScore};
      }
      String message;
      try {
        final err = jsonDecode(resp.body);
        if (err is Map && err['detail'] != null) {
          message = err['detail'].toString();
        } else if (err is Map && err['message'] != null) {
          message = err['message'].toString();
        } else {
          message = 'HTTP ${resp.statusCode}';
        }
      } catch (_) {
        message = 'HTTP ${resp.statusCode}';
      }
      throw Exception(message);
    } catch (e) {
      // 呼び出し元で処理できるようそのまま再スロー
      rethrow;
    } finally {
      if (created) {
        c.close();
      }
    }
  }
}
