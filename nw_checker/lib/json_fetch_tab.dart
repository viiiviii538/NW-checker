import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

/// Reusable tab widget that executes an async callback and displays JSON.
class JsonFetchTab extends StatefulWidget {
  const JsonFetchTab({
    super.key,
    required this.buttonText,
    required this.fetcher,
    this.buttonKey,
  });

  final String buttonText;
  final Future<Map<String, dynamic>> Function() fetcher;
  final Key? buttonKey;

  @override
  State<JsonFetchTab> createState() => _JsonFetchTabState();
}

class _JsonFetchTabState extends State<JsonFetchTab> {
  bool _isLoading = false;
  Map<String, dynamic>? _data;

  Future<void> _run() async {
    setState(() {
      _isLoading = true;
      _data = null;
    });

    await Future<void>.delayed(Duration.zero);
    try {
      final result = await widget.fetcher();
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _data = result;
      });
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _isLoading = false;
        _data = {'message': '結果がありません'};
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    Widget child;
    if (_isLoading) {
      child = const Center(child: CircularProgressIndicator());
    } else if (_data != null) {
      if (_data!.length == 1 && _data!.containsKey('message')) {
        child = Text(_data!['message'].toString());
      } else {
        final text = const JsonEncoder.withIndent('  ').convert(_data);
        child = SingleChildScrollView(child: SelectableText(text));
      }
    } else {
      child = ElevatedButton(
        key: widget.buttonKey,
        onPressed: _run,
        child: Text(widget.buttonText),
      );
    }
    return Center(child: child);
  }
}

/// Default CLI-backed implementations for dynamic scan and network map.
Future<Map<String, dynamic>> runDynamicCli() async {
  try {
    final resp = await http.get(
      Uri.parse('http://localhost:8000/scan/dynamic/results'),
    );
    if (resp.statusCode == 200) {
      return json.decode(resp.body) as Map<String, dynamic>;
    }
    return {'message': '結果がありません'};
  } catch (_) {
    return {'message': '結果がありません'};
  }
}

Future<Map<String, dynamic>> runNetworkCli() async {
  try {
    final result = await Process.run('python', [
      '-m',
      'src.network_map',
      '192.168.0.0/24',
    ]);
    if (result.exitCode != 0) {
      return {'message': '結果がありません'};
    }
    final lines = (result.stdout as String).trim().split('\n');
    final hosts = json.decode(lines.first);
    return {'hosts': hosts};
  } catch (_) {
    return {'message': '結果がありません'};
  }
}
