SimpleFTPServer
===============

TODO

To serve your local filesystem:

    pip install simpleftpserver
    python -m simpleftpserver

To serve an AWS S3 or Google GCS bucket:

    pip install simpleftpserver gcsfs
    python -m simpleftpserver gcs://bucket_name/


Highlights
----------

 * Can be backed with [PyFilesystem2](https://www.pyfilesystem.org/)
   filesystems
 * Does not use OS specific calls, so no fork or setuid is used
 * Does not support authentication
 * Made for educational purposes
 * Not optimized for speed or memory usage
 * Optimized for extensibility


Requirements
------------

Python >= 3.6 TODO


Notes
-----

I had problems with gcsfs, so included a patched version in this repository. It
can be accessed via `python -m simpleftpserver gcs-patched://bucket_name/` urls. 


TODOs
-----

 * Release to PyPI
 * Implement IPv6 extensions by rfc2428
 * Implement more extensions from rfc3659 like mdmt etc...
