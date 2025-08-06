import 'dart:async';

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
  /// 現状は1秒ごとにダミーデータを追加する。
  static Stream<List<String>> fetchResults() {
    final results = <String>[];
    var count = 1;
    return Stream.periodic(const Duration(seconds: 1), (_) {
      results.add('Result line $count');
      count++;
      return List<String>.from(results);
    });
  }
}
