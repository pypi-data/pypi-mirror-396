from collections import defaultdict
from functools import reduce
from typing import List


def body_dict_from_flags(body: List[str]) -> dict:
    def nested_dict():
        return defaultdict(nested_dict)

    body_dict = nested_dict()

    for part in body:
        key, value = part.split("=", 1)
        keys = key.split(".")
        reduce(dict.__getitem__, keys[:-1], body_dict)[keys[-1]] = value

    return dict(body_dict)


def parse_params(params: List[str]) -> dict:
    params_dict = {}
    for part in params:
        if "=" not in part:
            params_dict[part] = "true"
            continue
        key, value = part.split("=", 1)
        params_dict[key] = value
    return params_dict
