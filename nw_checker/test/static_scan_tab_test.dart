import 'package:flutter_test/flutter_test.dart';
import 'package:fake_async/fake_async.dart';
import 'package:nw_checker/static_scan_tab.dart';

void main() {
  test('performStaticScan returns dummy report', () {
    fakeAsync((async) {
      performStaticScan().then(expectAsync1((lines) {
        expect(
          lines,
          equals([
            '=== STATIC SCAN REPORT ===',
            'No issues detected.',
          ]),
        );
      }));
      async.elapse(const Duration(seconds: 90));
      async.flushMicrotasks();
    });
  });
}
