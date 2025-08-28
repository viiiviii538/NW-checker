import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'network_scan.dart';

/// SVGネットワーク図を表示するページ。
class NetworkDiagramPage extends StatefulWidget {
  final Map<String, dynamic>? initialHosts;
  final String? initialSvg;
  const NetworkDiagramPage({super.key, this.initialHosts, this.initialSvg});

  @override
  State<NetworkDiagramPage> createState() => _NetworkDiagramPageState();
}

class _NetworkDiagramPageState extends State<NetworkDiagramPage> {
  Map<String, dynamic>? _hosts;
  String? _svg;
  String _search = '';
  Map<String, dynamic>? _selected;
  final TransformationController _controller = TransformationController();

  @override
  void initState() {
    super.initState();
    if (widget.initialHosts != null && widget.initialSvg != null) {
      _hosts = widget.initialHosts;
      _svg = widget.initialSvg;
    } else {
      _load();
    }
  }

  Future<void> _load() async {
    final topo = await NetworkScan.fetchHostsJson();
    final svg = await NetworkScan.fetchTopologySvg();
    if (!mounted) return;
    setState(() {
      _hosts = topo;
      _svg = svg;
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_svg == null) {
      return const Center(child: CircularProgressIndicator());
    }
    final nodes = (_hosts?['nodes'] as List<dynamic>? ?? [])
        .where((n) {
          final q = _search.toLowerCase();
          return n['ip'].toString().contains(q) ||
              n['vendor'].toString().toLowerCase().contains(q) ||
              n['hostname'].toString().toLowerCase().contains(q);
        })
        .toList();
    return Row(
      children: [
        Expanded(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: TextField(
                  key: const Key('searchField'),
                  decoration: const InputDecoration(
                    labelText: '検索',
                    prefixIcon: Icon(Icons.search),
                  ),
                  onChanged: (v) => setState(() => _search = v),
                ),
              ),
              Expanded(
                child: InteractiveViewer(
                  key: const Key('diagramViewer'),
                  transformationController: _controller,
                  child: Stack(
                    children: [
                      SvgPicture.string(_svg!),
                      for (final node in nodes)
                        Positioned(
                          key: Key('node-${node['id']}'),
                          left: (node['x'] as num).toDouble() - 20,
                          top: (node['y'] as num).toDouble() - 20,
                          width: 40,
                          height: 40,
                          child: GestureDetector(
                            onTap: () => setState(() => _selected = node),
                            child: Container(
                              decoration: BoxDecoration(
                                color: Colors.transparent,
                                border: _selected?['id'] == node['id']
                                    ? Border.all(
                                        color: Theme.of(
                                          context,
                                        ).colorScheme.secondary,
                                        width: 2,
                                      )
                                    : null,
                              ),
                            ),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        Container(
          width: 200,
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          child: _selected == null
              ? const Center(child: Text('ノードを選択'))
              : Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _selected!['hostname'] as String,
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text('IP: ${_selected!['ip']}'),
                      Text('Vendor: ${_selected!['vendor']}'),
                    ],
                  ),
                ),
        ),
      ],
    );
  }
}
