import 'dart:convert';
import 'dart:io';
import 'package:flutter/services.dart' show rootBundle;

/// ネットワーク図データを読み込むユーティリティ。
class NetworkScan {
  static const _scriptPath = '../src/NWCD/generate_topology.py';

  /// Pythonスクリプトを実行して `hosts.json` と `topology.svg` を生成する。
  static Future<void> _runScanScript() async {
    try {
      await Process.run('python', [_scriptPath]).timeout(
        const Duration(seconds: 1),
      );
    } catch (_) {
      // スクリプト実行失敗時は静的アセットを利用
    }
  }

  /// ホスト情報JSONを取得。
  static Future<Map<String, dynamic>> fetchHostsJson() async {
    await _runScanScript();
    final file = File('hosts.json');
    if (await file.exists()) {
      final str = await file.readAsString();
      return json.decode(str) as Map<String, dynamic>;
    }
    final jsonStr = await rootBundle.loadString('assets/hosts.json');
    return json.decode(jsonStr) as Map<String, dynamic>;
  }

  /// トポロジSVGを取得。
  static Future<String> fetchTopologySvg() async {
    await _runScanScript();
    final file = File('topology.svg');
    if (await file.exists()) {
      return file.readAsString();
    }
    return rootBundle.loadString('assets/topology.svg');
  }
}
