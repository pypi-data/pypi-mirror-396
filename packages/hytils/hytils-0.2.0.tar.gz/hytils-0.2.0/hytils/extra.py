import inspect
from typing import Any, Type


def arg_list(model_class: type) -> list[str]:
    return [
        kw
        for kw in inspect.signature(model_class.__init__).parameters.keys()
    ][1:]


def swap_keys_values(d: Type[dict]) -> Type[dict]:
    """Swap keys and values in a dictionary.

    This function swaps the keys and values of the input dictionary.
    If a value is a list, it uses the value items as new keys, with
    the original key as the corresponding value. If a value already exists
    as a key in the swapped dictionary, it will be overwritten.
    """
    swapped: dict[Any, Any] = {}
    for k, v in d.items():
        swapped.update({x: k for x in (v if isinstance(v, list) else [v])})
    return swapped
