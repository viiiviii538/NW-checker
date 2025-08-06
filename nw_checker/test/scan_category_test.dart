import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/models/scan_category.dart';

void main() {
  test('severityFromString handles values', () {
    expect(severityFromString('HIGH'), Severity.high);
    expect(severityFromString('Medium'), Severity.medium);
    expect(severityFromString('unknown'), Severity.low);
  });

  test('severityColor maps to colors', () {
    expect(severityColor(Severity.high), Colors.red);
    expect(severityColor(Severity.medium), Colors.orange);
    expect(severityColor(Severity.low), Colors.green);
  });

  test('categoryIcon returns expected icons', () {
    expect(categoryIcon('Ports'), Icons.router);
    expect(categoryIcon('SMB'), Icons.folder_shared);
    expect(categoryIcon('DNS'), Icons.language);
    expect(categoryIcon('Other'), Icons.security);
  });
}
