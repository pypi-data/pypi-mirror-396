#!/usr/bin/env python3

import sys

import dpkt
import twnet_parser.packet

arg_pcap = None
arg_version = 7

def print_tw_packets(pcap):
    for _ts, buf in pcap:
        eth = dpkt.ethernet.Ethernet(buf)
        ip = eth.data
        if not isinstance(ip.data, dpkt.udp.UDP):
            continue
        udp_payload = ip.data.data
        try:
            if arg_version == 6:
                packet = twnet_parser.packet.parse6(udp_payload)
            else:
                packet = twnet_parser.packet.parse7(udp_payload)
        except:
            continue
        names = [msg.message_name for msg in packet.messages]
        print(f"[TW{arg_version}] {', '.join(names)}")

def usage():
    print(f'usage: {sys.argv[0]} <pcap file> [-6|-7]')
    print('options:')
    print(' -6  try to parse as teeworlds 0.6 packets')
    print(' -7  try to parse as teeworlds 0.7 packets (default)')

if len(sys.argv) < 2:
    usage()
    exit(1)

for arg in sys.argv[1:]:
    if arg == '-6':
        arg_version = 6
    elif arg == '-7':
        arg_version = 7
    elif arg_pcap is None:
        arg_pcap = arg

if arg_pcap is None:
    usage()
    exit(1)

with open(arg_pcap, 'rb') as f:
    pcap = dpkt.pcap.Reader(f)
    print_tw_packets(pcap)
