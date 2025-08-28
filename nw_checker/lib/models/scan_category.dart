import 'package:flutter/material.dart';

/// スキャン結果のカテゴリ。
class ScanCategory {
  final String name;
  final Severity severity;
  final List<String> issues;

  ScanCategory({
    required this.name,
    required this.severity,
    required this.issues,
  });

  factory ScanCategory.fromJson(Map<String, dynamic> json) {
    return ScanCategory(
      name: json['name'] as String,
      severity: severityFromString(json['severity'] as String? ?? ''),
      issues: (json['issues'] as List<dynamic>? ?? []).cast<String>(),
    );
  }
}

/// 危険度。
enum Severity { low, medium, high }

/// 文字列から危険度へ変換。
Severity severityFromString(String value) {
  switch (value.toLowerCase()) {
    case 'high':
      return Severity.high;
    case 'medium':
      return Severity.medium;
    case 'low':
    default:
      return Severity.low;
  }
}

/// 危険度に応じた色を返す。
Color severityColor(Severity severity) {
  switch (severity) {
    case Severity.high:
      return Colors.red;
    case Severity.medium:
      return Colors.orange;
    case Severity.low:
      return Colors.green;
  }
}

/// カテゴリ名に応じたアイコンを返す。
IconData categoryIcon(String name) {
  switch (name.toLowerCase()) {
    case 'ports':
      return Icons.router;
    case 'smb':
      return Icons.folder_shared;
    case 'dns':
      return Icons.language;
    case 'traffic':
      return Icons.traffic;
    default:
      return Icons.security;
  }
}
