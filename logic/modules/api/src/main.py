#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.server.http.server_fastapi import Server
import sys


def main():
    try:
        Server().run()
    except KeyboardInterrupt:
        return True
    except Exception as e:
        sys.stderr.write("Exception running server: {}\n".format(e))
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
