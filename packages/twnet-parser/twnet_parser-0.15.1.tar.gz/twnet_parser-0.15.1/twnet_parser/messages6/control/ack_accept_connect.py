from typing import Literal
from twnet_parser.pretty_print import PrettyPrint
from twnet_parser.packer import Unpacker

import twnet_parser.msg6

"""
Sent by the client to ack the connect accept message CtrlAcceptConnect

Control message id 3 is only valid in 0.6.4 and earlier
got removed in 0.6.5
"""
class CtrlAckAcceptConnect(PrettyPrint):
    def __init__(self) -> None:
        self.message_type: Literal['control'] = 'control'
        self.message_name: str = 'ack_accept_connect'
        self.message_id: int = twnet_parser.msg6.CTRL_ACCEPT

    def __iter__(self):
        yield 'message_type', self.message_type
        yield 'message_name', self.message_name
        yield 'message_id', self.message_id

    def unpack(self, unpacker: Unpacker, we_are_a_client: bool = True) -> bool:
        return False

    def pack(self, we_are_a_client: bool = True) -> bytes:
        return b''
