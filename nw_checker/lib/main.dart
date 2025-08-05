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
                    const SnackBar(
                      content: Text('静的スキャンを実行しました'),
                    ),
                  );
                },
                child: const Text('静的スキャンを実行'),
              ),
            ),
            Center(
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('動的スキャンを実行しました'),
                    ),
                  );
                },
                child: const Text('動的スキャンを実行'),
              ),
            ),
            Center(
              child: ElevatedButton
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('ネットワーク図を表示しました'),
                    ),
                  );
                },
                child: const Text('ネットワーク図を表示'),
              ),
            ),
            Center(
              child: ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('テストを開始しました'),
                    ),
                  );
                },
                child: const Text('テストを開始'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
