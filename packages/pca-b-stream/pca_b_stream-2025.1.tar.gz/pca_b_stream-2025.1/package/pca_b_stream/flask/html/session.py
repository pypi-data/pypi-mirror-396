"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dominate.tags as html
from pca_b_stream.flask.session.session import session_t
from si_fi_o.path.html import URLOfPath

_LEGEND = {
    "m": "Max. value in array (= number of sub-streams)",
    "c": "Compressed",
    "e": "Byte order (a.k.a. endianness)",
    "t": "dtype code",
    "T": "dtype name",
    "o": "Enumeration order",
    "v": "First value per sub-stream (0: 0 or False, 1: non-zero or True)",
    "d": "Array dimension",
    "l": "Lengths per dimension",
}


def SessionInputsAsHTML(_: session_t | None, __: str, /) -> html.html_tag:
    """"""
    return html.div(_class="container")


def SessionOutputsAsHTML(session: session_t, /) -> html.html_tag | None:
    """
    Needs to be kept in sync with processing.py since it assigns the outputs
    """
    if (outputs := session.outputs) is None:
        return None

    (stream, stream_size, details, high_contrast_name) = (
        outputs  # This is where syncing matters
    )
    if stream is None:
        stream = session["stream"]
        path = session.outputs_path
        name = "Decoded Stream"
    else:
        path = session["array"].server_path
        name = session["array"].client_name
    if high_contrast_name is None:
        high_contrast_path = path
    else:
        high_contrast_path = session.additional_paths[high_contrast_name]

    if path is None:
        figure = html.p("Decoding Error: Invalid Byte-Stream Representation")
        array_size = ""
    else:
        figure = html.figure(
            html.img(src=URLOfPath(high_contrast_path)),
            html.figcaption(
                html.i(f"{name} (do not download; contrast-enhanced version)")
            ),
        )
        array_size = path.stat().st_size

    output = html.div()
    with output:
        with html.table(style="margin-bottom:1em"):
            with html.tr():
                html.td(
                    html.div(
                        html.pre(stream),
                        style="margin-right:2em; width:50em; overflow:auto",
                    )
                )
                html.td(f"Stream length: {stream_size}")
            with html.tr():
                html.td(figure)
                html.td(f"Filesize: {array_size}")
        with html.table(border="1px", style="margin-bottom:1em"):
            with html.tr():
                for key in details.keys():
                    html.th(_LEGEND[key], style="width:10em; padding-left:1em; padding-right:1em; overflow:auto")
            with html.tr():
                for key, value in details.items():
                    if key in ("c", "v"):
                        html.td(html.div(value), _class="align_center")
                    elif key == "l":
                        html.td(
                            str(value)[1:-1].replace(",", " x"), _class="align_center"
                        )
                    else:
                        html.td(value, _class="align_center")

    return output
