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
      home: const HomePage(),
    );
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key, this.testOutput = _dummyTestOutput});

  /// 表示する診断結果（後でPython側から差し替え予定）
  final String testOutput;

  /// 仮の診断結果（ダミーデータ）
  static const String _dummyTestOutput = '''
[SCAN] TCP 3389 OPEN :: HIGH RISK (RDP) [WARN]
[SCAN] TCP 445 OPEN :: HIGH RISK (SMB) [WARN]
[SCAN] TCP 21 OPEN :: FTP (ANON) [WARN]
[SCAN] TCP 80 OPEN :: HTTP/1.1
NOTE: Multiple external ports detected.

[BANNER] 192.168.1.10:445 OS: WinServer2012R2 (EOL)
[BANNER] 192.168.1.15:80 SVC: Apache/2.2.15 (VULNERABLE)

[SMB] RESPONDING
[NETBIOS] RESPONDING
[UPNP] ENABLED
[ARP] Multiple replies detected (protection: NONE)
[DHCP] DUPLICATE (192.168.1.1 / 192.168.1.200)
[DNS] External: 8.8.8.8 / 114.114.114.114
[SSL] example.co.jp EXP: 12 days (AUTORENEW: DISABLED)
RISK SCORE: 92/100
STATUS: CRITICAL
(output truncated)
''';

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
            Container(
              color: Colors.white,
              padding: const EdgeInsets.all(8.0),
              child: Scrollbar(
                thumbVisibility: true,
                child: SingleChildScrollView(
                  child: SelectableText(
                    testOutput,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 13,
                      color: Colors.black,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
