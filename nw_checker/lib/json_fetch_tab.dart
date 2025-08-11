import 'dart:convert';

import 'package:flutter/material.dart';

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
    final result = await widget.fetcher();
    if (!mounted) return;
    setState(() {
      _isLoading = false;
      _data = result;
    });
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
Future<Map<String, dynamic>> runDynamicCli() async {
  // In production this would call a real CLI or backend service.
  await Future.delayed(const Duration(seconds: 1));
  return {'status': 'dynamic'};
}

Future<Map<String, dynamic>> runNetworkCli() async {
  // In production this would call a real CLI or backend service.
  await Future.delayed(const Duration(seconds: 1));
  return {'status': 'network'};
}
