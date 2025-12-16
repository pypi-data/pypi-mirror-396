"""
SEE COPYRIGHT, LICENCE, and DOCUMENTATION NOTICES: files
README-COPYRIGHT-utf8.txt, README-LICENCE-utf8.txt, and README-DOCUMENTATION-utf8.txt
at project source root.
"""

import re as rgex
from importlib import util
from pathlib import Path as path_t

from setuptools import find_namespace_packages, setup

HERE = path_t(__file__).parent.resolve()


def DescriptionFromAsciidoc() -> dict[str, str]:
    """"""
    output = {}

    where = HERE / "documentation" / "wiki" / "description.asciidoc"
    pattern = rgex.compile(r":([A-Z_]+): +(.+)\n?", flags=rgex.ASCII)

    with open(where) as accessor:
        for line in accessor.readlines():
            if (match := pattern.fullmatch(line)) is not None:
                name = match.group(1)
                value = match.group(2)
                output[name] = value

    return output


DESCRIPTION = DescriptionFromAsciidoc()
ENTRY_POINTS = {
    "console_scripts": [
        f"pca2bstream={DESCRIPTION['IMPORT_NAME']}.cli:PCA2BStream",
        f"bstream2pca={DESCRIPTION['IMPORT_NAME']}.cli:BStream2PCA",
    ],
    "gui_scripts": [],
}


long_description = (HERE / "README.rst").read_text(encoding="utf-8")

repository_url = (
    f"https://"
    f"{DESCRIPTION['REPOSITORY_SITE']}/"
    f"{DESCRIPTION['REPOSITORY_USER']}/"
    f"{DESCRIPTION['REPOSITORY_NAME']}/"
)
documentation_url = repository_url


def Version() -> str:
    """"""
    where = HERE / "package" / DESCRIPTION["IMPORT_NAME"] / "version.py"
    spec = util.spec_from_file_location(where.stem, where)
    module = spec.loader.load_module(spec.name)

    output = module.__version__
    if isinstance(output, str) and rgex.fullmatch(r"20[0-9]{2}\.[1-9][0-9]*", output):
        return output

    raise ValueError(f"{output}: Invalid version.")


def Requirements() -> tuple[str, ...]:
    """"""
    if not (HERE / "requirements.txt").is_file():
        return ()

    with open(HERE / "requirements.txt") as accessor:
        output = accessor.readlines()

    return tuple(output)


if __name__ == "__main__":
    #
    # fmt: off
    setup(
        author=DESCRIPTION["AUTHOR"],
        author_email=DESCRIPTION["EMAIL"],
        #
        name=DESCRIPTION["PYPI_NAME"],
        description=DESCRIPTION["SHORT_DESCRIPTION"],
        long_description=long_description,
        long_description_content_type="text/x-rst",
        license=DESCRIPTION["LICENSE_SHORT"],
        version=Version(),
        #
        classifiers=[
            f"Topic :: {DESCRIPTION['PYPI_TOPIC']}",
            f"Intended Audience :: {DESCRIPTION['PYPI_AUDIENCE']}",
            f"License :: OSI Approved :: {DESCRIPTION['LICENCE_LONG']} ({DESCRIPTION['LICENSE_SHORT']})",
            f"Programming Language :: Python :: {DESCRIPTION['PY_VERSION_MAJOR']}",
            f"Development Status :: {DESCRIPTION['PYPI_STATUS']}",
        ],
        keywords=DESCRIPTION["KEYWORDS"],
        #
        url=repository_url,
        project_urls={
            "Documentation": documentation_url,
            "Source": repository_url,
        },
        #
        packages=find_namespace_packages(where="package"),
        package_dir={"": "package"},
        package_data = {
            DESCRIPTION["IMPORT_NAME"]: [
                "flask/html/main.html",
                "flask/static/main.css",
            ],
        },
        entry_points=ENTRY_POINTS,
        python_requires=f">={DESCRIPTION['PY_VERSION_MIN']}",
        install_requires=Requirements(),
    )
