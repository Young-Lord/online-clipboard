from abc import ABC
from dataclasses import dataclass
from typing import Optional

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
