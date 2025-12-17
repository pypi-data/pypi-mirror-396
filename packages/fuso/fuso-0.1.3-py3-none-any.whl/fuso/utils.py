def to_list_of_dicts_by_key(values: list, key: str = "name") -> dict:
    """Convert a list of dictionaries to a dictionary of dictionaries
        using a specified key.

    Args:
        values (list): List of dictionaries to convert
        key (str): Key to use as the dictionary key

    Returns:
        dict: Dictionary of dictionaries
    """
    result = {}
    for value in values:
        value_copy = value.copy()
        try:
            value_key = value_copy.pop(key)
            result[value_key] = value_copy
        except KeyError:
            all_keys = ", ".join(value.keys())
            raise KeyError(
                f"Key '{key}' not found in value. Available keys: {all_keys}"
            )
    return result


def sort_list_of_dicts_by_key(
    values: list[dict], key: str, reverse: bool = False
) -> list[dict]:
    """Sort a list of dictionaries by a specified key.

    Args:
        values (list[dict]): List of dictionaries to sort
        key (str): Key to sort by
        reverse (bool): Whether to sort in descending order

    Returns:
        list[dict]: Sorted list of dictionaries
    """
    return sorted(values, key=lambda x: x[key], reverse=reverse)


def sort_dict(d: dict, key_order: list[str] | None = None) -> dict:
    """Sort a dictionary by a given (non-exhaustive) key order.

    Args:
        d (dict): dictionary to sort
        key_order (list[str]): Non-exhaustive list of keys to sort by

    Returns:
        dict: dictionary with ordered values
    """
    if key_order is None:
        key_order = []
    other_keys = [k for k in d.keys() if k not in key_order]
    order = key_order + other_keys
    return dict(sorted(d.items(), key=lambda x: order.index(x[0])))
