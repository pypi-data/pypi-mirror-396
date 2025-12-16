from typing import Optional, Literal

from twnet_parser.pretty_print import PrettyPrint

class ChunkFlags(PrettyPrint):
    def __init__(self):
        self.resend = False
        self.vital = False

    def __repr__(self):
        return "<class: '" + str(self.__class__.__name__) + "'>: " + str(self.__dict__)

    def __iter__(self):
        flags = []
        if self.resend:
            flags.append('resend')
        if self.vital:
            flags.append('vital')
        return iter(flags)

# same fields for 0.6 and 0.7
# different bit layout tho
class ChunkHeader(PrettyPrint):
    def __init__(self, version: Literal['0.6', '0.7']) -> None:
        self.version = version
        self.flags: ChunkFlags = ChunkFlags()
        self.size: Optional[int] = None
        # TODO: should seq be a optional?
        #       so it can be None for non vital packages
        #       this could turn downstream users logic errors into
        #       crashes which would be easier to detect
        #
        #       Or is None annoying because it crashes
        #       and pollutes the code with error checking?
        #       Also the teeworlds code uses -1
        #       doing the same for someone who knows the codebase
        #       could also be nice
        #
        #       update: self.size uses optional now
        #               so it can be computed automatically
        #               if unset
        self.seq: int = -1

    def __iter__(self):
        yield 'version', self.version
        yield 'flags', list(self.flags)
        yield 'size', self.size
        yield 'seq', self.seq

    def pack(self) -> bytes:
        flags: int = 0
        if self.flags.resend:
            flags |= 2
        if self.flags.vital:
            flags |= 1
        if self.size is None:
            self.size = 0
        data: bytearray
        if self.version == '0.6':
            data = bytearray([ \
                    ((flags & 0x03) << 6) | \
                    ((self.size >> 4) & 0x3f),
                    self.size & 0xf
            ])
            if self.flags.vital:
                data[1] |= (self.seq >> 2) & 0xf0
                data += bytes([self.seq & 0xff])
        else: # 0.7
            data = bytearray([ \
                    ((flags & 0x03) << 6) | \
                    ((self.size >> 6) & 0x3f),
                    self.size & 0x3f
            ])
            if self.flags.vital:
                data[1] |= (self.seq >> 2) & 0xc0
                data += bytes([self.seq & 0xff])
        return bytes(data)

    def __repr__(self):
        return "<class: '" + str(self.__class__.__name__) + "'>: " + str(dict(self))

