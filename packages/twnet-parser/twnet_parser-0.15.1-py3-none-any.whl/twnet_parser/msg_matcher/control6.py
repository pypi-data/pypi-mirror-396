from typing import Optional

import twnet_parser.msg6
from twnet_parser.ctrl_message import CtrlMessage

import twnet_parser.messages6.control.keep_alive as keep_alive6
import twnet_parser.messages6.control.connect as connect6
import twnet_parser.messages6.control.accept_connect as accept_connect6
import twnet_parser.messages6.control.ack_accept_connect as ack_accept_connect6
import twnet_parser.messages6.control.close as close6
from twnet_parser.packer import Unpacker
from twnet_parser.packet6 import TwPacket6

def match_control6(msg_id: int, unpacker: Unpacker, packet: TwPacket6, client: bool) -> CtrlMessage:
    msg: Optional[CtrlMessage] = None

    if msg_id == twnet_parser.msg6.CTRL_KEEPALIVE:
        msg = keep_alive6.CtrlKeepAlive()
    elif msg_id == twnet_parser.msg6.CTRL_CONNECT:
        # TODO: this does not belong here
        if unpacker.remaining_size() == 0:
            packet.set_version('0.6.4')
            msg = connect6.CtrlConnect64()
        elif unpacker.data()[0:4] == b'TKEN':
            packet.is_ddnet = True
            packet.set_version('0.6.4')
            msg = connect6.CtrlConnectDDNet()
        elif unpacker.remaining_size() > 500: # TODO: this is a totally random number
            packet.set_version('0.6.5')
            msg = connect6.CtrlConnect65()
        else:
            raise ValueError(f"Error: invalid 0.6 control connect message data={unpacker.data().hex(sep = ' ')}")
    elif msg_id == twnet_parser.msg6.CTRL_CONNECT_ACCEPT:
        msg = accept_connect6.CtrlAcceptConnect()
    elif msg_id == twnet_parser.msg6.CTRL_ACCEPT:
        msg = ack_accept_connect6.CtrlAckAcceptConnect()
    elif msg_id == twnet_parser.msg6.CTRL_CLOSE:
        msg = close6.CtrlClose()

    if msg is None:
        raise ValueError(f"Error: unknown control message id={msg_id} data={unpacker.data().hex(sep = ' ')}")

    msg.unpack(unpacker, client)
    return msg
