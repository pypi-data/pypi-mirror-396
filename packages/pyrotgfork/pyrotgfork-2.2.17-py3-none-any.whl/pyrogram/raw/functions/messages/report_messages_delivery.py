#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO
from typing import TYPE_CHECKING, Optional, Any

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject

if TYPE_CHECKING:
    from pyrogram import raw

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class ReportMessagesDelivery(TLObject["raw.base.Bool"]):
    """Used for Telegram Gateway verification messages : indicate to the server that one or more messages were received by the client, if requested by the message.report_delivery_until_date flag or the equivalent flag in push notifications.




    Details:
        - Layer: ``220``
        - ID: ``5A6D7395``

    Parameters:
        peer (:obj:`InputPeer <pyrogram.raw.base.InputPeer>`):
            The peer where the messages were received.

        id (List of ``int`` ``32-bit``):
            The IDs of the received messages.

        push (``bool``, *optional*):
            Must be set if the messages were received from a push notification.

    Returns:
        ``bool``
    """

    __slots__: list[str] = ["peer", "id", "push"]

    ID = 0x5a6d7395
    QUALNAME = "functions.messages.ReportMessagesDelivery"

    def __init__(self, *, peer: "raw.base.InputPeer", id: list[int], push: Optional[bool] = None) -> None:
        self.peer = peer  # InputPeer
        self.id = id  # Vector<int>
        self.push = push  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "ReportMessagesDelivery":
        
        flags = Int.read(b)
        
        push = True if flags & (1 << 0) else False
        peer = TLObject.read(b)
        
        id = TLObject.read(b, Int)
        
        return ReportMessagesDelivery(peer=peer, id=id, push=push)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.push else 0
        b.write(Int(flags))
        
        b.write(self.peer.write())
        
        b.write(Vector(self.id, Int))
        
        return b.getvalue()
