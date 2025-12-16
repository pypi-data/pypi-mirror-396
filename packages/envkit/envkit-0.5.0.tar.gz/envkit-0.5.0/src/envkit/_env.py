from __future__ import annotations

from os import getenv
from typing import TYPE_CHECKING, final, overload

if TYPE_CHECKING:
    from enum import Enum
    from typing import Callable, Literal, LiteralString


def _get[T](
    name: str, required: bool, default: T, converter: Callable[[str], T]
) -> T | None:
    raw = getenv(name)
    if raw is None:
        if required:
            raise KeyError(f"Environment variable {name!r} is required but not set")
        return default

    return converter(raw)


@final
class Env:
    @overload
    @staticmethod
    def str(
        name: str,
        *,
        required: Literal[False],
        default: str,
        strip: bool = False,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> str: ...

    @overload
    @staticmethod
    def str(
        name: str,
        *,
        required: Literal[False],
        default: None = None,
        strip: bool = False,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> str | None: ...

    @overload
    @staticmethod
    def str(
        name: str,
        *,
        required: Literal[True] = True,
        default: None = None,
        strip: bool = False,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> str: ...

    @staticmethod
    def str(
        name: str,
        *,
        required: bool = True,
        default: str | None = None,
        strip: bool = False,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> str | None:
        if (
            min_length is not None
            and max_length is not None
            and min_length > max_length
        ):
            raise ValueError("min_length cannot be greater than max_length")

        def converter(value: str) -> str:
            if strip:
                value = value.strip()

            if min_length is not None and len(value) < min_length:
                raise ValueError(f"{name!r} must be at least {min_length} chars")
            if max_length is not None and len(value) > max_length:
                raise ValueError(f"{name!r} must be at most {max_length} chars")
            return value

        return _get(name, required, default, converter)

    @overload
    @staticmethod
    def int(
        name: str,
        *,
        required: Literal[False],
        default: int,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int: ...

    @overload
    @staticmethod
    def int(
        name: str,
        *,
        required: Literal[False],
        default: None = None,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int | None: ...

    @overload
    @staticmethod
    def int(
        name: str,
        *,
        required: Literal[True] = True,
        default: None = None,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int: ...

    @staticmethod
    def int(
        name: str,
        *,
        required: bool = True,
        default: int | None = None,
        min_value: int | None = None,
        max_value: int | None = None,
    ) -> int | None:
        if min_value is not None and max_value is not None and min_value > max_value:
            raise ValueError("min_value cannot be greater than max_value")

        def converter(raw: str) -> int:
            try:
                value = int(raw.strip())
            except ValueError as e:
                raise ValueError(f"{name!r} must be an integer") from e

            if min_value is not None and value < min_value:
                raise ValueError(f"{name!r} must be >= {min_value}")
            if max_value is not None and value > max_value:
                raise ValueError(f"{name!r} must be <= {max_value}")
            return value

        return _get(name, required, default, converter)

    @overload
    @staticmethod
    def bool(
        name: str,
        *,
        required: Literal[False],
        default: bool,
    ) -> bool: ...

    @overload
    @staticmethod
    def bool(
        name: str,
        *,
        required: Literal[False],
        default: None = None,
    ) -> bool | None: ...

    @overload
    @staticmethod
    def bool(
        name: str,
        *,
        required: Literal[True] = True,
        default: None = None,
    ) -> bool: ...

    @staticmethod
    def bool(
        name: str,
        *,
        required: bool = True,
        default: bool | None = None,
    ) -> bool | None:
        def converter(raw: str) -> bool:
            match raw.strip().lower():
                case "true" | "1" | "yes" | "on":
                    return True
                case "false" | "0" | "no" | "off":
                    return False
                case _:
                    raise ValueError(f"{name!r} must be a boolean")

        return _get(name, required, default, converter)

    @overload
    @staticmethod
    def enum[E: Enum](
        name: str,
        enum: type[E],
        *,
        required: Literal[False],
        default: E,
        case_sensitive: bool = True,
    ) -> E: ...

    @overload
    @staticmethod
    def enum[E: Enum](
        name: str,
        enum: type[E],
        *,
        required: Literal[False],
        default: None = None,
        case_sensitive: bool = True,
    ) -> E | None: ...

    @overload
    @staticmethod
    def enum[E: Enum](
        name: str,
        enum: type[E],
        *,
        required: Literal[True] = True,
        default: None = None,
        case_sensitive: bool = True,
    ) -> E: ...

    @staticmethod
    def enum[E: Enum](
        name: str,
        enum: type[E],
        *,
        required: bool = True,
        default: E | None = None,
        case_sensitive: bool = True,
    ) -> E | None:
        def converter(key: str) -> E:
            key = key.strip()
            if not case_sensitive:
                insensitive_keys = {k.casefold(): k for k in enum.__members__}
                if len(insensitive_keys) < len(enum):
                    raise ValueError(
                        "Enum contains conflicting keys when case-insensitivity is applied"
                    )

                try:
                    key = insensitive_keys[key.casefold()]
                except KeyError:
                    valid = list(enum.__members__.keys())
                    raise ValueError(f"{name!r} must be one of {valid!r}")

            try:
                return enum[key]
            except KeyError:
                valid = list(enum.__members__.keys())
                raise ValueError(f"{name!r} must be one of {valid!r}")

        return _get(name, required, default, converter)

    @overload
    @staticmethod
    def literal[L: LiteralString](
        name: str,
        choices: tuple[L, ...],
        *,
        required: Literal[False],
        default: L,
        strip: bool = True,
    ) -> L: ...

    @overload
    @staticmethod
    def literal[L: LiteralString](
        name: str,
        choices: tuple[L, ...],
        *,
        required: Literal[False],
        default: None = None,
        strip: bool = True,
    ) -> L | None: ...

    @overload
    @staticmethod
    def literal[L: LiteralString](
        name: str,
        choices: tuple[L, ...],
        *,
        required: Literal[True] = True,
        default: None = None,
        strip: bool = True,
    ) -> L: ...

    @staticmethod
    def literal[L: LiteralString](
        name: str,
        choices: tuple[L, ...],
        *,
        required: bool = True,
        default: L | None = None,
        strip: bool = True,
    ) -> L | None:
        def converter(value: str) -> L:
            if strip:
                value = value.strip()
            if value not in choices:
                raise ValueError(f"{name!r} must be one of {choices!r}")
            return value

        return _get(name, required, default, converter)


__all__ = [
    "Env",
]
