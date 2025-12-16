#!/usr/bin/env python3

import socket
import time
import random
import argparse
from signal import signal, SIGINT
from typing import Optional, cast

from twnet_parser.net_message import NetMessage
from twnet_parser.packet import TwPacket7, parse7
from twnet_parser.messages7.control.token import CtrlToken
from twnet_parser.messages7.control.connect import CtrlConnect
from twnet_parser.messages7.control.close import CtrlClose
from twnet_parser.messages7.control.keep_alive import CtrlKeepAlive
from twnet_parser.messages7.system.info import MsgInfo
from twnet_parser.messages7.system.input import MsgInput
from twnet_parser.messages7.system.map_change import MsgMapChange
from twnet_parser.messages7.system.ready import MsgReady
from twnet_parser.messages7.game.cl_start_info import MsgClStartInfo
from twnet_parser.messages7.system.enter_game import MsgEnterGame
# from twnet_parser.messages7.game.cl_kill import MsgClKill

from twnet_parser.constants import NET_MAX_PACKETSIZE, NET_MAX_SEQUENCE

example_text = '''example:
 python %(prog)s localhost 8303 2
 python %(prog)s localhost 8303 10 --no-random-inputs
 python %(prog)s localhost 8303'''

description_text = '''
 Connects to given server. And keeps the connection alive.
'''

parser = argparse.ArgumentParser(
    prog='flood.py',
    description=description_text,
    epilog=example_text,
    formatter_class=argparse.RawDescriptionHelpFormatter
)
parser.add_argument("host")
parser.add_argument("port", type=int)
parser.add_argument("num_clients", type=int, default=1, nargs="?")
parser.add_argument('--random-inputs', action=argparse.BooleanOptionalAction, default=True)
parser.add_argument('--random-reconnects', default=False, action='store_true')
args = parser.parse_args()

class TeeworldsClient():
    def __init__(self, name, host, port):
        self.sock = None
        self.name = name
        self.connected = False
        self.connect(host, port)

    def connect(self, host, port):
        self.connected = False
        self.host = host
        self.port = port
        self.dest_srv = (self.host, self.port)

        self.log(f"Connecting to {host}:{port} ...")

        if self.sock:
            self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', 0))

        self.outfile = None
        self.downloaded_chunks = 0
        self.downloaded_bytes = 0
        self.sent_vital = 0
        self.got_vital = 0
        self.got_seqs = set()
        self.map_info: Optional[MsgMapChange] = None
        self.my_token = b'\xff\xaa\xbb\xee'
        self.srv_token = b'\xff\xff\xff\xff'
        self.last_send_time = time.time()

        # TODO: we should be able to set this
        # ctrl_token = CtrlToken(we_are_a_client = True)
        ctrl_token = CtrlToken()
        ctrl_token.response_token = self.my_token
        self.send_msg(ctrl_token)

    def disconnect(self):
        close = CtrlClose()
        self.log("sending disconnect")
        self.send_msg(close)

    def log(self, message):
        print(f"[{self.name}] {message}")

    def send_msg(self, messages):
        if self.sock is None:
            self.log("failed to send message! No socket!")
            return

        if not isinstance(messages, list):
            messages = [messages]
        packet = TwPacket7()
        packet.header.token = self.srv_token
        for msg in messages:
            if hasattr(msg, 'header'):
                if msg.header.flags.vital:
                    self.sent_vital += 1
                msg.header.seq = self.sent_vital
            packet.messages.append(msg)
        self.last_send_time = time.time()
        packet.header.ack = self.got_vital
        self.sock.sendto(packet.pack(), self.dest_srv)

    def send_random_inputs(self):
        input = MsgInput()
        input.ack_snapshot = 0
        input.intended_tick = 0
        input.input_size = 40
        input.input.direction = random.randint(-1, 1)
        input.input.fire = random.randint(0, 100)
        input.input.hook = random.randint(0, 1) == 0
        input.input.jump = random.randint(0, 1) == 0
        input.input.target_x = random.randint(-200, 200)
        input.input.target_y = random.randint(-200, 200)
        self.send_msg(input)

    def tick(self):
        data, addr = self.sock.recvfrom(NET_MAX_PACKETSIZE)
        packet = parse7(data)

        for msg in packet.messages:
            # self.log(f"got msg {msg.message_id}")
            if hasattr(msg, 'header'):
                msg = cast(NetMessage, msg)
                if msg.header.flags.vital and not msg.header.flags.resend:
                    self.got_vital = (self.got_vital + 1) % NET_MAX_SEQUENCE
                if msg.header.seq in self.got_seqs:
                    continue
                self.got_seqs.add(msg.header.seq)

            if msg.message_name == 'token':
                msg = cast(CtrlToken, msg)
                self.srv_token = msg.response_token

                ctrl_connect = CtrlConnect()
                ctrl_connect.response_token = self.my_token
                self.send_msg(ctrl_connect)
            elif msg.message_name == 'accept':
                info = MsgInfo()
                info.header.flags.vital = True
                self.send_msg(info)
            elif msg.message_name == 'map_change' or msg.message_name == 'map_data':
                ready = MsgReady()
                ready.header.flags.vital = True
                self.send_msg(ready)
            elif msg.message_name == 'con_ready':
                self.log("sending info")
                startinfo = MsgClStartInfo()
                startinfo.header.flags.vital = True
                self.send_msg(startinfo)
                enter_game = MsgEnterGame()
                enter_game.header.flags.vital = True
                self.send_msg(enter_game)
            elif msg.message_name == 'close':
                msg = cast(CtrlClose, msg)
                self.log(f"disconnected reason='{msg.reason}'")
                exit(1)
            elif msg.message_name.startswith('snap_'):
                self.connected = True
                self.log("connected!")

        if args.random_reconnects and self.connected and random.randint(0, 100) > 90:
            self.disconnect()
            self.connect(self.host, self.port)

        if (time.time() - self.last_send_time) > 1:
            if args.random_inputs:
                self.send_random_inputs()
            else:
                self.send_msg(CtrlKeepAlive())
            # kill = MsgClKill()
            # kill.header.flags.vital = True
            # self.send_msg(kill)

clients = []

for i in range(0, args.num_clients):
    client = TeeworldsClient(name = i, host = args.host, port = args.port)
    clients.append(client)

def handler(signal_received, frame):
    global clients
    print('SIGINT or CTRL-C detected. Exiting gracefully')
    for client in clients:
        client.disconnect()
    exit(0)

signal(SIGINT, handler)

while True:
    for client in clients:
        client.tick()

