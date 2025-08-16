import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:nw_checker/json_fetch_tab.dart';

void main() {
  test('runDynamicCli returns data when server responds', () async {
    final client = MockClient((request) async {
      return http.Response('{"ok": true}', 200);
    });
    final result = await runDynamicCli(client: client);
    expect(result['ok'], isTrue);
  });

  test('runDynamicCli returns message when server errors', () async {
    final client = MockClient((request) async {
      throw http.ClientException('error');
    });
    final result = await runDynamicCli(client: client);
    expect(result['message'], 'No results');
  });

  test('runNetworkCli returns data when command succeeds', () async {
    final dir = Directory('src');
    final script = File('src/network_map.py');
    await dir.create();
    await script.writeAsString(
      'import json, sys; json.dump({"value": 42}, sys.stdout);\n',
    );
    try {
      final result = await runNetworkCli();
      expect(result['value'], 42);
    } finally {
      await script.delete();
      await dir.delete();
    }
  });

  test('runNetworkCli returns message on failure', () async {
    final result = await runNetworkCli();
    expect(result['message'], 'No results');
  });

  testWidgets('JsonFetchTab shows message when fetcher throws', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      MaterialApp(
        home: JsonFetchTab(
          buttonText: 'Run',
          fetcher: () async => throw Exception('fail'),
        ),
      ),
    );

    await tester.tap(find.text('Run'));
    await tester.pump();
    await tester.pumpAndSettle();
    expect(find.textContaining('No results'), findsOneWidget);
  });
}

