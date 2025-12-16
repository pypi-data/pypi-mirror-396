"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import typing as h

import imageio as mgio
import numpy as nmpy
import pca_b_stream.main as pcas
from pca_b_stream.flask.session.form import form_t
from pca_b_stream.flask.session.session import session_t
from si_fi_o.session.session import file_output_t

output_types_h = tuple[
    tuple[h.Any, ...], tuple[file_output_t, ...] | None, str | tuple[str] | None
]


def ProcessSession(session: session_t, /) -> output_types_h:
    """"""
    if form_t.RequestedToByteStream():
        return _ToSTR(session)
    else:
        return _ToARY(session)


def _ToSTR(session: session_t, /) -> output_types_h:
    """"""
    image = mgio.v3.imread(session["array"].server_path)
    issues = pcas.PCArrayIssues(image)
    if issues.__len__() == 0:
        stream = pcas.PCA2BStream(image)
        length = stream.__len__()
        details = pcas.BStreamDetails(stream)
        stream = stream.decode("ascii")
    else:
        issues = "\n    ".join(issues)
        stream = f"Invalid Piecewise-Constant Array:\n    {issues}"
        length = -1
        details = None

    high_contrast = nmpy.around(255.0 * (image / nmpy.amax(image))).astype(nmpy.uint8)
    high_contrast_name = "image-high-contrast.png"
    file_output = file_output_t(
        name=high_contrast_name, contents=high_contrast, Write=mgio.imwrite
    )

    return (stream, length, details, high_contrast_name), (file_output,), None


def _ToARY(session: session_t, /) -> output_types_h:
    """"""
    stream = bytes(session["stream"], "ascii")
    length = stream.__len__()

    try:
        decoded = pcas.BStream2PCA(stream)
    except:
        decoded = None

    if decoded is None:
        return (None, length, None, None), None, None

    high_contrast = nmpy.around(255.0 * (decoded / nmpy.amax(decoded))).astype(
        nmpy.uint8
    )
    details = pcas.BStreamDetails(stream)

    file_output_1 = file_output_t(
        name="decoded.png", contents=decoded, Write=mgio.imwrite
    )
    high_contrast_name = "decoded-high-contrast.png"
    file_output_2 = file_output_t(
        name=high_contrast_name, contents=high_contrast, Write=mgio.imwrite
    )

    return (
        (None, length, details, high_contrast_name),
        (file_output_1, file_output_2),
        "decoded.png",
    )
