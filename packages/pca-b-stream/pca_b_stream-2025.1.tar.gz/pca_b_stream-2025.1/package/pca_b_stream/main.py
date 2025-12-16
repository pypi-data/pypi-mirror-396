"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import base64 as bs64
import sys as syst
import typing as h
import zlib as cmpr

import leb128 as lenc
import numpy as nmpy

array_t = nmpy.ndarray


# See also: nmpy.sctypes and nmpy.sctypeDict
# /!\ Some types have several codes (e.g., "l" = "p" = numpy.int64; see mpy.sctypeDict)
VALID_NUMPY_TYPES = "?" + nmpy.typecodes["AllInteger"] + nmpy.typecodes["Float"]


def PCA2BStream(
    mask: array_t, /, *, should_check_mask: bool = False
) -> bytes | list[str]:
    """"""
    if should_check_mask:
        issues = PCArrayIssues(mask)
        if issues.__len__() > 0:
            return issues

    # --- Storage
    dtype = mask.dtype
    byte_order = dtype.byteorder
    if byte_order == "=":
        if syst.byteorder == "big":
            byte_order = ">"
        else:
            byte_order = "<"
    if mask.flags["C_CONTIGUOUS"]:
        enumeration_order = "C"
    else:
        enumeration_order = "F"
    storage = byte_order + dtype.char + enumeration_order

    # --- Geometry
    geometry = [mask.ndim, *mask.shape]

    # --- Content
    raveled_mask = nmpy.ravel(mask, order="K")
    max_value = int(nmpy.amax(raveled_mask))
    if max_value > 1:
        content = []
        for value in range(1, max_value + 1):
            content.append(_EncodedMask(raveled_mask == value))
        content = b"".join(content)
    elif max_value > 0:
        content = _EncodedMask(raveled_mask.astype(nmpy.bool_, copy=False))
    else:
        content = b""

    # --- Complete stream
    stream = bytes(storage, "ascii") + _EncodedIntegers(geometry) + content

    # --- Compression and encoding
    compressed = cmpr.compress(stream, cmpr.Z_BEST_COMPRESSION)
    if compressed.__len__() < stream.__len__():
        stream = b"1" + compressed
    else:
        stream = b"0" + stream

    return bs64.b85encode(stream)


def BStream2PCA(
    stream: bytes, /, *, just_details: bool = False
) -> array_t | tuple[bool, int, int, str, h.Sequence[int]]:
    """"""
    output = None

    # --- Decoding and decompression
    decoded = bs64.b85decode(stream)
    if decoded[0] == ord("0"):  # decoded[0] is an integer. Hence, the "ord".
        uncompressed = decoded[1:]
    else:
        uncompressed = cmpr.decompress(decoded[1:])

    # --- Storage
    storage_length = 3
    byte_order, dtype, enumeration_order = uncompressed[:storage_length]
    if byte_order == ord("|"):
        dtype_spec = chr(dtype)
    else:
        dtype_spec = chr(byte_order) + chr(dtype)
    enumeration_order = chr(enumeration_order)
    next_reading_idx = storage_length

    # --- Geometry
    ndim, next_reading_idx = _DecodedIntegers(
        uncompressed, next_reading_idx=next_reading_idx, n_integers=1
    )
    shape, next_reading_idx = _DecodedIntegers(
        uncompressed, next_reading_idx=next_reading_idx, n_integers=ndim
    )
    if isinstance(shape, int):  # One-dimensional array.
        shape = (shape,)

    if just_details:
        return (decoded[0] != ord("0"), byte_order, dtype, enumeration_order, shape)

    if next_reading_idx == uncompressed.__len__():
        return nmpy.zeros(shape, dtype=dtype_spec, order=enumeration_order)

    value = 1
    while next_reading_idx < uncompressed.__len__():
        first_value = int(chr(uncompressed[next_reading_idx]))
        next_reading_idx += 1

        if first_value < 2:
            substream_length, next_reading_idx = _DecodedIntegers(
                uncompressed, next_reading_idx=next_reading_idx, n_integers=1
            )
            run_lengths = _DecodedIntegers(
                uncompressed[next_reading_idx : (next_reading_idx + substream_length)]
            )
            value_groups = (
                _lgt * (_idx % 2,)
                for _idx, _lgt in enumerate(run_lengths, start=first_value)
            )
            values = tuple(_elm for _grp in value_groups for _elm in _grp)

            if output is None:
                output = nmpy.array(values, dtype=dtype_spec)
                output = nmpy.reshape(output, shape, order=enumeration_order)
            else:
                mask = nmpy.array(values, dtype=nmpy.bool_)
                mask = nmpy.reshape(mask, shape, order=enumeration_order)
                output[mask] = value
        else:
            substream_length = 0
            if output is None:
                output = nmpy.zeros(shape, dtype=dtype_spec, order=enumeration_order)

        next_reading_idx += substream_length
        value += 1

    return output


def BStreamDetails(
    stream: bytes,
    /,
    *,
    details: str = "+",
    should_print: bool = False,
    should_return: bool = True,
) -> dict[str, h.Any] | tuple[h.Any, ...] | h.Any | None:
    """
    Details: if "+", retrieve all details. Otherwise, pick among:
    c: compression indicator
    d: array dimension
    l: array lengths per dimension
    t: dtype type code; See: https://numpy.org/doc/stable/reference/generated/numpy.dtype.char.html
    T: dtype name; Translated from "t" by Numpy.sctypeDict
    o: enumeration order; See: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flags.html, ?_CONTIGUOUS
    e: endianness (or byte order); See: https://numpy.org/doc/stable/reference/generated/numpy.dtype.byteorder.html
    """
    if not (should_print or should_return):
        return None

    if details == "+":
        output = {}
    else:
        output = {_key: None for _key in details}

    (is_compressed, byte_order, dtype, enumeration_order, shape) = BStream2PCA(
        stream, just_details=True
    )

    if ("c" in details) or (details == "+"):
        output["c"] = is_compressed

    if ("d" in details) or (details == "+"):
        output["d"] = shape.__len__()
    if ("l" in details) or (details == "+"):
        output["l"] = tuple(shape)

    if ("t" in details) or (details == "+"):
        output["t"] = chr(dtype)
    if ("T" in details) or (details == "+"):
        output["T"] = nmpy.sctypeDict[nmpy.dtype(chr(dtype)).name].__name__
    if ("o" in details) or (details == "+"):
        output["o"] = enumeration_order
    if ("e" in details) or (details == "+"):
        output["e"] = chr(byte_order)

    if should_print:
        for key, value in output.items():
            print(f"{key} = {value}")

    if should_return:
        if details == "+":
            return output
        else:
            output = tuple(output.values())
            if output.__len__() > 1:
                return output
            elif output.__len__() > 0:
                return output[0]
            else:
                return output  # Empty tuple

    return None


def PCArrayIssues(mask: array_t, /) -> list[str]:
    """"""
    output = []

    if mask.dtype.char not in VALID_NUMPY_TYPES:
        output.append(
            f"{mask.dtype.name}: Invalid type with code {mask.dtype.char}; "
            f"Expected={VALID_NUMPY_TYPES}."
        )

    unique_values = tuple(nmpy.unique(mask))
    if (unique_values != (False, True)) and (
        not set(unique_values).issubset(range(int(unique_values[-1]) + 1))
    ):
        output.append(
            "Mask is neither a boolean mask nor a numeric mask with integer values."
        )

    return output


def _EncodedMask(mask: array_t, /) -> bytes:
    """
    mask: boolean array
    """
    if any(mask):
        # --- Run lengths
        n_elements = mask.size
        jumps = nmpy.diff(mask)
        jump_idc = nmpy.nonzero(jumps)[0]
        if jump_idc.size > 1:
            run_lengths = (
                [jump_idc[0] + 1]
                + nmpy.diff(jump_idc).tolist()
                + [n_elements - jump_idc[-1] - 1]
            )
        elif jump_idc.size > 0:
            run_lengths = (jump_idc[0] + 1, n_elements - jump_idc[0] - 1)
        else:
            run_lengths = (n_elements,)
        encoded = _EncodedIntegers(run_lengths)

        # --- First value indicator
        if mask[0]:  # First value is "True"
            first_value = b"1"
        else:
            first_value = b"0"

        return first_value + lenc.u.encode(encoded.__len__()) + encoded
    else:
        return b"2"  # Fake first value.


def _EncodedIntegers(integers: h.Sequence[int], /) -> bytes:
    """"""
    return b"".join(map(lenc.u.encode, integers))


def _DecodedIntegers(
    encoded: bytes, /, *, next_reading_idx: int = 0, n_integers: int = None
) -> h.Sequence[int] | tuple[int | h.Sequence[int], int]:
    """"""
    integers = []

    while next_reading_idx < encoded.__len__():
        until_idx = next_reading_idx
        # TODO: Document the loop below.
        while encoded[until_idx] & 0b10000000 > 0:
            until_idx += 1
        past_until = until_idx + 1

        piece = encoded[next_reading_idx:past_until]
        integers.append(lenc.u.decode(piece))

        next_reading_idx = past_until

        if integers.__len__() == n_integers:
            if n_integers > 1:
                return integers, next_reading_idx
            else:
                return integers[0], next_reading_idx

    return integers
