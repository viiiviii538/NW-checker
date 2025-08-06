import 'dart:async';
import '../models/scan_report.dart';

/// ダミーの動的スキャンAPI。
/// 実際のバックエンドとの通信は今後実装予定。
class DynamicScanApi {
  /// スキャンを開始する。
  static Future<void> startScan() async {
    // TODO: 実際のAPI呼び出しを実装
    await Future.delayed(const Duration(milliseconds: 300));
  }

  /// スキャンを停止する。
  static Future<void> stopScan() async {
    // TODO: 実際のAPI呼び出しを実装
    await Future.delayed(const Duration(milliseconds: 300));
  }

  /// スキャン結果をストリームで返す。
  /// 現状は1秒後にダミーのJSONをパースして返す。
  static Stream<ScanReport> fetchResults() {
    const dummyJson = {
      'riskScore': 87,
      'categories': [
        {
          'name': 'Ports',
          'severity': 'high',
          'issues': ['22/tcp open', '23/tcp open'],
        },
        {
          'name': 'SMB',
          'severity': 'medium',
          'issues': ['SMBv1 enabled'],
        },
        {
          'name': 'DNS',
          'severity': 'low',
          'issues': ['Zone transfer allowed'],
        },
      ],
    };
    return Stream.fromFuture(
      Future.delayed(
        const Duration(seconds: 1),
        () => ScanReport.fromJson(dummyJson),
      ),
    );
  }

  /// 指定期間の履歴を取得する。
  static Future<List<String>> fetchHistory(DateTime from, DateTime to) async {
    // TODO: 実際のAPI呼び出しを実装
    await Future.delayed(const Duration(milliseconds: 300));
    return ['History ${from.toIso8601String()} - ${to.toIso8601String()}'];
  }

  /// 指定期間の履歴を取得する。
  static Future<List<String>> fetchHistory(DateTime from, DateTime to) async {
    // TODO: 実際のAPI呼び出しを実装
    await Future.delayed(const Duration(milliseconds: 300));
    return ['History ${from.toIso8601String()} - ${to.toIso8601String()}'];
  }
}
