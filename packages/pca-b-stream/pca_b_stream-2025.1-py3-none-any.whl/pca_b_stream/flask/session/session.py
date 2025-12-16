"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

from pca_b_stream.flask.session.form import form_t
from si_fi_o.session.form import file_t
from si_fi_o.session.session import session_t as base_session_t


class session_t(base_session_t):
    # additional_paths: list[path_t] | None = None
    #
    # def DeleteOutputsFile(self) -> None:
    #     """"""
    #     super().DeleteOutputsFile()
    #
    #     if self.additional_paths is not None:
    #         for path in self.additional_paths:
    #             if path.is_file():
    #                 path.unlink()
    #         self.additional_paths = None

    def IsComplete(self, *, form: form_t = None) -> bool:
        """"""
        # Do not use self[_key] below since reference and/or detection files are missing if the form has been submitted
        # without these files (they are not required fields since the session can supply them) and the session has not
        # received these files yet, e.g. on the first run if not selecting these files.
        if form_t.RequestedToByteStream():
            return isinstance(self.get("array"), file_t)

        return self["stream"].__len__() > 0
