#!/usr/bin/env python3

import socket
import os
import sys
import hashlib
from typing import Optional

from twnet_parser.packet import TwPacket, parse7
from twnet_parser.messages7.control.token import CtrlToken
from twnet_parser.messages7.control.connect import CtrlConnect
from twnet_parser.messages7.control.close import CtrlClose
from twnet_parser.messages7.system.info import MsgInfo
from twnet_parser.messages7.system.map_change import MsgMapChange
from twnet_parser.messages7.system.request_map_data import MsgRequestMapData

from twnet_parser.constants import NET_MAX_PACKETSIZE, NET_MAX_SEQUENCE

def progress(have, want):
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')
    percent = int(100 * have / want)
    bar = '=' * int(percent / 2)
    bar = bar[0:-1] + '>'
    print(f"[{bar:50}] {have}/{want} {percent}%")
    print(outfile)

if len(sys.argv) < 3:
    print("usage: download.py HOST PORT")
    print("description:")
    print("  connects to given server and downloads the map")
    print("  the file will be stored in the current working directory")
    print("  then the client disconnects and quits the program")
    print("example:")
    print("  download.py localhost 8303")
    exit(1)

host = sys.argv[1]
port = int(sys.argv[2])
dest_srv = (host, port)

print(f"Connecting to {host}:{port} ...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 0))

outfile = None
downloaded_chunks = 0
downloaded_bytes = 0
sent_vital = 0
got_vital = 0
got_seqs = set()
map_info: Optional[MsgMapChange] = None
my_token = b'\xff\xaa\xbb\xee'
srv_token = b'\xff\xff\xff\xff'

def send_msg(messages):
    global srv_token
    global got_vital
    global sent_vital
    if not isinstance(messages, list):
        messages = [messages]
    packet = TwPacket()
    packet.header.token = srv_token
    for msg in messages:
        if hasattr(msg, 'header'):
            if msg.header.flags.vital:
                sent_vital += 1
            msg.header.seq = sent_vital
        packet.messages.append(msg)
    packet.header.ack = got_vital
    sock.sendto(packet.pack(), dest_srv)

# TODO: we should be able to set this
# ctrl_token = CtrlToken(we_are_a_client = True)
ctrl_token = CtrlToken()
ctrl_token.response_token = my_token
send_msg(ctrl_token)

def verify_checksum(filename, sha256):
    with open(filename, "rb") as f:
        bytes = f.read()
        readable_hash = hashlib.sha256(bytes).hexdigest()
        if readable_hash == sha256:
            print("OK checksum matches.")
            return
        else:
            print(f"ERROR expected={sha256} got={readable_hash}")
    exit(1)

while True:
    data, addr = sock.recvfrom(NET_MAX_PACKETSIZE)
    packet = parse7(data)

    for msg in packet.messages:
        if hasattr(msg, 'header'):
            if msg.header.flags.vital and not msg.header.flags.resend:
                got_vital = (got_vital + 1) % NET_MAX_SEQUENCE
            if msg.header.seq in got_seqs:
                continue
            got_seqs.add(msg.header.seq)

        if msg.message_name == 'token':
            srv_token = msg.response_token

            ctrl_connect = CtrlConnect()
            ctrl_connect.response_token = my_token
            send_msg(ctrl_connect)
        elif msg.message_name == 'accept':
            info = MsgInfo()
            info.header.flags.vital = True
            send_msg(info)
        elif msg.message_name == 'map_change':
            map_info = msg
            outfile = f"{map_info.name}_{map_info.sha256.hex()}.map"
            if os.path.isfile(outfile):
                print(f"Error: file already exists '{outfile}'")
                exit(1)
            req = MsgRequestMapData()
            req.header.flags.vital = True
            send_msg(req)
        elif msg.message_name == 'map_data':
            if not outfile:
                continue
            downloaded_chunks += 1
            downloaded_bytes += msg.header.size
            with open(outfile, "ab") as map_file:
                map_file.write(msg.data)
            progress(downloaded_bytes, map_info.size)
            if downloaded_bytes >= map_info.size:
                print(f"finished downloading {map_info.name}")
                verify_checksum(outfile, map_info.sha256.hex())
                send_msg(CtrlClose())
                exit(0)
            if downloaded_chunks % map_info.num_response_chunks_per_request == 0:
                req = MsgRequestMapData()
                req.header.flags.vital = True
                send_msg(req)
        elif msg.message_name == 'close':
            print("disconnected")
            exit(1)
