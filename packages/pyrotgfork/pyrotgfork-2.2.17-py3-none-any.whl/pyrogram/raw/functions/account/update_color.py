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


class UpdateColor(TLObject["raw.base.Bool"]):
    """Update the accent color and background custom emoji  of the current account.




    Details:
        - Layer: ``220``
        - ID: ``684D214E``

    Parameters:
        for_profile (``bool``, *optional*):
            Whether to change the accent color emoji pattern of the profile page; otherwise, the accent color and emoji pattern of messages will be changed.

        color (:obj:`PeerColor <pyrogram.raw.base.PeerColor>`, *optional*):
            ID of the accent color palette » to use (not RGB24, see here » for more info).

    Returns:
        ``bool``
    """

    __slots__: list[str] = ["for_profile", "color"]

    ID = 0x684d214e
    QUALNAME = "functions.account.UpdateColor"

    def __init__(self, *, for_profile: Optional[bool] = None, color: "raw.base.PeerColor" = None) -> None:
        self.for_profile = for_profile  # flags.1?true
        self.color = color  # flags.2?PeerColor

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "UpdateColor":
        
        flags = Int.read(b)
        
        for_profile = True if flags & (1 << 1) else False
        color = TLObject.read(b) if flags & (1 << 2) else None
        
        return UpdateColor(for_profile=for_profile, color=color)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 1) if self.for_profile else 0
        flags |= (1 << 2) if self.color is not None else 0
        b.write(Int(flags))
        
        if self.color is not None:
            b.write(self.color.write())
        
        return b.getvalue()
