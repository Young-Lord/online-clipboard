from abc import ABC
from dataclasses import dataclass
from typing import Final, Optional
from mimetypes import guess_type


@dataclass
class ContentFilter(ABC):
    def is_valid(self) -> bool:
        return True


@dataclass
class ClipTextContentFilter(ContentFilter):
    clip_name: Optional[str] = None
    content: Optional[str] = None


@dataclass
class MailContentFilter(ContentFilter):
    mail_address: Optional[str] = None
    content: Optional[str] = None


allow_filetypes: Final[set[str]] = {"audio", "video", "image", "application/pdf"}


def is_browser_previewable(filename: str) -> bool:
    mimestart = guess_type(filename)[0]

    if mimestart is not None and (
        (mimestart.split("/")[0] in allow_filetypes) or (mimestart in allow_filetypes)
    ):
        return True

    return False
