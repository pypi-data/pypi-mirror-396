#!/usr/bin/env python

# pylint: disable=duplicate-code

from typing import Union, cast, Optional, Literal, Iterator, Any
import json

from twnet_parser.packer import pack_int
from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.net_message import NetMessage
from twnet_parser.ctrl_message import CtrlMessage
from twnet_parser.connless_message import ConnlessMessage
from twnet_parser.constants import NET_MAX_SEQUENCE, NET_PACKETVERSION

import twnet_parser.huffman
import twnet_parser.serialize

# TODO: what is a nice pythonic way of storing those?
#       also does some version:: namespace thing make sense?
PACKETFLAG7_CONTROL = 1
PACKETFLAG7_RESEND = 2
PACKETFLAG7_COMPRESSION = 4
PACKETFLAG7_CONNLESS = 8

CHUNKFLAG7_VITAL = 1
CHUNKFLAG7_RESEND = 2

PACKET_HEADER7_SIZE = 7
CONNLESS_PACKET_HEADER7_SIZE = 9
CONNLESS_PACKET_HEADER6_SIZE = 6

class PacketFlags7(PrettyPrint):
    def __init__(self) -> None:
        self.control: Optional[bool] = None
        self.resend: Optional[bool] = None
        self.compression: Optional[bool] = None
        self.connless: Optional[bool] = None

    def __iter__(self):
        flags = []
        if self.control:
            flags.append('control')
        if self.resend:
            flags.append('resend')
        if self.compression:
            flags.append('compression')
        if self.connless:
            flags.append('connless')
        return iter(flags)

    def __repr__(self):
        return "<class: '" + str(self.__class__.__name__) + "'>: " + str(list(self))

class PacketHeader7(PrettyPrint):
    def __init__(
            self,
            flags: Optional[PacketFlags7] = None,
            ack: int = 0,
            token: bytes = b'\xff\xff\xff\xff',
            num_chunks: Optional[int] = None
    ) -> None:
        """
        If num_chunks is not set it will count
        the messages it was given when
        the pack() method is called
        """
        if not flags:
            flags = PacketFlags7()
        self.flags: PacketFlags7 = flags
        self.ack: int = ack % NET_MAX_SEQUENCE
        self.token: bytes = token
        self.num_chunks: Optional[int] = num_chunks

        # connless only
        self.connless_version: int = NET_PACKETVERSION
        self.response_token: bytes = b'\xff\xff\xff\xff'

    def __iter__(self):
        yield 'flags', list(self.flags)
        yield 'ack', self.ack
        yield 'token', self.token
        yield 'num_chunks', self.num_chunks

        if self.flags.connless:
            yield 'connless_version', self.connless_version
            yield 'response_token', self.response_token

    def pack(self) -> bytes:
        """
        Generate 7 byte teeworlds 0.7 packet header
        based on the current instance variable
        values.

        The layout is as follows
        6bit flags, 2bit ack
        8bit ack
        8bit chunks
        32bit token

        ffffffaa
        aaaaaaaa
        NNNNNNNN
        TTTTTTTT
        TTTTTTTT
        TTTTTTTT
        TTTTTTTT
        """
        flags = 0
        if self.flags.control:
            flags |= PACKETFLAG7_CONTROL
        if self.flags.resend:
            flags |= PACKETFLAG7_RESEND
        if self.flags.compression:
            flags |= PACKETFLAG7_COMPRESSION
        if self.flags.connless:
            flags |= PACKETFLAG7_CONNLESS
        if self.num_chunks is None:
            self.num_chunks = 0
        if self.flags.connless:
            return bytes([ \
                ((PACKETFLAG7_CONNLESS<<2)&0xfc) | (self.connless_version&0x03)
            ]) + self.token + self.response_token
        return bytes([ \
            ((flags << 2)&0xfc) | ((self.ack>>8)&0x03), \
            self.ack&0xff, \
            self.num_chunks \
        ]) + self.token

class TwPacket7(PrettyPrint):
    def __init__(self, version: Literal['0.7'] = '0.7') -> None:
        # version is 0.7 at all times for TwPacket7
        self._version: Literal['0.7'] = version

        # There is no packet level ddnet protocol based on 0.7
        # There are still 0.7 snapshot and net message extensions
        # but no custom header/flags or tokens
        self.is_ddnet = False

        # packet payload as raw bytes
        # might be huffman compressed if header.flags.compression is set
        self.payload_raw: bytes = b''

        # packet payload after huffman decompression
        # can match payload_raw if no compression was applied
        self.payload_decompressed: bytes = b''

        # information about the packet
        # metadata that is not contained in the payload
        self.header: PacketHeader7
        if self.version == '0.7':
            self.header = PacketHeader7()
        else:
            raise ValueError(f"Error: invalid packet version '{self.version}'")
        self.messages: list[Union[CtrlMessage, NetMessage, ConnlessMessage]] = []

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield 'version', self.version
        yield 'payload_raw', self.payload_raw
        yield 'payload_decompressed', self.payload_decompressed
        yield 'header', dict(self.header)

        yield 'messages', [dict(msg) for msg in self.messages]

    def to_json(self) -> str:
        return json.dumps(
            dict(self),
            indent=2,
            sort_keys=False,
            default=twnet_parser.serialize.bytes_to_hex
        )

    @property
    def version(self) -> Literal['0.7']:
        return self._version

    def pack(self, we_are_a_client = True) -> bytes:
        payload: bytes = b''
        msg: Union[CtrlMessage, NetMessage, ConnlessMessage]
        is_control: bool = False
        is_connless: bool = False
        for msg in self.messages:
            if msg.message_type == 'connless':
                is_connless = True
                msg = cast(ConnlessMessage, msg)
                payload += bytes(msg.message_id)
                payload += msg.pack()
            elif msg.message_type == 'control':
                is_control = True
                msg = cast(CtrlMessage, msg)
                payload += pack_int(msg.message_id)
                payload += msg.pack(we_are_a_client)
            else: # game or system message
                msg = cast(NetMessage, msg)
                msg_payload: bytes = pack_int(
                    (msg.message_id<<1) |
                    (int)(msg.system_message)
                )
                msg_payload += msg.pack()
                if msg.header.size is None:
                    msg.header.size = len(msg_payload)
                payload += msg.header.pack()
                payload += msg_payload
        if self.header.num_chunks is None:
            if is_control:
                self.header.num_chunks = 0
            else:
                self.header.num_chunks = len(self.messages)
        if is_control:
            if self.header.flags.control is None:
                self.header.flags.control = True
        if is_connless:
            if self.header.flags.connless is None:
                self.header.flags.connless = True
        if self.header.flags.compression:
            payload = twnet_parser.huffman.compress(payload)
        return self.header.pack() + payload

class PacketHeaderParser7():
    def parse_flags7(self, data: bytes) -> PacketFlags7:
        # FFFF FFaa
        flag_bits = (data[0] & 0xfc) >> 2
        flags = PacketFlags7()
        flags.control = (flag_bits & PACKETFLAG7_CONTROL) != 0
        flags.resend = (flag_bits & PACKETFLAG7_RESEND) != 0
        flags.compression = (flag_bits & PACKETFLAG7_COMPRESSION) != 0
        flags.connless = (flag_bits & PACKETFLAG7_CONNLESS) != 0
        return flags

    def parse_ack(self, header_bytes: bytes) -> int:
        # ffAA AAAA AAAA
        return ((header_bytes[0] & 0x3) << 8) | header_bytes[1]

    def parse_num_chunks(self, header_bytes: bytes) -> int:
        # TODO: not sure if this is correct
        return header_bytes[2]

    def parse_token(self, header_bytes: bytes) -> bytes:
        return header_bytes[3:7]

    def parse_header(self, data: bytes) -> PacketHeader7:
        header = PacketHeader7()
        # bits 2..5
        header.flags = self.parse_flags7(data)
        if header.flags.connless:
            # TODO: do not hardcode version field
            #       but actually read the bits
            header.connless_version = NET_PACKETVERSION
            header.token = data[1:5]
            header.response_token = data[5:9]
        else:
            # bits 6..16
            header.ack = self.parse_ack(data)
            # bits 17..25
            header.num_chunks = self.parse_num_chunks(data)
            # bits 16..57
            header.token = self.parse_token(data)
        return header

