import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;
import 'package:meta/meta.dart';

/// Returns the base URL for API calls.
///
/// [--dart-define=API_BASE_URL] can override the value.
String baseUrl() {
  final override = _envApiBaseUrl();
  if (override.isNotEmpty) {
    return override;
  }
  if (_isWeb()) {
    return 'http://localhost:8000';
  }
  if (_platformIsAndroid()) {
    // Android エミュレータからホストのlocalhostにアクセスする場合
    return 'http://10.0.2.2:8000';
  }
  return 'http://localhost:8000';
}

String Function() _envApiBaseUrl = () =>
    const String.fromEnvironment('API_BASE_URL', defaultValue: '');

bool Function() _isWeb = () => kIsWeb;

bool Function() _platformIsAndroid = () => Platform.isAndroid;

/// 以下はテスト用ヘルパー。
@visibleForTesting
void setEnvApiBaseUrlForTest(String Function() fn) {
  _envApiBaseUrl = fn;
}

@visibleForTesting
void resetEnvApiBaseUrlForTest() {
  _envApiBaseUrl = () =>
      const String.fromEnvironment('API_BASE_URL', defaultValue: '');
}

@visibleForTesting
void setIsWebForTest(bool Function() fn) {
  _isWeb = fn;
}

@visibleForTesting
void resetIsWebForTest() {
  _isWeb = () => kIsWeb;
}

@visibleForTesting
void setPlatformIsAndroidForTest(bool Function() fn) {
  _platformIsAndroid = fn;
}

@visibleForTesting
void resetPlatformIsAndroidForTest() {
  _platformIsAndroid = () => Platform.isAndroid;
}
