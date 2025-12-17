import ctypes
import re
import numpy as np


def norm_stokes_name(name: str):
    name = name.strip()
    name = name.replace("psrdada_cpp::", "")
    if name.startswith("Stokes"):
        return name[len("Stokes"):]
    return name

def stokes_type(type_name):
    m = re.compile(r"(?:[\w:]+::)?StokesVector\s*<\s*([^,<>]+?)\s*,\s*(.*?)\s*>$").match(type_name)
    if m:
        storage_type = m.group(1).strip()
        param_list = [p.strip() for p in m.group(2).split(",")]
        # base scalar dtype
        base_dtype = to_numpy_dtype(storage_type)
        # convert StokesXYZ → field name
        field_names = [norm_stokes_name(p) for p in param_list]
        # build structured dtype
        fields = [(name, base_dtype) for name in field_names]
        return np.dtype(fields)
    return None

def to_ctypes_type(type_name: str, user_conversions: dict=None) -> any:
    """Convert a C/C++ type based on its string representation into a ctype

    Args:
        type_name (str): The type name e.g. 'float' -> np.float32, 'int4' -> np.dtype("int32",(4,))
        user_conversions (dict, optional): convert an arbiatry name into a type. Defaults to None.
            e.g. {"Yo, I'm Mr. Bool": ctypes.c_bool} -> ctypes.c_bool

    Raises:
        TypeError: No suiteable conversion found

    Returns:
        ctype: The determined type
    """
    type_name = type_name.replace("std::", "")
    # user-defined special conversions
    if user_conversions is not None and type_name in user_conversions:
        return user_conversions[type_name]
    # Complex data types #
    complex_match = re.match(r"complex<(.+)>", type_name)
    # Will always return a vector type, never np.complexXX
    if complex_match:
        inner = complex_match.group(1).replace(" ", "")
        inner_ctype = to_ctypes_type(inner, user_conversions)
        return inner_ctype * 2
    # normalize
    type_name = type_name.replace(" ", "")
    type_name = type_name.replace("unsigned", "u")
    type_name = type_name.replace("signed", "")
    # trivial cases
    try:
        return getattr(ctypes, f"c_{type_name}")
    except AttributeError:
        pass
    # types like uint64_t, int32_t
    try:
        return getattr(ctypes, f"c_{type_name.rstrip('_t')}")
    except AttributeError:
        pass
    # vector types like float4, char2
    match = re.match(r"([a-zA-Z]+)(\d+)$", type_name)
    if match:
        base, count = match.groups()
        if base == "char":
            base = "int8"  # signed char fallback
        return getattr(ctypes, f"c_{base}") * int(count)
    raise TypeError(f"No valid type conversion for: {type_name}")


def to_numpy_dtype(type_name: str, user_conversions: dict=None) -> np.dtype:
    """Convert a C/C++ type based on its string representation into a NumPy dtype

    Args:
        type_name (str): The type name e.g. 'float' -> np.float32, 'int4' -> np.dtype("int32",(4,))
        user_conversions (dict, optional): convert an arbiatry name into a type. Defaults to None.
            e.g. {"Yo, I'm Mr. Bool": ctypes.c_bool} -> np.bool_
                 {"Hey, I'm Mrs. Bool": np.bool_} -> np.bool_

    Raises:
        TypeError: No suiteable conversion found

    Returns:
        np.dtype: The determined type
    """
    # If the user conversion is already a np.dtype it should not be passed to to_ctypes_type
    if user_conversions is not None and type_name in user_conversions:
        if isinstance(user_conversions[type_name], np.dtype):
            return user_conversions[type_name]
    res = stokes_type(type_name)
    if res is not None:
        return res
    ctype = to_ctypes_type(type_name, user_conversions)

    try:
        return np.dtype(ctype)
    except TypeError:
        raise TypeError(f"Cannot convert {type_name} (ctype={ctype}) to NumPy dtype")