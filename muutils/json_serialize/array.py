import typing
import warnings
from typing import Any, Dict, Iterable, Literal, Optional, Sequence

import numpy as np
import jaxtyping

from muutils.json_serialize.util import JSONitem
from muutils.tensor_utils import NDArray

# pylint: disable=unused-argument

ArrayMode = Literal["list", "array_list_meta", "array_hex_meta", "external"]


def array_n_elements(arr: jaxtyping.Shaped[jaxtyping.Array, "..."]) -> int:  # type: ignore[name-defined]
    """get the number of elements in an array"""
    if isinstance(arr, np.ndarray):
        return arr.size
    elif str(type(arr)) == "<class 'torch.Tensor'>":
        return arr.nelement()
    else:
        raise TypeError(f"invalid type: {type(arr)}")


def arr_metadata(arr: jaxtyping.Shaped[jaxtyping.Array, "..."]) -> Dict[str, Any]:
    """get metadata for a numpy array"""
    return {
        "shape": arr.shape,
        "dtype": str(arr.dtype),
        "n_elements": array_n_elements(arr),
    }


def serialize_array(
    jser: "JsonSerializer",  # type: ignore[name-defined]
    arr: np.ndarray,
    path: str | Sequence[str | int],
    array_mode: ArrayMode | None = None,
) -> JSONitem:
    """serialize a numpy or pytorch array in one of several modes

    if the object is zero-dimensional, simply get the unique item

    `array_mode: ArrayMode` can be one of:
    - `list`: serialize as a list of values, no metadata (equivalent to `arr.tolist()`)
    - `array_list_meta`: serialize dict with metadata, actual list under the key `data`
    - `array_hex_meta`: serialize dict with metadata, actual hex string under the key `data`
        # - `external`: reference to external file

    for `array_list_meta` and `array_hex_meta`, the output will look like
    ```
    {
        "__format__": <array_list_meta|array_hex_meta>,
        "shape": arr.shape,
        "dtype": str(arr.dtype),
        "data": <arr.tolist()|arr.tobytes().hex()>,
    }
    ```

    # Parameters:
     - `arr : Any` array to serialize
     - `array_mode : ArrayMode` mode in which to serialize the array
       (defaults to `None` and inheriting from `jser: JsonSerializer`)

    # Returns:
     - `JSONitem`
       json serialized array

    # Raises:
     - `KeyError` : if the array mode is not valid
    """

    if len(arr.shape) == 0:
        return arr.item()

    if array_mode is None:
        array_mode = jser.array_mode

    if array_mode == "array_list_meta":
        return {
            "__format__": "array_list_meta",
            "data": arr.tolist(),
            **arr_metadata(arr),
        }
    elif array_mode == "list":
        return arr.tolist()
    elif array_mode == "array_hex_meta":
        return {
            "__format__": "array_hex_meta",
            "data": arr.tobytes().hex(),
            **arr_metadata(arr),
        }
    else:
        raise KeyError(f"invalid array_mode: {array_mode}")


def infer_array_mode(arr: JSONitem) -> ArrayMode:
    """given a serialized array, infer the mode

    assumes the array was serialized via `serialize_array()`
    """
    if isinstance(arr, typing.Mapping):
        fmt: Optional[str] = arr.get("__format__", None)
        if fmt == "array_list_meta":
            if not isinstance(arr["data"], Iterable):
                raise ValueError(f"invalid list format: {type(arr['data']) = }\t{arr}")
            return fmt  # type: ignore[return-value]
        elif fmt == "array_hex_meta":
            if not isinstance(arr["data"], str):
                raise ValueError(f"invalid hex format: {type(arr['data']) = }\t{arr}")
            return fmt  # type: ignore[return-value]
        elif fmt == "external:npy":
            if ("$ref" not in arr) or (not isinstance(arr["$ref"], (str, np.ndarray))):
                raise ValueError(
                    f"invalid external format: {type(arr['$ref']) = }\t{arr}"
                )
            return fmt  # type: ignore[return-value]
        else:
            raise ValueError(f"invalid format: {arr}")
    elif isinstance(arr, list):
        return "list"  # type: ignore[return-value]
    else:
        raise ValueError(f"cannot infer array_mode from\t{type(arr) = }\n{arr = }")


def load_array(arr: JSONitem, array_mode: Optional[ArrayMode] = None) -> Any:
    """load a json-serialized array, infer the mode if not specified"""
    # return arr if its already a numpy array
    if isinstance(arr, np.ndarray) and array_mode is None:
        return arr

    # try to infer the array_mode
    array_mode_inferred: ArrayMode = infer_array_mode(arr)
    if array_mode is None:
        array_mode = array_mode_inferred
    elif array_mode != array_mode_inferred:
        warnings.warn(
            f"array_mode {array_mode} does not match inferred array_mode {array_mode_inferred}"
        )

    # actually load the array
    if array_mode == "array_list_meta":
        assert isinstance(arr, dict), f"invalid list format: {type(arr) = }\n{arr = }"

        data = np.array(arr["data"], dtype=arr["dtype"])
        if tuple(arr["shape"]) != tuple(data.shape):
            raise ValueError(f"invalid shape: {arr}")
        return data

    elif array_mode == "array_hex_meta":
        assert isinstance(arr, dict), f"invalid list format: {type(arr) = }\n{arr = }"

        data = np.frombuffer(bytes.fromhex(arr["data"]), dtype=arr["dtype"])
        return data.reshape(arr["shape"])

    elif array_mode == "list":
        assert isinstance(arr, list), f"invalid list format: {type(arr) = }\n{arr = }"

        return np.array(arr)
    elif array_mode == "external:npy":
        data = np.array(arr["$ref"], dtype=arr["dtype"])
        if tuple(arr["shape"]) != tuple(data.shape):
            raise ValueError(f"invalid shape: {arr}")
        return data
    else:
        raise ValueError(f"invalid array_mode: {array_mode}")
