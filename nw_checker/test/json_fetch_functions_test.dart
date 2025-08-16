import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/json_fetch_tab.dart';

void main() {
  group('runDynamicCli', () {
    test('returns JSON on success', () async {
      final server = await HttpServer.bind('localhost', 8000);
      addTearDown(() => server.close(force: true));
      server.listen((request) {
        request.response
          ..statusCode = 200
          ..headers.contentType = ContentType.json
          ..write('{"ok": true}')
          ..close();
      });
      final result = await runDynamicCli();
      expect(result, {'ok': true});
    });

    test('returns message when backend fails', () async {
      final server = await HttpServer.bind('localhost', 8000);
      addTearDown(() => server.close(force: true));
      server.listen((request) {
        request.response
          ..statusCode = 500
          ..close();
      });
      final result = await runDynamicCli();
      expect(result, {'message': '結果がありません'});
    });
  });

  test('runNetworkCli returns message on failure', () async {
    final result = await runNetworkCli();
    expect(result, {'message': '結果がありません'});
  });
}
