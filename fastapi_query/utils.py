from typing import Dict, Any


def flatten_dict(
        obj: Dict[str, Any],
        delimiter: str = "__"
) -> Dict[str, Any]:
    res: Dict[str, Any] = {}

    for key, val in obj.items():
        if isinstance(val, dict):
            nested_obj = flatten_dict(
                obj=val,
                delimiter=delimiter
            )
            res.update({
                f"{key}{delimiter}{nested_key}": val
                for nested_key, val in nested_obj.items()
            })
        else:
            res[key] = val

    return res
