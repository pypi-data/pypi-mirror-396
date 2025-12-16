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

PACKETFLAG6_UNUSED = 1
PACKETFLAG6_TOKEN = 2
PACKETFLAG6_CONTROL = 4
PACKETFLAG6_CONNLESS = 8
PACKETFLAG6_RESEND = 16
PACKETFLAG6_COMPRESSION = 32

# not sure if this is correct
# i get big 3 byte vibes from 0.6
# and then there is the 0.6.5 token extension
CONNLESS_PACKET_HEADER6_SIZE = 6

class PacketFlags6(PrettyPrint):
    def __init__(self) -> None:
        self.token: Optional[bool] = None
        self.control: Optional[bool] = None
        self.resend: Optional[bool] = None
        self.compression: Optional[bool] = None
        self.connless: Optional[bool] = None

    def __iter__(self):
        flags = []
        if self.token:
            flags.append('token')
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

class PacketHeader6(PrettyPrint):
    def __init__(
            self,
            flags: Optional[PacketFlags6] = None,
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
            flags = PacketFlags6()
        self.flags: PacketFlags6 = flags
        self.ack: int = ack % NET_MAX_SEQUENCE

        # the token has to be 4 bytes at all times
        # ff ff ff ff represents the empty token
        # if the packet is a 0.6.5 packet the token will be part of the header
        # if the packet is a 0.6.4 ddnet packet the token will be appended at the
        # end of the packet after the payload
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

    def pack(self, include_token: bool = True) -> bytes:
        """
        Generate 7 byte teeworlds 0.6.5 packet header
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
        if self.flags.token is None:
            # do not automatically set the token flag
            # if the token field has the empty token value
            if self.token != b'\xff\xff\xff\xff':
                self.flags.token = True
        if self.flags.token and include_token:
            flags |= PACKETFLAG6_TOKEN
        if self.flags.control:
            flags |= PACKETFLAG6_CONTROL
        if self.flags.connless:
            flags |= PACKETFLAG6_CONNLESS
        if self.flags.resend:
            flags |= PACKETFLAG6_RESEND
        if self.flags.compression:
            flags |= PACKETFLAG6_COMPRESSION
        if self.num_chunks is None:
            self.num_chunks = 0
        if self.flags.connless:
            return b'\xff\xff\xff\xff\xff\xff'
        packed = bytes([ \
            ((flags << 2)&0xfc) | ((self.ack>>8)&0x03), \
            self.ack&0xff, \
            self.num_chunks \
        ])
        if self.flags.token and include_token:
            packed += self.token
        return packed

class TwPacket6(PrettyPrint):
    def __init__(self, is_ddnet: bool = False, version: Literal['0.6']= '0.6') -> None:
        # teeworlds protocol version
        # can be set to a more specific version than 0.6 using set_version()
        self._version: Literal['0.6', '0.6.4', '0.6.5'] = version

        # does this packet use the 0.6.4 + TKEN extension protocol
        # if true the last 4 bytes of the packet are the ddnet security token
        self.is_ddnet = is_ddnet

        # packet payload as raw bytes
        # might be huffman compressed if header.flags.compression is set
        self.payload_raw: bytes = b''

        # packet payload after huffman decompression
        # can match payload_raw if no compression was applied
        self.payload_decompressed: bytes = b''

        # information about the packet
        # metadata that is not contained in the payload
        self.header = PacketHeader6()

        # packet payload parsed as message array
        self.messages: list[Union[CtrlMessage, NetMessage, ConnlessMessage]] = []

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        yield 'version', self.version
        yield 'is_ddnet', self.is_ddnet
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
    def version(self) -> Literal['0.6', '0.6.4', '0.6.5']:
        has_token = self.header.token != b'\xff\xff\xff\xff' or self.header.flags.token
        if self.is_ddnet:
            self._version = '0.6.4'
        elif has_token:
            self._version = '0.6.5'
        return self._version

    def set_version(self, version: Literal['0.6', '0.6.4', '0.6.5']) -> str:
        self._version = version
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
        if self.is_ddnet:
            return self.header.pack(include_token=False) + payload + self.header.token
        return self.header.pack() + payload

class PacketHeaderParser6():
    def parse_flags6(self, data: bytes) -> PacketFlags6:
        # FFFF FFaa
        flag_bits = data[0] >> 2
        flags = PacketFlags6()
        flags.token = (flag_bits & PACKETFLAG6_TOKEN) != 0
        flags.control = (flag_bits & PACKETFLAG6_CONTROL) != 0
        flags.connless = (flag_bits & PACKETFLAG6_CONNLESS) != 0
        flags.resend = (flag_bits & PACKETFLAG6_RESEND) != 0
        flags.compression = (flag_bits & PACKETFLAG6_COMPRESSION) != 0
        if flags.connless:
            # connless packets send FF
            # as the flag byte
            # but setting the connless bit basically means
            # all other flags are false implicitly
            flags.token = False
            flags.control = False
            flags.resend = False
            flags.compression = False
        return flags

    def parse_ack(self, header_bytes: bytes) -> int:
        # ffAA AAAA AAAA
        return ((header_bytes[0] & 0x3) << 8) | header_bytes[1]

    def parse_num_chunks(self, header_bytes: bytes) -> int:
        # TODO: not sure if this is correct
        return header_bytes[2]

    def parse_token(self, header_bytes: bytes) -> bytes:
        return header_bytes[3:7]

    def parse_header(self, data: bytes) -> PacketHeader6:
        header = PacketHeader6()
        # bits 1..5
        header.flags = self.parse_flags6(data)
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
            if header.flags.token:
                header.token = self.parse_token(data)
            else:
                header.token = b''
        return header

