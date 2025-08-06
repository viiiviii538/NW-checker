import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/scan_result_detail_page.dart';

void main() {
  testWidgets('ScanResultDetailPage shows detail text', (tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: ScanResultDetailPage(title: 'Ports', detail: '22/tcp open'),
    ));
    expect(find.text('22/tcp open'), findsOneWidget);
  });
}
