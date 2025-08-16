import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vector_math/vector_math_64.dart' show Matrix4;

import 'package:nw_checker/network_diagram_page.dart';

void main() {
  testWidgets('search, filter, and interactive viewer works', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: NetworkDiagramPage())),
    );
    await tester.pump();
    await tester.pump(const Duration(seconds: 1));

    await tester.enterText(find.byKey(const Key('searchField')), 'router');
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('node-router')), findsOneWidget);
    expect(find.byKey(const Key('node-server')), findsNothing);

    await tester.tap(find.byKey(const Key('node-router')));
    await tester.pumpAndSettle();
    expect(find.text('Router'), findsOneWidget);
    final container = tester.widget<Container>(
      find.descendant(
        of: find.byKey(const Key('node-router')),
        matching: find.byType(Container),
      ),
    );
    final BoxDecoration? deco = container.decoration as BoxDecoration?;
    expect(deco?.border, isNotNull);

    final viewerFinder = find.byKey(const Key('diagramViewer'));
    final controller = tester
        .widget<InteractiveViewer>(viewerFinder)
        .transformationController!;
    final Offset center = tester.getCenter(viewerFinder);

    final TestGesture g1 = await tester.startGesture(
      center - const Offset(10, 0),
    );
    final TestGesture g2 = await tester.startGesture(
      center + const Offset(10, 0),
    );
    await tester.pump();
    await g1.moveTo(center - const Offset(40, 0));
    await g2.moveTo(center + const Offset(40, 0));
    await tester.pump();
    await g1.up();
    await g2.up();
    await tester.pumpAndSettle();
    expect(controller.value.getMaxScaleOnAxis(), greaterThan(1.0));

    final TestGesture gesture = await tester.startGesture(center);
    await gesture.moveBy(const Offset(50, 0));
    await gesture.up();
    await tester.pumpAndSettle();
    expect(controller.value.getTranslation().x, isNot(0));
  });
}
