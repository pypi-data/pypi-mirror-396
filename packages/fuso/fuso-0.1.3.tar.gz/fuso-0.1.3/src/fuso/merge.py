from collections.abc import Callable

from fuso.dotpath import from_dotpath, to_dotpath
from fuso.utils import sort_dict, sort_list_of_dicts_by_key, to_list_of_dicts_by_key


def merge_list_of_dicts_by_key(
    values: list[dict],
    updates: list[dict],
    key: str,
    default_key: str | None = None,
    merge_functions: dict[str, Callable[[object, object], object]] | None = None,
) -> list[dict]:
    """Merge two lists of dictionaries by a specified key.

    Args:
        values (list[dict]): List of original dictionaries
        updates (list[dict]): List of dictionaries with updates
        key (str): Key to use for merging
        default_key (str | None): Key to use for default updates
        merge_functions (dict[str, Callable[[object, object], object]] | None):
            Dictionary of functions to use for merging specific keys

    Returns:
        list[dict]: Merged list of dictionaries
    """
    if merge_functions is None:
        merge_functions = {}
    dict_values = to_list_of_dicts_by_key(values or [], key=key)
    try:
        dict_updates = to_list_of_dicts_by_key(updates or [], key=key)
    except KeyError as e:
        raise KeyError(
            f"Key '{key}' not found in update. Available keys: "
            f"{', '.join(updates[0].keys())}"
        ) from e
    if default_key is not None:
        default_updates = dict_updates.pop(default_key, {})
    else:
        default_updates = {}
    result = []
    all_keys = set(dict_values.keys()).union(dict_updates.keys())
    for value_key in all_keys:
        value = dict_values.get(value_key, {})
        specific_update = dict_updates.get(value_key, {})
        merged = merge_dict(
            values=value,
            updates=merge_dict(values=default_updates, updates=specific_update),
            merge_functions=merge_functions,
        )
        merged[key] = value_key
        result.append(merged)
    return sort_list_of_dicts_by_key(result, key=key)


def merge_dict(
    values: dict,
    updates: dict,
    merge_functions: dict[str, Callable[[object, object], object]] | None = None,
    key_order: list[str] | None = None,
) -> dict:
    """Merge two dictionaries.

    Args:
        values (dict): Original dictionary
        updates (dict): Dictionary with updates
        merge_functions (dict[str, Callable[[object, object], object]] | None):
            Dictionary of functions to use for merging specific keys
        key_order (list[str] | None): Non-exhaustive list of keys to sort by

    Returns:
        dict: Merged dictionary
    """
    result = {}
    all_keys = set(values.keys()).union(updates.keys())
    for key in all_keys:
        value = values.get(key)
        update = updates.get(key)
        merge_function = merge_functions.get(key) if merge_functions else None
        if merge_function:
            result[key] = merge_function(value, update)
        else:
            result[key] = update if update is not None else value
    return sort_dict(result, key_order=key_order)


def merge(
    original: dict,
    updates: dict,
    merge_functions: dict[str, Callable[[object, object], object]] | None = None,
    post_processor=None,
    key_order: list[str] | None = None,
) -> dict:
    """Merge two dictionaries.

    Args:
        original (dict): Original dictionary
        updates (dict): Dictionary with updates
        merge_functions (dict[str, Callable[[object, object], object]] | None):
            Dictionary of functions to use for merging specific keys
        post_processor (callable | None): Function to process the result after merging
        key_order (list[str] | None): Non-exhaustive list of keys to sort by

    Returns:
        dict: Merged dictionary
    """
    if merge_functions is None:
        merge_functions = {}
    original_dotpath = to_dotpath(original)
    update_dotpath = to_dotpath(updates)
    result = {}
    all_keys = set(original_dotpath.keys()).union(update_dotpath.keys())
    for key in all_keys:
        original_value = original_dotpath.get(key)
        update_value = update_dotpath.get(key)
        merge_function = merge_functions.get(key)
        if merge_function:
            result[key] = merge_function(original_value, update_value)
        elif update_value is None:
            result[key] = original_value
        else:
            result[key] = update_value
    result = from_dotpath(result)
    if post_processor:
        result = post_processor(result)
    return sort_dict(result, key_order=key_order)
