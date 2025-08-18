import 'dart:async';
import 'dart:convert';
import '../api_config.dart';
import '../models/scan_report.dart';
import 'package:http/http.dart' as http;

/// ダミーの動的スキャンAPI。
/// 実際のバックエンドとの通信は今後実装予定。
class DynamicScanApi {
  static String get _baseUrl => baseUrl();
  static const String _token = String.fromEnvironment(
    'API_TOKEN',
    defaultValue: '',
  );

  static Map<String, String> _headers() => _token.isEmpty
      ? {'Content-Type': 'application/json'}
      : {'Content-Type': 'application/json', 'Authorization': 'Bearer $_token'};

  /// スキャンを開始する。
  static Future<void> startScan() async {
    try {
      await http.post(
        Uri.parse('$_baseUrl/dynamic-scan/start'),
        headers: _headers(),
        body: jsonEncode({}),
      );
    } catch (_) {
      // 接続できない場合は無視（テスト環境など）
    }
    await Future.delayed(const Duration(milliseconds: 300));
  }

  /// スキャンを停止する。
  static Future<void> stopScan() async {
    try {
      await http.post(
        Uri.parse('$_baseUrl/dynamic-scan/stop'),
        headers: _headers(),
      );
    } catch (_) {}
    await Future.delayed(const Duration(milliseconds: 300));
  }

  /// スキャン結果をストリームで返す。
  /// 実際のAPI呼び出しを試み、失敗時はダミーデータを返す。
  static Stream<ScanReport> fetchResults() async* {
    try {
      final resp = await http.get(
        Uri.parse('$_baseUrl/dynamic-scan/results'),
        headers: _headers(),
      );
      if (resp.statusCode == 200) {
        final decoded = jsonDecode(resp.body) as Map<String, dynamic>;
        yield ScanReport.fromJson({
          'riskScore': decoded['risk_score'] ?? 0,
          'categories': decoded['categories'] ?? [],
        });
        return;
      }
    } catch (_) {}

    const dummyJson = {
      'risk_score': 1,
      'categories': [
        {
          'name': 'protocols',
          'severity': 'high',
          'issues': ['ftp'],
        },
        {
          'name': 'dhcp',
          'severity': 'medium',
          'issues': ['10.0.0.1', 'WARNING: Multiple DHCP servers detected'],
        },
      ],
    };
    yield await Future.delayed(
      const Duration(seconds: 1),
      () => ScanReport.fromJson({
        'riskScore': dummyJson['risk_score'] as int,
        'categories': dummyJson['categories'],
      }),
    );
  }

  /// 指定期間の履歴を取得する。
  static Future<List<String>> fetchHistory(DateTime from, DateTime to) async {
    try {
      final resp = await http.get(
        Uri.parse(
          '$_baseUrl/dynamic-scan/history?start=${from.toIso8601String()}&end=${to.toIso8601String()}',
        ),
        headers: _headers(),
      );
      if (resp.statusCode == 200) {
        final decoded = jsonDecode(resp.body) as Map<String, dynamic>;
        final results = decoded['results'];
        if (results is List) {
          return results.cast<String>();
        }
      }
    } catch (_) {}
    await Future.delayed(const Duration(milliseconds: 300));
    return ['History ${from.toIso8601String()} - ${to.toIso8601String()}'];
  }

  /// アラート通知を購読する。
  /// 現状は2秒毎に2件のダミーアラートを流す。
  /// 実装済みの `/ws/dynamic-scan` WebSocket が利用可能になれば置き換え予定。
  static Stream<String> subscribeAlerts() {
    return Stream.periodic(const Duration(seconds: 2), (count) {
      if (count == 0) {
        return 'ALERT: Port scan detected';
      }
      return 'CRITICAL: Malware detected';
    }).take(2);
  }
}
