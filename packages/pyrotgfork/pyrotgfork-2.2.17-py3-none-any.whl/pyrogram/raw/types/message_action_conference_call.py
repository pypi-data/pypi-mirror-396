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


class MessageActionConferenceCall(TLObject):
    """Represents a conference call (or an invitation to a conference call, if neither the missed nor active flags are set).
If call_requests_disabled is not set or false, an incoming messageActionConferenceCall with the missed and active flags not set should trigger ringing and an incoming call screen, just like for one-on-one calls.



    Constructor of :obj:`~pyrogram.raw.base.MessageAction`.

    Details:
        - Layer: ``220``
        - ID: ``2FFE2F7A``

    Parameters:
        call_id (``int`` ``64-bit``):
            Call ID.

        missed (``bool``, *optional*):
            Whether the conference call has ended and the user hasn't joined.

        active (``bool``, *optional*):
            Whether the user is currently in the conference call.

        video (``bool``, *optional*):
            Whether this is a video conference call.

        duration (``int`` ``32-bit``, *optional*):
            Call duration, for left calls only.

        other_participants (List of :obj:`Peer <pyrogram.raw.base.Peer>`, *optional*):
            Identifiers of some other call participants.

    """

    __slots__: list[str] = ["call_id", "missed", "active", "video", "duration", "other_participants"]

    ID = 0x2ffe2f7a
    QUALNAME = "types.MessageActionConferenceCall"

    def __init__(self, *, call_id: int, missed: Optional[bool] = None, active: Optional[bool] = None, video: Optional[bool] = None, duration: Optional[int] = None, other_participants: Optional[list["raw.base.Peer"]] = None) -> None:
        self.call_id = call_id  # long
        self.missed = missed  # flags.0?true
        self.active = active  # flags.1?true
        self.video = video  # flags.4?true
        self.duration = duration  # flags.2?int
        self.other_participants = other_participants  # flags.3?Vector<Peer>

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionConferenceCall":
        
        flags = Int.read(b)
        
        missed = True if flags & (1 << 0) else False
        active = True if flags & (1 << 1) else False
        video = True if flags & (1 << 4) else False
        call_id = Long.read(b)
        
        duration = Int.read(b) if flags & (1 << 2) else None
        other_participants = TLObject.read(b) if flags & (1 << 3) else []
        
        return MessageActionConferenceCall(call_id=call_id, missed=missed, active=active, video=video, duration=duration, other_participants=other_participants)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.missed else 0
        flags |= (1 << 1) if self.active else 0
        flags |= (1 << 4) if self.video else 0
        flags |= (1 << 2) if self.duration is not None else 0
        flags |= (1 << 3) if self.other_participants else 0
        b.write(Int(flags))
        
        b.write(Long(self.call_id))
        
        if self.duration is not None:
            b.write(Int(self.duration))
        
        if self.other_participants is not None:
            b.write(Vector(self.other_participants))
        
        return b.getvalue()
