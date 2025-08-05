import 'package:flutter/material.dart';

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
      '[SCAN] TCP  445 OPEN :: HIGH RISK (SMB) [WARN]',
      '[SCAN] TCP   21 OPEN :: FTP (ANON) [WARN]',
      '[SCAN] TCP   80 OPEN :: HTTP/1.1',
      'NOTE: Multiple external ports detected.',
      '-------------------- SECTION --------------------',
      '[BANNER] 192.168.1.10:445 OS: WinServer2012R2 (EOL)',
      '[BANNER] 192.168.1.15:80 SVC: Apache/2.2.15 (VULNERABLE)',
      '-------------------- SECTION --------------------',
      '[SMB] RESPONDING',
      '[NETBIOS] RESPONDING',
      '[UPNP] ENABLED',
      '[ARP] Multiple replies detected (protection: NONE)',
      '[DHCP] DUPLICATE (192.168.1.1 / 192.168.1.200)',
      '[DNS] External: 8.8.8.8 / 114.114.114.114',
      '[SSL] example.co.jp EXP: 12 days (AUTORENEW: DISABLED)',
      '-------------------- SECTION --------------------',
      'RISK SCORE: 92/100',
      'STATUS: CRITICAL',
      '(output truncated)',
    ];
  }

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  bool _showTestOutput = false;
  bool _isLoading = false;

  List<InlineSpan> _buildOutputSpans() {
    const warnStyle = TextStyle(
      color: Color(0xFFCC0000),
      fontWeight: FontWeight.bold,
    );
    const labelTextStyle = TextStyle(
      fontFamily: 'Courier New',
      fontFamilyFallback: ['Consolas', 'monospace'],
      fontSize: 12,
      height: 1.2,
      color: Colors.white,
      fontWeight: FontWeight.bold,
    );

    final spans = <InlineSpan>[];
    for (final line in widget.testOutputLines) {
      if (line.startsWith('STATUS:')) {
        spans.add(const TextSpan(text: 'STATUS: '));
        spans.add(
          WidgetSpan(
            alignment: PlaceholderAlignment.middle,
            child: Container(
              color: const Color(0xFFCC0000),
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
              child: const Text('CRITICAL', style: labelTextStyle),
            ),
          ),
        );
        spans.add(const TextSpan(text: '\n'));
        continue;
      }
      final regex = RegExp(r'HIGH RISK|\[WARN\]');
      int start = 0;
      for (final match in regex.allMatches(line)) {
        if (match.start > start) {
          spans.add(TextSpan(text: line.substring(start, match.start)));
        }
        spans.add(TextSpan(text: match.group(0), style: warnStyle));
        start = match.end;
      }
      spans.add(TextSpan(text: line.substring(start)));
      spans.add(const TextSpan(text: '\n'));
    }
    return spans;
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Network Checker'),
          bottom: const TabBar(
            tabs: [
              Tab(text: '静的スキャン'),
              Tab(text: '動的スキャン'),
              Tab(text: 'ネットワーク図'),
              Tab(text: 'テスト'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            Center(
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('静的スキャンを実行しました')),
                  );
                },
                child: const Text('静的スキャンを実行'),
              ),
            ),
            Center(
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('動的スキャンを実行しました')),
                  );
                },
                child: const Text('動的スキャンを実行'),
              ),
            ),
            Center(
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('ネットワーク図を表示しました')),
                  );
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
                      Future.delayed(const Duration(seconds: 90), () {
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
                      child: Center(child: CircularProgressIndicator()),
                    )
                  else if (_showTestOutput)
                    Expanded(
                      child: Container(
                        decoration: BoxDecoration(
                          color: const Color(0xFFFAFAFA),
                          border: Border.all(color: Color(0xFF999999)),
                        ),
                        padding: const EdgeInsets.all(8.0),
                        child: Scrollbar(
                          thumbVisibility: true,
                          child: SingleChildScrollView(
                            child: SelectableText.rich(
                              TextSpan(children: _buildOutputSpans()),
                              style: const TextStyle(
                                fontFamily: 'Courier New',
                                fontFamilyFallback: ['Consolas', 'monospace'],
                                fontSize: 12,
                                height: 1.2,
                                color: Colors.black,
                              ),
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
      ),
    );
  }
}
