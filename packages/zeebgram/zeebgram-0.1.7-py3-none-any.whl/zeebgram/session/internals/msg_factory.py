
from zeebgram.raw.core import Message, MsgContainer, TLObject
from zeebgram.raw.functions import Ping
from zeebgram.raw.types import MsgsAck, HttpWait
from .msg_id import MsgId
from .seq_no import SeqNo

not_content_related = (Ping, HttpWait, MsgsAck, MsgContainer)


class MsgFactory:
    def __init__(self):
        self.seq_no = SeqNo()

    def __call__(self, body: TLObject) -> Message:
        return Message(
            body,
            MsgId(),
            self.seq_no(not isinstance(body, not_content_related)),
            len(body)
        )
