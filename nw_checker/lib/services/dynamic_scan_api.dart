import 'dart:async';

// ダミーデータを提供する動的スキャンAPI
final _dummyLines = <String>[
  'Starting dynamic scan...',
  'Scanning open ports...',
  'Analyzing network traffic...',
  'Scan complete.'
];

StreamController<List<String>>? _controller;
Timer? _timer;

/// スキャンを開始し、ダミー結果を順次ストリームへ流す
Future<void> startScan() async {
  await stopScan();
  _controller = StreamController<List<String>>.broadcast();
  final results = <String>[];
  var index = 0;
  _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
    if (index >= _dummyLines.length) {
      timer.cancel();
      _controller?.add(results);
      _controller?.close();
    } else {
      results.add(_dummyLines[index]);
      _controller?.add(List.from(results));
      index++;
    }
  });
}

/// スキャンを停止する
Future<void> stopScan() async {
  _timer?.cancel();
  _timer = null;
  await _controller?.close();
  _controller = null;
}

/// スキャン結果をストリームとして取得する
Stream<List<String>> fetchResults() {
  return _controller?.stream ?? const Stream<List<String>>.empty();
}

