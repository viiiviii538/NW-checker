from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, TCP

from src.dynamic_scan import parser

def test_parse_packet_tcp_fields():
    pkt = (
        Ether(src="aa:aa:aa:aa:aa:aa", dst="bb:bb:bb:bb:bb:bb")
        / IP(src="1.1.1.1", dst="2.2.2.2")
        / TCP()
    )
    pkt.time = 123.456
    parsed = parser.parse_packet(pkt)
    assert parsed.src_mac == "aa:aa:aa:aa:aa:aa"
    assert parsed.dst_mac == "bb:bb:bb:bb:bb:bb"
    assert parsed.src_ip == "1.1.1.1"
    assert parsed.dst_ip == "2.2.2.2"
    assert parsed.protocol == "tcp"
    assert parsed.size == len(pkt)
    assert parsed.timestamp == 123.456

def test_parse_packet_unknown_protocol():
    pkt = IP(src="3.3.3.3", dst="4.4.4.4", proto=1)  # ICMP
    pkt.time = 1.0
    parsed = parser.parse_packet(pkt)
    assert parsed.src_mac is None
    assert parsed.protocol == "1"
    assert parsed.src_ip == "3.3.3.3"
    assert parsed.dst_ip == "4.4.4.4"

def test_parse_packet_none_returns_empty():
    parsed = parser.parse_packet(None)
    assert vars(parsed) == {}
