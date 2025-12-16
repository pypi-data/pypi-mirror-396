from typing import Optional

import twnet_parser.msg7
from twnet_parser.ctrl_message import CtrlMessage

import twnet_parser.messages7.control.keep_alive as keep_alive7
import twnet_parser.messages7.control.connect as connect7
import twnet_parser.messages7.control.accept as accept7
import twnet_parser.messages7.control.close as close7
import twnet_parser.messages7.control.token as token7
from twnet_parser.packer import Unpacker

def match_control7(msg_id: int, data: bytes, client: bool) -> CtrlMessage:
    msg: Optional[CtrlMessage] = None

    if msg_id == twnet_parser.msg7.CTRL_KEEPALIVE:
        msg = keep_alive7.CtrlKeepAlive()
    elif msg_id == twnet_parser.msg7.CTRL_CONNECT:
        msg = connect7.CtrlConnect()
    elif msg_id == twnet_parser.msg7.CTRL_ACCEPT:
        msg = accept7.CtrlAccept()
    elif msg_id == twnet_parser.msg7.CTRL_CLOSE:
        msg = close7.CtrlClose()
    elif msg_id == twnet_parser.msg7.CTRL_TOKEN:
        msg = token7.CtrlToken()

    if msg is None:
        raise ValueError(f"Error: unknown control message id={msg_id} data={data[0]}")

    unpacker = Unpacker(data)
    msg.unpack(unpacker, client)
    return msg
