from typing import TypeVar, overload

T = TypeVar("T")


def _to_dotpath(value: dict, parent_key: str = "", sep: str = "."):
    """Convert a nested dictionary to a dotpath dictionary.

    Args:
        value (dict): Nested dictionary to convert
        parent_key (str): Parent key for recursion
        sep (str): Separator to use for dotpath

    Returns:
        dict: Dotpath dictionary
    """
    items = []
    for k, v in value.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_to_dotpath(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            fields = []
            for item in v:
                if isinstance(item, dict):
                    fields.append(_to_dotpath(item, "", sep=sep))
                else:
                    fields.append(item)
            items.append((new_key, fields))
        else:
            items.append((new_key, v))
    return dict(items)


def to_dotpath(value: dict, sep: str = ".") -> dict:
    """Convert a nested dictionary to a dotpath dictionary.

    Args:
        value (dict): Nested dictionary to convert
        sep (str): Separator to use for dotpath

    Returns:
        dict: Dotpath dictionary
    """
    return _to_dotpath(value, sep=sep)


@overload
def from_dotpath(value: str, sep: str = ".") -> str: ...


@overload
def from_dotpath(value: int, sep: str = ".") -> int: ...


@overload
def from_dotpath(value: float, sep: str = ".") -> float: ...


@overload
def from_dotpath(value: bool, sep: str = ".") -> bool: ...


@overload
def from_dotpath(value: None, sep: str = ".") -> None: ...


@overload
def from_dotpath(value: list, sep: str = ".") -> list: ...


@overload
def from_dotpath(
    value: dict,
    sep: str = ".",
    dotpath_ignores: list | None = None,
) -> dict: ...


def from_dotpath(
    value: dict | list | str | int | float | bool | None,
    sep: str = ".",
    dotpath_ignores: list | None = None,
):
    """Convert a dotpath dictionary to a nested dictionary.

    Args:
        value (dict | list | str | int | float | bool | None): Dotpath dictionary to
            convert
        sep (str): Separator used for dotpath
        dotpath_ignores (list | None): List of dotpath keys to ignore during conversion

    Returns:
        dict | list | str | int | float | bool | None: Nested dictionary
    """
    if dotpath_ignores is None:
        dotpath_ignores = []
    if isinstance(value, list):
        return [from_dotpath(item, sep=sep) for item in value]
    elif isinstance(value, dict):
        result = {}
        for compound_key, compound_value in value.items():
            if compound_key in dotpath_ignores:
                result[compound_key] = compound_value
                continue
            keys = compound_key.split(sep)
            d = result
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            if isinstance(compound_value, list):
                d[keys[-1]] = from_dotpath(compound_value, sep=sep)
            elif isinstance(compound_value, dict):
                d[keys[-1]] = from_dotpath(compound_value, sep=sep)
            else:
                d[keys[-1]] = compound_value
        return result
    else:
        return value
