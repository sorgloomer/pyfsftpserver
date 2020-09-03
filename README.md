pyfsftpserver
=============

![License](https://img.shields.io/badge/License-MIT-blue.svg)


A simple FTP server for serving PyFilesystem2 filesystems.

Serve the current directory on your local filesystem over FTP:

    pip install pyfsftpserver
    python -m pyfsftpserver

Serve an AWS S3 or Google GCS bucket:

    pip install pyfsftpserver gcsfs
    python -m pyfsftpserver gcs://bucket_name/


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

Python >= 3.6


Notes
-----

I had problems with gcsfs, so included a patched version in this repository. It
can be accessed via `python -m pyfsftpserver gcs-patched://bucket_name/` urls.


Sources
-------

https://github.com/sorgloomer/pyfsftpserver


Changelog
-------

https://github.com/sorgloomer/pyfsftpserver/blob/master/CHANGELOG.md


TODOs
-----

 * Release to PyPI
 * Implement IPv6 extensions by rfc2428
 * Implement more extensions from rfc3659 like mdmt etc...

License
-------

MIT
