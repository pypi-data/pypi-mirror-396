"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import dominate.tags as html
from pca_b_stream.flask.session.constants import PROJECT_NAME

NAME_MEANING = "Byte Stream Representation of Piecewise-Constant Array"
SHORT_DESCRIPTION = (
    "Generation of a printable byte stream representation of a piecewise-constant Numpy array, "
    "and re-creation of the array from the byte stream."
)

ABOUT = html.div(
    html.h4("Purpose"),
    html.p(SHORT_DESCRIPTION),
    #
    html.h4("Privacy"),
    html.p(
        f"""
            Uploaded inputs are stored on the server for the sole processing by {PROJECT_NAME}.
            All data, uploaded, intermediate and final, can be deleted manually through a dedicated button
            that appears on processing completion.
            If not deleted manually, all data are automatically deleted based on their timestamp
            by a process running several times a day.
        """
    ),
    #
    html.h4("Links"),
    html.ul(
        html.li(
            html.a(
                "Documentation",
                href="https://gitlab.inria.fr/edebreuv/pca-b-stream/-/blob/master/README.rst",
            )
        ),
        html.li(
            html.a(
                "Source code (Gitlab repository)",
                href="https://gitlab.inria.fr/edebreuv/pca-b-stream/",
            )
        ),
        html.li(
            html.a(
                "Python Package Index (PyPI) page",
                href="https://pypi.org/project/pca-b-stream/",
            )
        ),
    ),
)

MAX_IMAGE_SIZE = 256  # MB
