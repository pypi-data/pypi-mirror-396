..
   SEE COPYRIGHT and LICENCE NOTICES: files README-COPYRIGHT-utf8.txt and
   README-LICENCE-utf8.txt at project source root.

.. |PROJECT_NAME|      replace:: PCA-B-Stream
.. |SHORT_DESCRIPTION| replace:: Byte Stream Representation of Piecewise-Constant Array

.. |PYPI_NAME_LITERAL| replace:: ``pca-b-stream``
.. |PYPI_PROJECT_URL|  replace:: https://pypi.org/project/pca-b-stream/
.. _PYPI_PROJECT_URL:  https://pypi.org/project/pca-b-stream/

.. |DOCUMENTATION_URL| replace:: https://??MISSING_REPOSITORY_SITE??/??MISSING_REPOSITORY_USER??/??MISSING_REPOSITORY_NAME??/-/wikis/home
.. _DOCUMENTATION_URL: https://??MISSING_REPOSITORY_SITE??/??MISSING_REPOSITORY_USER??/??MISSING_REPOSITORY_NAME??/-/wikis/home

.. |DEPENDENCIES_MANDATORY| replace:: dominate, flask, flask-bootstrap4, flask-session, flask-uploads, flask-wtf, imageio, leb128, numpy, si-fi-o, tqdm, wtforms
.. |DEPENDENCIES_OPTIONAL|  replace:: None



===================================
|PROJECT_NAME|: |SHORT_DESCRIPTION|
===================================



Documentation
=============

The documentation is available below.



Installation
============

.. A Web app of |PROJECT_NAME| might be available on `PythonAnywhere <https://ericdbv.eu.pythonanywhere.com>`_.

This project is published
on the `Python Package Index (PyPI) <https://pypi.org/>`_
at: |PYPI_PROJECT_URL|_.
It should be installable from Python distribution platforms or Integrated Development Environments (IDEs).
Otherwise, it can be installed from a command console using `pip <https://pip.pypa.io/>`_:

+--------------+-------------------------------------------------------+----------------------------------------------------------+
|              | For all users (after acquiring administrative rights) | For the current user (no administrative rights required) |
+==============+=======================================================+==========================================================+
| Installation | ``pip install`` |PYPI_NAME_LITERAL|                   | ``pip install --user`` |PYPI_NAME_LITERAL|               |
+--------------+-------------------------------------------------------+----------------------------------------------------------+
| Update       | ``pip install --upgrade`` |PYPI_NAME_LITERAL|         | ``pip install --user --upgrade`` |PYPI_NAME_LITERAL|     |
+--------------+-------------------------------------------------------+----------------------------------------------------------+



Brief Description
=================

In a Few Words
--------------

The ``PCA-B-Stream`` project allows to generate a printable `byte stream <https://docs.python.org/3/library/stdtypes.html#bytes-objects>`_ representation of a piecewise-constant `Numpy array <https://numpy.org/devdocs/reference/generated/numpy.ndarray.html>`_, and to re-create the array from the byte stream, similarly to what is available as part of the `COCO API <https://github.com/cocodataset/cocoapi>`_.



Illustration
------------

In Python:

.. code-block:: python

    >>> import pca_b_stream as pcas
    >>> import numpy as nmpy
    >>> # --- Array creation
    >>> array = nmpy.zeros((10, 10), dtype=nmpy.uint8)
    >>> array[1, 1] = 1
    >>> # --- Array -> Byte stream -> Array
    >>> stream = pcas.PCA2BStream(array)
    >>> decoding = pcas.BStream2PCA(stream)
    >>> # --- Check and print
    >>> assert nmpy.array_equal(decoding, array)
    >>> print(stream)
    b'FnmHoFain+3jtU'

From command line:

.. code-block:: sh

    pca2bstream some_image_file           # Prints the corresponding byte stream
    bstream2pca a_byte_stream a_filename  # Creates an image from the byte stream and stores it



.. _sct_motivations:

Motivations
===========

The motivations for developing an alternative to existing solutions are:

- Arrays can be of any dimension (i.e., not just 2-dimensional),
- Their `dtype <https://numpy.org/devdocs/reference/generated/numpy.dtype.html>`_ can be of boolean, integer, or float types,
- They can contain more than 2 distinct values (i.e., non-binary arrays) as long as the values are integers (potentially stored in a floating-point format though),
- The byte stream representation is self-contained; In particular, there is no need to keep track of the array shape externally,
- The byte stream representation contains everything needed to re-create the array *exactly* as it was instantiated (``dtype``, endianness, C or Fortran ordering); See `note <note_on_exact_>`_ though.


.. _note_on_exact:

.. note::
    The statement "re-create the array *exactly* as it was instantiated" is over-confident. First this has not been fully tested by, for example, re-creating an array on a another machine with a native endianness different from the one it was originally instantiated on. Second, more work might be required to ensure that enumeration ordering is correctly dealt with.



Documentation
=============

Functions
---------

The ``pca_b_stream`` module defines the following functions:

- ``PCA2BStream``
    - Generates the byte stream representation of an array; Optionally checks the array validity (see ``PCArrayIssues``)
    - Input: a `Numpy ndarray <https://numpy.org/devdocs/reference/generated/numpy.ndarray.html>`_, and an optional ``should_check_mask`` argument
    - Output: an object of type `bytes <https://docs.python.org/3/library/stdtypes.html#bytes-objects>`_
- ``BStream2PCA``
    - Re-creates the array from its bytes stream representation; Does not check the stream format validity
    - Input/Output: input and output of ``PCA2BStream`` swapped
- ``PCArrayIssues``
    - Checks whether an array is a valid input for stream representation generation; It is meant to be used before calling ``PCA2BStream``
    - Input: a `Numpy ndarray <https://numpy.org/devdocs/reference/generated/numpy.ndarray.html>`_
    - Output: a tuple issues in ``str`` format. The tuple is empty if the array is valid.
    - Additional information about what are valid piecewise-constant arrays here is provided in the section `"Motivations" <sct_motivations_>`_.
- ``BStreamDetails``
    - Extract details from a byte stream representation; See section `"Byte Stream Format" <byte_stream_format_>`_
    - Inputs:
        - a byte stream generated by ``PCA2BStream``
        - details: a string where each character corresponds to a detail to extract, or "+" to extract all of the available details; Default: "+"; Available details are:
            - c: compression indicator
            - d: array dimension
            - l: array lengths per dimension
            - t: dtype type code; See: https://numpy.org/doc/stable/reference/generated/numpy.dtype.char.html
            - T: dtype name; Translated from "t" by Numpy.sctypeDict
            - o: enumeration order; See: https://numpy.org/doc/stable/reference/generated/numpy.ndarray.flags.html, ?_CONTIGUOUS
            - e: endianness (or byte order); See: https://numpy.org/doc/stable/reference/generated/numpy.dtype.byteorder.html
        - should_print: a boolean to instruct whether the extracted details should be printed to console; Defaults: False
        - should_return: a boolean to instruct whether the extracted details should be returned (see Outputs); Defaults: True
    - Output: either one of:
        - None if should_return is False
        - a dictionary of all of the available details if the ``details`` parameter is "+"
        - a tuple of the requested details in the same order as in the ``details`` parameter



Command Line Scripts
--------------------

The ``PCA-B-Stream`` project defines two command line scripts: ``pca2bstream`` and ``bstream2pca``. The former takes a path to an image file as argument, and prints the corresponding byte stream (without the "b" string type prefix). The latter takes a character string and a filename as arguments, in that order, and creates an image file with this name that corresponds to the string interpreted as a byte stream. The file must not already exist.



.. _byte_stream_format:

Byte Stream Format
------------------

A byte stream is a `base85-encoded <https://docs.python.org/3/library/base64.html#base64.b85encode>`_ stream. Once decoded, it has the following format (in lexicographical order; all characters are in ``bytes`` format):

- one character "0" or "1": indicates whether the remaining of the stream is in uncompressed or `ZLIB compressed <https://docs.python.org/3/library/zlib.html#zlib.compress>`_ format; See `note on compression <note_on_compression_>`_; The remaining of the description applies to the stream in uncompressed format
- 3 characters "{E}{T}{O}":
    - E: endianness among "|", "<" and ">"
    - T: ``dtype`` character code among: "?" + numpy.typecodes["AllInteger"] + numpy.typecodes["Float"]
    - O: enumeration order among "C" (C-ordering) and "F" (Fortran-ordering)
- one integer for the dimension of the array (1 for vectors, 2 for matrices, 3 for volumes...)
- one integer per dimension giving the length of the array in that dimension

The remaining of the stream is the actual array content.

- If the array is not all False's or zeros:
    - one character "0" or "1": whether the first value in the array is zero (or False) or one (or True)
    - one integer for the length of the run-length representation
    - integers of the `run-length representation <https://en.wikipedia.org/wiki/Run-length_encoding>`_ of the array read in its proper enumeration order
- If the array is all False's or zeros:
    - one character "2"

All the integers are encoded by the `unsigned LEB128 encoding <https://en.wikipedia.org/wiki/LEB128#Unsigned_LEB128>`_ using the `leb128 project <https://github.com/mohanson/leb128>`_.

For non-boolean arrays with a maximum value of 2 or more, the content part is the concatenation of the sub-contents corresponding to each value between 1 and the maximum value in the array.


.. _note_on_compression:

.. note::
    For small arrays, compressing the byte stream actually produces a longer stream.



Dependencies
============

The development relies on several packages:

- Mandatory: |DEPENDENCIES_MANDATORY|
- Optional:  |DEPENDENCIES_OPTIONAL|

The mandatory dependencies, if any, are installed automatically by `pip <https://pip.pypa.io/>`_, if they are not already, as part of the installation of |PROJECT_NAME|.
Python distribution platforms or Integrated Development Environments (IDEs) should also take care of this.
The optional dependencies, if any, must be installed independently by following the related instructions, for added functionalities of |PROJECT_NAME|.



Acknowledgments
===============

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. image:: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
    :target: https://pycqa.github.io/isort/

The project is developed with `PyCharm Community <https://www.jetbrains.com/pycharm/>`_.

The code is formatted by `Black <https://github.com/psf/black/>`_, *The Uncompromising Code Formatter*.

The imports are ordered by `isort <https://github.com/timothycrosley/isort/>`_... *your imports, so you don't have to*.
