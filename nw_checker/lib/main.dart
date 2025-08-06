import 'package:flutter/material.dart';
import 'static_scan_tab.dart';
import 'history_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Network Checker',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: HomePage(),
    );
  }
}

class HomePage extends StatefulWidget {
  HomePage({super.key, List<String>? testOutputLines})
    : testOutputLines = testOutputLines ?? _generateDummyOutput();

  /// 表示する診断結果（後でPython側から差し替え予定）
  final List<String> testOutputLines;

  /// 仮の診断結果（ダミーデータ）
  static List<String> _generateDummyOutput() {
    final timestamp = DateTime.now().toString().split('.').first;
    return [
      '=== NETWORK SECURITY SCAN REPORT ===',
      'Scan Date: $timestamp',
      '-------------------- SECTION --------------------',
      '[SCAN] TCP 3389 OPEN :: HIGH RISK (RDP) [WARN]',
      '[SCAN] TCP 445 OPEN :: HIGH RISK (SMB) [WARN]',
      '[SCAN] TCP 21 OPEN :: FTP (ANON) [WARN]',
      '[SCAN] TCP 80 OPEN :: HTTP [INFO]',
      'NOTE: Multiple external ports detected (exposed to WAN).',
      '',
      '-------------------- SECTION --------------------',
      '[BANNER] 192.168.1.20:3389 OS: WinServer2016 (EOL)',
      '[DEVICE] IoT camera detected (192.168.1.50) - Firmware outdated (820 days)',
      '',
      '-------------------- SECTION --------------------',
      '[DNS] External: 8.8.8.8 (Google) / 114.114.114.114 (China Telecom)',
      'NOTE: At least one DNS server is located outside Japan.',
      '',
      '[CONNECTIONS] Suspicious outbound traffic detected:',
      '  - 192.168.1.15 → 185.143.220.13 (RU) [PORT 443] [Unknown certificate issuer]',
      '  - 192.168.1.22 → 203.113.25.42 (VN) [PORT 8080] [Service: proxy]',
      'NOTE: Connections to high-risk countries (RU, VN) observed.',
      '',
      '-------------------- SECTION --------------------',
      '[SSL] expired.example.com EXP: -5 days (CERT EXPIRED)',
      '[SSL] secure.example.jp EXP: 7 days (AUTORENEW: DISABLED) [WARN]',
      '',
      '-------------------- SECTION --------------------',
      'RISK SCORE: 97/100',
      'STATUS: CRITICAL',
      'SUMMARY: Multiple high-risk services open, outdated firmware, expired SSL, and outbound traffic to blacklisted regions detected.',
      '(output truncated)',
    ];
  }

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> with TickerProviderStateMixin {
  bool _showTestOutput = false;
  bool _isLoading = false;
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 5, vsync: this);
  }

  List<InlineSpan> _buildOutputSpans(Iterable<String> lines) {
    const warnStyle = TextStyle(
      color: Color(0xFFB71C1C),
      backgroundColor: Color(0xFFFFEBEE),
      fontWeight: FontWeight.bold,
    );
    const infoStyle = TextStyle(
      color: Color(0xFF0D47A1),
      backgroundColor: Color(0xFFE3F2FD),
      fontWeight: FontWeight.bold,
    );
    const noteStyle = TextStyle(
      color: Color(0xFF004D40),
      fontStyle: FontStyle.italic,
    );
    const sectionStyle = TextStyle(
      color: Color(0xFF666666),
      fontWeight: FontWeight.w400,
    );
    const labelTextStyle = TextStyle(
      fontFamily: 'Courier New',
      fontFamilyFallback: ['Consolas', 'monospace'],
      fontSize: 12,
      height: 1.2,
      color: Colors.white,
      fontWeight: FontWeight.w600,
    );

    final spans = <InlineSpan>[];
    for (final line in lines) {
      if (line.startsWith('STATUS:')) {
        final status = line.substring('STATUS: '.length);
        spans.add(const TextSpan(text: 'STATUS: '));
        spans.add(
          WidgetSpan(
            alignment: PlaceholderAlignment.middle,
            child: Container(
              color: const Color(0xFFD32F2F),
              padding: const EdgeInsets.all(4),
              child: Text(status, style: labelTextStyle),
            ),
          ),
        );
        spans.add(const TextSpan(text: '\n'));
        continue;
      }
      if (line.startsWith('NOTE:')) {
        spans.add(TextSpan(text: line, style: noteStyle));
        spans.add(const TextSpan(text: '\n'));
        continue;
      }
      if (line.startsWith('--------------------')) {
        spans.add(TextSpan(text: line, style: sectionStyle));
        spans.add(const TextSpan(text: '\n'));
        continue;
      }
      final combinedRegex = RegExp(r'\[HIGH RISK\]|\[WARN\]|CRITICAL|\[INFO\]');
      int start = 0;
      for (final match in combinedRegex.allMatches(line)) {
        if (match.start > start) {
          spans.add(TextSpan(text: line.substring(start, match.start)));
        }
        final text = match.group(0)!;
        TextStyle? style;
        if (RegExp(r'\[HIGH RISK\]|\[WARN\]|CRITICAL').hasMatch(text)) {
          style = warnStyle;
        } else if (text == '[INFO]') {
          style = infoStyle;
        }
        spans.add(TextSpan(text: text, style: style));
        start = match.end;
      }
      spans.add(TextSpan(text: line.substring(start)));
      spans.add(const TextSpan(text: '\n'));
    }
    return spans;
  }

  Widget _buildReportContent() {
    final baseStyle = const TextStyle(
      fontFamily: 'Courier New',
      fontFamilyFallback: ['Consolas', 'monospace'],
      fontSize: 12,
      height: 1.2,
      fontWeight: FontWeight.w600,
      color: Colors.black,
    );
    final lines = widget.testOutputLines;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          width: double.infinity,
          color: Colors.black,
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Text(
            lines.first,
            style: baseStyle.copyWith(color: Colors.white),
          ),
        ),
        Align(
          alignment: Alignment.centerRight,
          child: Text(lines[1], style: baseStyle),
        ),
        SelectableText.rich(
          TextSpan(children: _buildOutputSpans(lines.skip(2))),
          style: baseStyle,
        ),
      ],
    );
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Network Checker'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(key: Key('staticTab'), text: '静的スキャン'),
            Tab(key: Key('dynamicTab'), text: '動的スキャン'),
            Tab(key: Key('historyTab'), text: '履歴'),
            Tab(key: Key('networkTab'), text: 'ネットワーク図'),
            Tab(key: Key('testTab'), text: 'テスト'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          const StaticScanTab(),
          Center(
            child: ElevatedButton(
              key: const Key('dynamicButton'),
              onPressed: () {
                ScaffoldMessenger.of(
                  context,
                ).showSnackBar(const SnackBar(content: Text('動的スキャンを実行しました')));
              },
              child: const Text('動的スキャンを実行'),
            ),
          ),
          const HistoryPage(),
          Center(
            child: ElevatedButton(
              key: const Key('networkButton'),
              onPressed: () {
                ScaffoldMessenger.of(
                  context,
                ).showSnackBar(const SnackBar(content: Text('ネットワーク図を表示しました')));
              },
              child: const Text('ネットワーク図を表示'),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              children: [
                ElevatedButton(
                  onPressed: () {
                    setState(() {
                      _isLoading = true;
                      _showTestOutput = false;
                    });
                    Future.delayed(const Duration(seconds: 3), () {
                      if (!mounted) return;
                      setState(() {
                        _isLoading = false;
                        _showTestOutput = true;
                      });
                    });
                  },
                  child: const Text('テストを実行'),
                ),
                if (_isLoading)
                  const Expanded(
                    child: Center(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          CircularProgressIndicator(),
                          SizedBox(height: 16),
                          Text('Loading...'),
                        ],
                      ),
                    ),
                  )
                else if (_showTestOutput)
                  Expanded(
                    child: Container(
                      color: const Color(0xFFF4F4F4),
                      alignment: Alignment.topCenter,
                      child: Scrollbar(
                        thumbVisibility: true,
                        child: SingleChildScrollView(
                          child: Container(
                            width: 700,
                            margin: const EdgeInsets.symmetric(vertical: 16),
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.15),
                                  blurRadius: 8,
                                ),
                              ],
                            ),
                            child: _buildReportContent(),
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
