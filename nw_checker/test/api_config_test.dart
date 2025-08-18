import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/api_config.dart';

void main() {
  setUp(() {
    resetEnvApiBaseUrlForTest();
    resetIsWebForTest();
    resetPlatformIsAndroidForTest();
  });

  group('baseUrl', () {
    test('returns Android emulator host on Android', () {
      setPlatformIsAndroidForTest(() => true);
      expect(baseUrl(), 'http://10.0.2.2:8000');
    });

    test('returns localhost on non-Android', () {
      setPlatformIsAndroidForTest(() => false);
      expect(baseUrl(), 'http://localhost:8000');
    });

    test('returns override when API_BASE_URL is defined', () {
      setEnvApiBaseUrlForTest(() => 'https://example.com');
      setPlatformIsAndroidForTest(() => true);
      expect(baseUrl(), 'https://example.com');
    });

    test('returns localhost for web even on Android', () {
      setIsWebForTest(() => true);
      setPlatformIsAndroidForTest(() => true);
      expect(baseUrl(), 'http://localhost:8000');
    });
  });
}
