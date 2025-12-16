#!/usr/bin/env python

from typing import Union, cast, Literal

from twnet_parser.error import ParserError
from twnet_parser.packer import Unpacker
from twnet_parser.message_parser import MessageParser
from twnet_parser.net_message import NetMessage
from twnet_parser.ctrl_message import CtrlMessage
from twnet_parser.connless_message import ConnlessMessage
from twnet_parser.chunk_header import ChunkHeader, ChunkFlags
from twnet_parser.msg_matcher.control7 import match_control7
from twnet_parser.msg_matcher.connless7 import match_connless7
from twnet_parser.msg_matcher.control6 import match_control6
from twnet_parser.msg_matcher.connless6 import match_connless6

import twnet_parser.huffman
from twnet_parser.packet6 import CONNLESS_PACKET_HEADER6_SIZE, TwPacket6, PacketHeaderParser6
from twnet_parser.packet7 import CONNLESS_PACKET_HEADER7_SIZE
from twnet_parser.packet7 import CHUNKFLAG7_RESEND, CHUNKFLAG7_VITAL, PACKET_HEADER7_SIZE
from twnet_parser.packet7 import PacketHeaderParser7, TwPacket7
import twnet_parser.serialize

class ChunkHeaderParser:
    def parse_flags7(self, data: bytes) -> ChunkFlags:
        # FFss ssss  xxss ssss
        flag_bits = (data[0] >> 6) & 0x03
        flags = ChunkFlags()
        flags.resend = (flag_bits & CHUNKFLAG7_RESEND) != 0
        flags.vital = (flag_bits & CHUNKFLAG7_VITAL) != 0
        return flags

    # the first byte of data has to be the
    # first byte of the chunk header
    def parse_header7(self, data: bytes) -> ChunkHeader:
        header = ChunkHeader(version = '0.7')
        header.flags = self.parse_flags7(data)
        # ffSS SSSS  xxSS SSSS
        header.size = ((data[0] & 0x3F) << 6) | (data[1] & 0x3F)
        if header.flags.vital:
            # ffss ssss  XXss ssss
            header.seq = ((data[1] & 0xC0) << 2) | data[2]
        return header

    # the first byte of data has to be the
    # first byte of the chunk header
    def parse_header6(self, data: bytes) -> ChunkHeader:
        header = ChunkHeader(version = '0.6')
        header.flags = self.parse_flags7(data)
        header.size = ((data[0] & 0x3F) << 4) | (data[1] & 0xF)
        if header.flags.vital:
            header.seq = ((data[1] & 0xF0) << 2) | data[2]
        return header

class PacketParser():
    def __init__(self, ignore_errors = False) -> None:
        self.version: Literal['0.6', '0.6.4', '0.6.5', '0.7'] = '0.7'
        # by default we throw on unexpected values
        self.ignore_errors = ignore_errors

    # the first byte of data has to be the
    # first byte of a message chunk
    # NOT the whole packet with packet header
    def get_messages(self, data: bytes, packet: Union[TwPacket6, TwPacket7]) -> list[NetMessage]:
        messages: list[NetMessage] = []
        i = 0
        while i < len(data) and len(messages) < (packet.header.num_chunks or 0):
            msg = self.get_message(data[i:])
            if msg.header.size is None:
                raise ValueError('header size is not set')
            i += msg.header.size + 2 # header + msg id = 3
            if msg.header.flags.vital:
                i += 1
            messages.append(msg)
        if i < len(data):
            num_bytes: int = len(data) - i
            if num_bytes == 4 and packet.version.startswith('0.6'):
                # if there are exactly 4 bytes left over at the end
                # of the message we assume it is the ddnet TKEN extension
                packet.is_ddnet = True
                packet.header.token = data[i:]
            elif not self.ignore_errors:
                raise ParserError(
                    f"Got {len(messages)}/{packet.header.num_chunks} messages " +
                    f"but there are still {num_bytes} bytes remaining"
                )
        return messages

    # the first byte of data has to be the
    # first byte of a message chunk
    # NOT the whole packet with packet header
    def get_message(self, data: bytes) -> NetMessage:
        if self.version == '0.6':
            chunk_header = ChunkHeaderParser().parse_header6(data)
        else:
            chunk_header = ChunkHeaderParser().parse_header7(data)
        i = 2
        if chunk_header.flags.vital:
            i += 1
        unpacker = Unpacker(data[i:])
        msg_id: int = unpacker.get_int()
        i += 1
        sys: bool = (msg_id & 1) == 1
        msg_id >>= 1
        msg: NetMessage
        if sys:
            msg = MessageParser().parse_sys_message(self.version, msg_id, unpacker.get_raw())
        else:
            msg = MessageParser().parse_game_message(self.version, msg_id, unpacker.get_raw())
        msg.header = chunk_header
        return msg

    def parse6(self, data: bytes, client: bool) -> TwPacket6:
        pck = TwPacket6(version = '0.6')
        # can be overwritten with 0.6.4 or 0.6.5 if we detect something specific
        self.version = '0.6'
        # TODO: what is the most performant way in python to do this?
        #       heap allocating a PacketHeaderParser7 just to bundle a bunch of
        #       methods that do not share state seems like a waste of performance
        #       would this be nicer with class methods?
        pck.header = PacketHeaderParser6().parse_header(data)
        # TODO: this is wrong!
        #       0.6.4 headers are 3 bytes
        #       and in 0.6.5 only if the token flag is set they are 7 bytes
        header_size = PACKET_HEADER7_SIZE
        if pck.header.flags.connless:
            header_size = CONNLESS_PACKET_HEADER6_SIZE
        elif not pck.header.flags.token:
            header_size = 3
        pck.payload_raw = data[header_size:]
        pck.payload_decompressed = pck.payload_raw
        if pck.header.flags.control:
            unpacker = Unpacker(data[header_size+1:])
            ctrl_msg: CtrlMessage = match_control6(data[header_size], unpacker, pck, client)
            pck.messages.append(ctrl_msg)
            if unpacker.remaining_size() == 4:
                # if there are exactly 4 bytes left over at the end
                # of the packet we assume it is the ddnet TKEN extension
                pck.is_ddnet = True
                pck.header.token = unpacker.get_raw(4)
                pck.set_version('0.6.4') # ddnet is always 0.6.4
            elif not self.ignore_errors and unpacker.remaining_size() > 0:
                raise ParserError(
                    f"Got control message with {unpacker.remaining_size()} "
                     "unexpected bytes at the end"
                )
            return pck
        if pck.header.flags.connless:
            connless_msg: ConnlessMessage = match_connless6(data[header_size:14], data[14:])
            pck.messages.append(connless_msg)
            return pck
        if pck.header.flags.compression:
            payload = pck.payload_raw
            pck.payload_decompressed = twnet_parser.huffman.decompress(payload)
        pck.messages = cast(
                list[Union[CtrlMessage, NetMessage, ConnlessMessage]],
                self.get_messages(pck.payload_decompressed, pck))
        return pck

    def parse7(self, data: bytes, client: bool) -> TwPacket7:
        pck = TwPacket7(version = '0.7')
        self.version = '0.7'
        # TODO: what is the most performant way in python to do this?
        #       heap allocating a PacketHeaderParser7 just to bundle a bunch of
        #       methods that do not share state seems like a waste of performance
        #       would this be nicer with class methods?
        pck.header = PacketHeaderParser7().parse_header(data)
        header_size = PACKET_HEADER7_SIZE
        if pck.header.flags.connless:
            header_size = CONNLESS_PACKET_HEADER7_SIZE
        pck.payload_raw = data[header_size:]
        pck.payload_decompressed = pck.payload_raw
        if pck.header.flags.control:
            ctrl_msg: CtrlMessage = match_control7(data[header_size], data[8:], client)
            pck.messages.append(ctrl_msg)
            return pck
        if pck.header.flags.connless:
            connless_msg: ConnlessMessage = match_connless7(data[header_size:17], data[17:])
            pck.messages.append(connless_msg)
            return pck
        if pck.header.flags.compression:
            payload = pck.payload_raw
            pck.payload_decompressed = twnet_parser.huffman.decompress(payload)
        pck.messages = cast(
                list[Union[CtrlMessage, NetMessage, ConnlessMessage]],
                self.get_messages(pck.payload_decompressed, pck))
        return pck

def parse6(data: bytes, ignore_errors: bool = False, we_are_a_client: bool = True) -> TwPacket6:
    return PacketParser(ignore_errors).parse6(data, we_are_a_client)

def parse7(data: bytes, ignore_errors: bool = False, we_are_a_client: bool = True) -> TwPacket7:
    return PacketParser(ignore_errors).parse7(data, we_are_a_client)
