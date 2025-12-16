#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from nextnextping.grammer.ttl_parser_worker import TtlPaserWolker


class MyTtlPaserWolker(TtlPaserWolker):
    """ my TtlPaserWolker  """
    def __init__(self):
        super().__init__()

    def setLog(self, strvar):
        """ log setting """
        print(strvar, end="")


def pyttl(argv) -> TtlPaserWolker:
    if len(argv) <= 1:
        print("Usage: python pyttl.py FILE [OPTION]...")
    else:
        ttlPaserWolker = None
        try:
            ttlPaserWolker = MyTtlPaserWolker()
            ttlPaserWolker.execute(argv[1], argv[1:])
        finally:
            if ttlPaserWolker is not None:
                # No matter what, the worker will be killed.
                ttlPaserWolker.stop()
    return ttlPaserWolker


def main():
    pyttl(sys.argv)


if __name__ == "__main__":
    pyttl()
    #
