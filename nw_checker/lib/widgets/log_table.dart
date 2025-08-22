import 'package:flutter/material.dart';

/// ログ表示用テーブルコンポーネントの雛形
class LogTable extends StatelessWidget {
  final List<DataRow> rows;
  final List<DataColumn> columns;
  final String placeholder;
  final bool showHeader;

  const LogTable({
    super.key,
    required this.rows,
    this.columns = const [DataColumn(label: Text('Log'))],
    this.placeholder = 'No logs',
    this.showHeader = true,
  });

  @override
  Widget build(BuildContext context) {
    final displayRows = rows.isNotEmpty
        ? rows
        : [
            DataRow(
              cells: [
                DataCell(Text(placeholder)),
                ...List.generate(
                  columns.length - 1,
                  (_) => const DataCell(Text('')),
                ),
              ],
            ),
          ];
    return DataTable(
      columns: columns,
      rows: displayRows,
      headingRowHeight: showHeader ? null : 0,
    );
  }
}
