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


class MessageActionSuggestedPostRefund(TLObject):
    """A suggested post  was accepted and posted or scheduled, but either the channel deleted the posted/scheduled post before stars_suggested_post_age_min seconds have elapsed, or the user refunded the payment for the stars used to pay for the suggested post.



    Constructor of :obj:`~pyrogram.raw.base.MessageAction`.

    Details:
        - Layer: ``220``
        - ID: ``69F916F8``

    Parameters:
        payer_initiated (``bool``, *optional*):
            If set, the user refunded the payment for the stars used to pay for the suggested post.

    """

    __slots__: list[str] = ["payer_initiated"]

    ID = 0x69f916f8
    QUALNAME = "types.MessageActionSuggestedPostRefund"

    def __init__(self, *, payer_initiated: Optional[bool] = None) -> None:
        self.payer_initiated = payer_initiated  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "MessageActionSuggestedPostRefund":
        
        flags = Int.read(b)
        
        payer_initiated = True if flags & (1 << 0) else False
        return MessageActionSuggestedPostRefund(payer_initiated=payer_initiated)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.payer_initiated else 0
        b.write(Int(flags))
        
        return b.getvalue()
