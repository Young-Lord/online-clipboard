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
    name: str = "Clip"
    description: str = "A simple clipboard app"
    owner: str = "Niko"
    email: str = "ly-niko@qq.com"
    version: str = "0.0.18"
    url: str = ""
    logo: str = ""
    repository: str = "https://github.com/Young-Lord/online-clipboard"
    max_content_length: int = 1000000
    max_name_length: int = 100
    max_password_length: int = 256
    max_file_size: int = 200 * 1024 * 1024  # 200 MiB
    max_file_count: int = 10
    max_all_file_size: int = 1024 * 1024 * 1024  # 1 GiB
    # set any of two above to 0 to disable file upload
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
    limiter_default: list[str] = field(
        default_factory=lambda: ["100/minute"]
    )  # limiter for some API endpoint
    limiter_file: str = (
        "15/minute"  # delim with `;`, limiter for file upload / download / delete / get info
    )
    limiter_note: str = (
        "100/minute"  # limiter for any note API, doesn't include file-related API
    )
    limiter_send_mail: str = "20/hour"  # limiter for sending mail
    illegal_ban_time: list[int] = (
        field(  # how long should clip been banned for each report
            default_factory=lambda: [
                60 * 30,  # 30 minutes
                60 * 60 * 24,  # 1 day
                60 * 60 * 24 * 7,  # 7 days
                -1,  # forever
            ]
        )
    )
    allow_mail: bool = True
    mail_max_content: int = max_content_length
    mail_verify_timeout: int = 60 * 60 * 24 * 180  # 180 days

    def __repr__(self):
        return f"<Metadata {self.name}>"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


Metadata = BaseMetadata()
