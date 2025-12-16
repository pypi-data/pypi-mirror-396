import msgpack
import msgpack_numpy as m
import numpy as np


def get_metadata(data: dict[bytes, bytes]) -> dict[str, dict]:
    """
    Extract type, shape, and dtype information from serialized data.

    Parameters
    ----------
    data : dict[bytes, bytes]
        Dictionary with byte keys and msgpack-serialized byte values.

    Returns
    -------
    dict[str, dict]
        Mapping of decoded string keys to metadata dictionaries.
        Each metadata dict contains:

        - For ndarrays: {"type": "ndarray", "dtype": str, "shape": tuple}
        - For numpy scalars: {"type": "numpy_scalar", "dtype": str}
        - For Python types: {"type": typename} where typename is one of
          "str", "int", "float", "bool", "NoneType", "list", "dict"
    """
    metadata = {}

    for key_bytes, value_bytes in data.items():
        # Decode the key from bytes to string
        key = key_bytes.decode("utf-8")

        # Deserialize the value
        value = msgpack.unpackb(value_bytes, object_hook=m.decode)

        # Determine type and extract metadata
        metadata[key] = _get_value_metadata(value)

    return metadata


def _get_value_metadata(value) -> dict:
    """
    Extract metadata for a single value.

    Parameters
    ----------
    value : Any
        Deserialized value.

    Returns
    -------
    dict
        Type information and additional metadata.
    """
    # Check for NumPy array
    if isinstance(value, np.ndarray):
        return {
            "type": "ndarray",
            "dtype": str(value.dtype),
            "shape": value.shape,
        }

    # Check for NumPy scalar types
    if isinstance(value, np.generic):
        return {
            "type": "numpy_scalar",
            "dtype": value.dtype.name,
        }

    if isinstance(value, bytes):
        return {"type": "bytes"}
    elif value is None:
        return {"type": "NoneType"}
    elif isinstance(value, bool):
        return {"type": "bool"}
    elif isinstance(value, int):
        return {"type": "int"}
    elif isinstance(value, float):
        return {"type": "float"}
    elif isinstance(value, str):
        return {"type": "str"}
    elif isinstance(value, list):
        return {"type": "list"}
    elif isinstance(value, dict):
        return {"type": "dict"}
    else:
        # Fallback for unknown types
        return {"type": type(value).__name__}
