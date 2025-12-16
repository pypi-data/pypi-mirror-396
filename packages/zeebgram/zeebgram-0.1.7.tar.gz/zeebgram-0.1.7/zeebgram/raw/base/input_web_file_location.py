
# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #

from typing import Union
from zeebgram import raw
from zeebgram.raw.core import TLObject

InputWebFileLocation = Union[raw.types.InputWebFileAudioAlbumThumbLocation, raw.types.InputWebFileGeoPointLocation, raw.types.InputWebFileLocation]


# noinspection PyRedeclaration
class InputWebFileLocation:  # type: ignore
    """Telegram API base type.

    Constructors:
        This base type has 3 constructors available.

        .. currentmodule:: zeebgram.raw.types

        .. autosummary::
            :nosignatures:

            InputWebFileAudioAlbumThumbLocation
            InputWebFileGeoPointLocation
            InputWebFileLocation
    """

    QUALNAME = "zeebgram.raw.base.InputWebFileLocation"

    def __init__(self):
        raise TypeError("Base types can only be used for type checking purposes: "
                        "you tried to use a base type instance as argument, "
                        "but you need to instantiate one of its constructors instead. "
                        "More info: https://docs.zeebgram.org/telegram/base/input-web-file-location")
