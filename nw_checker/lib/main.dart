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
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 4,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Network Checker'),
          bottom: const TabBar(
            tabs: [
              Tab(key: Key('tab-static'), text: '静的スキャン'),
              Tab(key: Key('tab-dynamic'), text: '動的スキャン'),
              Tab(key: Key('tab-network'), text: 'ネットワーク図'),
              Tab(key: Key('tab-test'), text: 'テスト'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            Center(
              child: Builder(
                builder:
                    (context) => ElevatedButton(
                      key: const Key('btn-static'),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('静的スキャンを実行しました')),
                        );
                      },
                      child: const Text('静的スキャンを実行'),
                    ),
              ),
            ),
            Center(
              child: Builder(
                builder:
                    (context) => ElevatedButton(
                      key: const Key('btn-dynamic'),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('動的スキャンを実行しました')),
                        );
                      },
                      child: const Text('動的スキャンを実行'),
                    ),
              ),
            ),
            Center(
              child: Builder(
                builder:
                    (context) => ElevatedButton(
                      key: const Key('btn-network'),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('ネットワーク図を表示しました')),
                        );
                      },
                      child: const Text('ネットワーク図を表示'),
                    ),
              ),
            ),
            Center(
              child: Builder(
                builder:
                    (context) => ElevatedButton(
                      key: const Key('btn-test'),
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('テストを開始しました')),
                        );
                      },
                      child: const Text('テストを開始'),
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
