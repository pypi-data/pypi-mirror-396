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


class InvokeWithReCaptcha(TLObject["raw.base.X"]):
    """Official clients only: re-execute a method call that required reCAPTCHA verification via a RECAPTCHA_CHECK_%s__%s, where the first placeholder is the action, and the second one is the reCAPTCHA key ID.




    Details:
        - Layer: ``220``
        - ID: ``ADBB0F94``

    Parameters:
        token (``str``):
            reCAPTCHA token received after verification.

        query (Any function from :obj:`~pyrogram.raw.functions`):
            The original method call.

    Returns:
        Any object from :obj:`~pyrogram.raw.types`
    """

    __slots__: list[str] = ["token", "query"]

    ID = 0xadbb0f94
    QUALNAME = "functions.InvokeWithReCaptcha"

    def __init__(self, *, token: str, query: TLObject) -> None:
        self.token = token  # string
        self.query = query  # !X

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "InvokeWithReCaptcha":
        # No flags
        
        token = String.read(b)
        
        query = TLObject.read(b)
        
        return InvokeWithReCaptcha(token=token, query=query)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(String(self.token))
        
        b.write(self.query.write())
        
        return b.getvalue()
