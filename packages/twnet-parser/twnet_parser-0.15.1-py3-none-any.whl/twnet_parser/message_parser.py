from typing import Literal

from twnet_parser.net_message import NetMessage

from twnet_parser.msg_matcher.game7 import match_game7
from twnet_parser.msg_matcher.system7 import match_system7

from twnet_parser.msg_matcher.game6 import match_game6
from twnet_parser.msg_matcher.system6 import match_system6

# could also be named ChunkParser
class MessageParser():
    # the first byte of data has to be the
    # first byte of a message PAYLOAD
    # NOT the whole packet with packet header
    # and NOT the whole message with chunk header
    def parse_game_message(
            self,
            version: Literal['0.6', '0.6.4', '0.6.5', '0.7'],
            msg_id: int,
            data: bytes
    ) -> NetMessage:
        if version == '0.6':
            return match_game6(msg_id, data)
        return match_game7(msg_id, data)
    def parse_sys_message(
            self,
            version: Literal['0.6', '0.6.4', '0.6.5', '0.7'],
            msg_id: int,
            data: bytes
    ) -> NetMessage:
        if version == '0.6':
            return match_system6(msg_id, data)
        return match_system7(msg_id, data)
