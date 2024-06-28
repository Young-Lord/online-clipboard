import json
import tomllib
from pathlib import Path
from typing import Final


load_paths: Final[list[Path]] = [
    Path("app/locales"),
    Path("server/app/locales"),
    Path(__file__) / ".." / "locales",
]
locales: dict[str, dict[str, str]] = {}
fallback = "en"


def construct_translation_items(
    result: dict[str, str], obj: dict[str, str | dict], parent: str = ""
) -> None:
    for key, value in obj.items():
        if isinstance(value, dict):
            construct_translation_items(
                result, value, f"{parent}.{key}" if parent else key
            )
        else:
            result.update({f"{parent}.{key}" if parent else key: value})


for load_path in load_paths:
    for file in load_path.glob("*.json"):
        result = {}
        with open(file, "r", encoding="utf8") as f:
            construct_translation_items(result, json.load(f))
        locales.setdefault(file.stem, {}).update(result)

    for file in load_path.glob("*.toml"):
        result = {}
        with open(file, "rb") as f:
            construct_translation_items(result, tomllib.load(f))
        locales.setdefault(file.stem, {}).update(result)

assert fallback in locales


def _t(locale: str, key: str, *values, **kwvalues) -> str:
    if locale not in locales:
        locale = fallback
    pattern = locales[locale].get(key, locales[fallback].get(key, key))
    return pattern.format(*values, **kwvalues)
