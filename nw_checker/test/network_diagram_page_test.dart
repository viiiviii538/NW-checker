import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nw_checker/network_diagram_page.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  final hosts = {
    'nodes': [
      {
        'id': 'router',
        'ip': '192.168.0.1',
        'vendor': 'Cisco',
        'hostname': 'Router',
        'x': 100,
        'y': 100
      },
      {
        'id': 'server',
        'ip': '192.168.0.2',
        'vendor': 'Dell',
        'hostname': 'Server',
        'x': 300,
        'y': 100
      }
    ]
  };
  const svg = '<svg width="400" height="400"></svg>';

  testWidgets('search, filter, and interactive viewer works', (tester) async {
    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: NetworkDiagramPage(initialHosts: hosts, initialSvg: svg),
        ),
      ),
    );
    await tester.pump();
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('searchField')), findsOneWidget);

    await tester.enterText(
        find.byKey(const Key('searchField')), '192.168.0.1');
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('node-router')), findsOneWidget);
    expect(find.byKey(const Key('node-server')), findsNothing);

    await tester.enterText(find.byKey(const Key('searchField')), 'Dell');
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('node-server')), findsOneWidget);
    expect(find.byKey(const Key('node-router')), findsNothing);

    await tester.enterText(find.byKey(const Key('searchField')), 'Router');
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('node-router')));
    await tester.pumpAndSettle();

    final viewerFinder = find.byKey(const Key('diagramViewer'));
    final controller = tester
        .widget<InteractiveViewer>(viewerFinder)
        .transformationController!;
    controller.value = Matrix4.identity()..scale(2.0);
    await tester.pump();
    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1.0));

    controller.value = Matrix4.identity()..translate(50.0, 0.0);
    await tester.pump();
    expect(controller.value.getTranslation().x, isNot(0));
  });
}
