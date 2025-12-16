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

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import TYPE_CHECKING, Union
from pyrogram import raw
from pyrogram.raw.core import BaseTypeMeta


if TYPE_CHECKING:
    PaidMessagesRevenue = Union[raw.types.account.PaidMessagesRevenue]
else:
    # noinspection PyRedeclaration
    class PaidMessagesRevenue(metaclass=BaseTypeMeta):  # type: ignore
        """Total number of non-refunded Telegram Stars a user has spent on sending us messages either directly or through a channel, see here  for more info on paid messages.

Telegram Stars are virtual items that allow users to purchase digital goods and services from bots and mini apps inside the Telegram ecosystem, send gifts to content creators on the Telegram platform, and more.
Telegram Stars can be used to pay for sending messages to users, supergroups and channels that have configured paid messages, requiring a payment for every message sent to them.


    Constructors:
        This base type has 1 constructor available.

        .. currentmodule:: pyrogram.raw.types

        .. autosummary::
            :nosignatures:

            account.PaidMessagesRevenue

    Functions:
        This object can be returned by 1 function.

        .. currentmodule:: pyrogram.raw.functions

        .. autosummary::
            :nosignatures:

            account.GetPaidMessagesRevenue
        """

        QUALNAME = "pyrogram.raw.base.account.PaidMessagesRevenue"
        __union_types__ = Union[raw.types.account.PaidMessagesRevenue]

        def __init__(self):
            raise TypeError(
                "Base types can only be used for type checking purposes: "
                "you tried to use a base type instance as argument, "
                "but you need to instantiate one of its constructors instead. "
                "More info: https://telegramplayground.github.io/pyrogram/telegram/base/paid-messages-revenue"
            )
