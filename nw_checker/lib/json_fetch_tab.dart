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
        _data = {'message': 'No results'};
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    Widget child;
    if (_isLoading) {
      child = const Center(child: CircularProgressIndicator());
    } else if (_data != null) {
      final text = const JsonEncoder.withIndent('  ').convert(_data);
      child = SingleChildScrollView(child: SelectableText(text));
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
Future<Map<String, dynamic>> runDynamicCli({http.Client? client}) async {
  client ??= http.Client();
  try {
    final resp = await client.get(
      Uri.parse('http://localhost:8000/dynamic-scan/results'),
    );
    if (resp.statusCode == 200) {
      final decoded = jsonDecode(resp.body);
      if (decoded is Map<String, dynamic>) {
        return decoded;
      }
    }
  } catch (_) {}
  return {'message': 'No results'};
}

Future<Map<String, dynamic>> runNetworkCli() async {
  try {
    final result = await Process.run(
      'python',
      ['src/network_map.py', '192.168.0.0/24'],
    );
    if (result.exitCode == 0) {
      final lines = const LineSplitter().convert(result.stdout.toString());
      if (lines.isNotEmpty) {
        final decoded = jsonDecode(lines.first);
        if (decoded is List) {
          return {'hosts': decoded};
        } else if (decoded is Map<String, dynamic>) {
          return decoded;
        }
      }
    }
  } catch (_) {}
  return {'message': 'No results'};
}
