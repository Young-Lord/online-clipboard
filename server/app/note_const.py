from dataclasses import asdict, dataclass, field
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


# https://passlib.readthedocs.io/en/stable/narr/quickstart.html#choosing-a-hash
PASSWORD_SCHEMES: list[str] = ["pbkdf2_sha256", "bcrypt", "argon2", "sha512_crypt"]


@dataclass
class BaseMetadata:
    name: str = "Clipd"
    description: str = "A simple clipboard app"
    owner: str = "Niko"
    version: str = "0.0.8"
    url: str = ""
    logo: str = ""
    repository: str = "https://github.com/Young-Lord/online-clipboard"
    max_content_length: int = 1000000
    max_name_length: int = 100
    max_password_length: int = 256
    max_file_size: int = 200 * 1024 * 1024  # 200 MiB
    max_file_count: int = 10
    max_all_file_size: int = 1024 * 1024 * 1024  # 1 GiB
    max_timeout: int = 60 * 60 * 24 * 365 * 3  # 3 years
    default_note_timeout: int = 60 * 60 * 24 * 30  # 30 day
    default_file_timeout: int = 60 * 60 * 24 * 30  # 30 day
    file_link_timeout: int = 60 * 60 * 1  # 1 hour
    allow_chars: str = ALLOW_CHAR_IN_NAMES
    timeout_selections: list[int] = field(
        default_factory=lambda: [
            60 * 1,  # 1 minute
            60 * 10,  # 10 minutes
            60 * 30,  # 30 minutes
            60 * 60,  # 1 hour
            60 * 60 * 6,  # 6 hours
            60 * 60 * 12,  # 12 hours
            60 * 60 * 24,  # 1 day
            60 * 60 * 24 * 7,  # 7 days
            60 * 60 * 24 * 14,  # 14 days
            60 * 60 * 24 * 30,  # 30 days
            60 * 60 * 24 * 365,  # 1 year
            60 * 60 * 24 * 365 * 3,  # 3 years
        ]
    )

    def __repr__(self):
        return f"<Metadata {self.name}>"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Metadata = BaseMetadata()
