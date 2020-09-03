from simpleftpserver.server import main

from simpleftpserver.with_pyfs.server import PyfsFtpServer

__all__ = ["PyfsFtpServer", "main"]

if __name__ == "__main__":
    main()
