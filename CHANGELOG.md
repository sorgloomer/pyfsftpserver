Changelog - pyfsftpserver
=========================


NEXT
------------------

### Bugfixes

 * Previous version reported it handles UTF-8, but it didn't. Changed default encoding to UTF-8.


v0.1.0 - 2020.12.04
------------------

### Features

 * implemented EPSV

### Bugfixes

 * fixed PASV - previously it responded with the server sockets listening interface (which can be 0.0.0.0), now it responds with the ip address of the socket of the command channel, so at least clients from the local network can connect


v0.0.1 - 2020.09.03
------------------

 * initial release
