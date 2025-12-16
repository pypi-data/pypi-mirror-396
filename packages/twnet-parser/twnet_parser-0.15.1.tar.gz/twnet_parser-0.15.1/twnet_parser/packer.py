#!/usr/bin/env python

from typing import Final, Literal, Optional

from twnet_parser.master_server import MastersrvAddr

# Before chaning the current packer code to extend it
# Consider having two packers
#
# One being this one. That is simple and fast.
# Has no state or side effects.
# Does no error checking.
#
# And another one that sanitizes the data
# will throw errors unexpected data
# return the amount of read and written bytes
# and is attached to a class instance that
# keeps track of a state

NO_SANITIZE: Final[int] = 0
SANITIZE: Final[int]  = 1
SANITIZE_CC: Final[int] = 2
SKIP_START_WHITESPACES: Final[int] = 3

class Unpacker():
    def __init__(self, data: bytes) -> None:
        self._data = data
        self.idx = 0

    # first byte of the current buffer
    def byte(self) -> int:
        return self._data[self.idx]

    def data(self) -> bytes:
        return self._data[self.idx:]

    def remaining_size(self) -> int:
        return len(self._data) - self.idx

    def get_raw(self, size: int = -1) -> bytes:
        if size == -1:
            return self.data()
        end: int = self.idx + size
        data: bytes = self._data[self.idx:end]
        self.idx = end
        return data

    def get_packed_addresses(self) -> list[MastersrvAddr]:
        servers: list[MastersrvAddr] = []
        while len(self.data()) >= 18:
            ipaddr = self.get_raw(16)
            ipv4_mapping = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF'
            family: Literal[4, 6] = 4
            addr_str: str = ''
            if ipaddr[0:12] == ipv4_mapping:
                addr_str = f"{ipaddr[12]}.{ipaddr[13]}.{ipaddr[14]}.{ipaddr[15]}"
            else:
                # TODO: make ipv6 nicer
                addr_str = str(ipaddr)
                family = 6
            port = self.get_be_uint16() # TODO: i randomly assumed this would work
            servers.append(MastersrvAddr(family, addr_str, int(port)))
        return servers

    def get_uint8(self) -> int:
        res = self.byte()
        self.idx += 1
        return res

    def get_be_uint16(self) -> int:
        left = self.byte()
        self.idx += 1
        right = self.byte()
        self.idx += 1
        return left << 8 | right

    def get_optional_int(self) -> Optional[int]:
        if self.idx >= len(self._data):
            return None
        return self.get_int()

    def get_int(self) -> int:
        sign = (self.byte() >> 6) & 1
        res = self.byte() & 0x3F
        # fake loop should only loop once
        # its the poor mans goto hack
        while True:
            if (self.byte() & 0x80) == 0:
                break
            self.idx += 1
            res |= (self.byte() & 0x7F) << 6

            if (self.byte() & 0x80) == 0:
                break
            self.idx += 1
            res |= (self.byte() & 0x7F) << (6 + 7)

            if (self.byte() & 0x80) == 0:
                break
            self.idx += 1
            res |= (self.byte() & 0x7F) << (6 + 7 + 7)

            if (self.byte() & 0x80) == 0:
                break
            self.idx += 1
            res |= (self.byte() & 0x7F) << (6 + 7 + 7 + 7)
            break

        self.idx += 1
        res ^= -sign
        return res

    def get_optional_str(self, sanitize: int = SANITIZE) -> Optional[str]:
        if self.idx >= len(self._data):
            return None
        return self.get_str(sanitize)

    # TODO: optimize performance
    #       I am highly confident iterating byte by byte is very
    #       expensive in python
    #       and something common as byte filtering has to have
    #       a fast alternative
    #
    #       If there is nothing from the python standard
    #       this might be worth writing in Cython
    #       external C or rust
    # TODO: make literals work currently passing in SANITIZE as arg
    #       to unpacker.get_str() does not work because its not a literal ._.
    # def get_str(self, sanitize: Literal[0,1,2,3] = 1) -> str:
    def get_str(self, sanitize: int = SANITIZE) -> str:
        str_end: int = self.data().find(b'\x00')
        res: bytes = self.data()[:str_end]
        self.idx += str_end + 1
        if sanitize == NO_SANITIZE:
            return res.decode('utf-8', 'ignore')
        if sanitize == SANITIZE:
            return bytes( \
                [x if x > 32 or x in (9, 10, 13) else 32 for x in res]) \
                .decode('utf-8', 'ignore' \
            )
        if sanitize == SANITIZE_CC:
            return bytes( \
                [x if x > 32 else 32 for x in res]) \
                .decode('utf-8', 'ignore' \
            )
        if sanitize == SKIP_START_WHITESPACES:
            return res.decode('utf-8').lstrip()
        raise ValueError(f"Error: invalid sanitize mode {sanitize}")

# TODO: optimize performance and benchmark in tests
def pack_int(num: int) -> bytes:
    res: bytearray = bytearray(b'\x00')
    if num < 0:
        res[0] |= 0x40 # set sign bit
        num = ~num

    res[0] |= num & 0x3F # pack 6bit into res
    num >>= 6 # discard 6 bits

    i = 0
    while num != 0:
        res[i] |= 0x80 # set extend bit
        i += 1
        res.extend(bytes([num & 0x7F])) # pack 7 bit
        num >>= 7 # discard 7 bits
    return bytes(res)

def pack_be_uint16(num: int) -> bytes:
    high = (num >> 8) & 0xff
    low = num & 0xff
    return bytes([high, low])

def pack_uint8(num: int) -> bytes:
    return bytes([num])

def pack_packed_addresses(servers: list[MastersrvAddr]) -> bytes:
    res: bytes = b''
    for server in servers:
        if server.family == 4:
            ipv4_mapping = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF'
            res += ipv4_mapping
            res += bytes([int(x) for x in server.ipaddr.split('.')])
        else:
            # TODO: ipv6 is wrong
            res += server.ipaddr.encode('utf-8')
        res += pack_be_uint16(server.port)
    return res

def pack_str(data: str) -> bytes:
    return data.encode('utf-8') + b'\x00'

# TODO: optimize performance and benchmark in tests
def unpack_int(data: bytes) -> int:
    sign = (data[0] >> 6) & 1
    res = data[0] & 0x3F
    i = 0
    # fake loop should only loop once
    # its the poor mans goto hack
    while True:
        if (data[i] & 0x80) == 0:
            break
        i += 1
        res |= (data[i] & 0x7F) << 6

        if (data[i] & 0x80) == 0:
            break
        i += 1
        res |= (data[i] & 0x7F) << (6 + 7)

        if (data[i] & 0x80) == 0:
            break
        i += 1
        res |= (data[i] & 0x7F) << (6 + 7 + 7)

        if (data[i] & 0x80) == 0:
            break
        i += 1
        res |= (data[i] & 0x7F) << (6 + 7 + 7 + 7)
        break

    res ^= -sign
    return res
