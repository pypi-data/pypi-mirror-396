"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import wtforms as wtfm
from flask import request as flask_request
from si_fi_o.session.form import form_t as base_form_t

_TO_BYTE_STREAM = "to byte stream"
_TO_ARRAY = "to array"


class form_t(base_form_t):
    """"""

    array = wtfm.FileField(label="Piecewise-Constant Array")
    stream = wtfm.TextAreaField(label="Byte Stream", render_kw={"cols": 75, "rows": 3})
    submit_to_str = wtfm.SubmitField(
        label="Convert to Byte Stream", name=_TO_BYTE_STREAM
    )
    submit_to_ary = wtfm.SubmitField(
        label="Convert to Piecewise-Constant Array", name=_TO_ARRAY
    )

    @staticmethod
    def RequestedToByteStream() -> bool:
        """"""
        # FIXME: Find a better way to guess targeted conversion
        return _TO_BYTE_STREAM in flask_request.form
