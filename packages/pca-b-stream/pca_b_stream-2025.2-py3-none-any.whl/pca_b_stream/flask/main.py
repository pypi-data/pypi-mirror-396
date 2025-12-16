"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from flask import Flask as flask_app_t
from pca_b_stream.flask.html.constants import ABOUT, MAX_IMAGE_SIZE, NAME_MEANING
from pca_b_stream.flask.html.session import SessionInputsAsHTML, SessionOutputsAsHTML
from pca_b_stream.flask.session.constants import APP_NAME, PROJECT_NAME
from pca_b_stream.flask.session.form import form_t
from pca_b_stream.flask.session.processing import ProcessSession
from pca_b_stream.flask.session.session import session_t
from si_fi_o.app import ConfigureApp

HTML_FOLDER = "html"
HOME_PAGE_DETAILS = {
    "html_template": "main.html",
    "name": PROJECT_NAME,
    "name_meaning": NAME_MEANING,
    "about": ABOUT,
    "SessionInputsAsHTML": SessionInputsAsHTML,
    "max_file_size": MAX_IMAGE_SIZE,
    "SessionOutputsAsHTML": SessionOutputsAsHTML,
}


app = flask_app_t(__name__, template_folder=HTML_FOLDER)
ConfigureApp(
    app, HOME_PAGE_DETAILS, form_t, session_t, MAX_IMAGE_SIZE, ProcessSession, APP_NAME
)


if __name__ == "__main__":
    #
    print(
        "####\n"
        "#### Open the http address that appears below "
        "(usually http://127.0.0.1:5000)\n"
        "#### in a web browser to start using PCA-B-Stream\n"
        "####"
    )
    app.run()
