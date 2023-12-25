from dataclasses import asdict, dataclass
import string
from typing import Any, Final

ALLOW_CHAR_IN_NAMES: Final[str] = string.ascii_letters + string.digits + "-_"
DISABLE_WORDS_IN_NAMES: Final[set[str]] = {
    "api",
    "static",
    "admin",
    "login",
    "logout",
    "register",
    "about",
}
READONLY_PREFIX: Final[str] = "ro*"


@dataclass
class BaseMetadata:
    name: str = "Clipboard"
    description: str = "A simple clipboard app"
    owner: str = "Niko"
    version: str = "0.0.1"
    url: str = ""
    logo: str = ""
    repository: str = "https://github.com/Young-Lord/online-clipboard"
    max_content_length: int = 1000000
    max_name_length: int = 100
    max_password_length: int = 256
    max_file_size: int = 50 * 1024 * 1024  # 50 MiB
    max_file_count: int = 10
    max_timeout: int = 60 * 60 * 24 * 365 * 3  # 3 years
    default_timeout: int = 60 * 60 * 24 * 30  # 30 day
    default_file_timeout: int = 60 * 60 * 24 * 30  # 30 day
    file_link_timeout: int = 60 * 60 * 1 # 1 hour
    allow_chars: str = ALLOW_CHAR_IN_NAMES

    def __repr__(self):
        return f"<Metadata {self.name}>"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Metadata = BaseMetadata()
