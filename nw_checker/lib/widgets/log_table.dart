import 'package:flutter/material.dart';

/// ログ表示用テーブルコンポーネント
class LogTable extends StatelessWidget {
  final List<DataRow> rows;

  const LogTable({super.key, required this.rows});

  @override
  Widget build(BuildContext context) {
    return DataTable(
      columns: const [DataColumn(label: Text('Log'))],
      rows:
          rows.isNotEmpty
              ? rows
              : const [
                DataRow(cells: [DataCell(Text('No logs'))]),
              ],
    );
  }
}
