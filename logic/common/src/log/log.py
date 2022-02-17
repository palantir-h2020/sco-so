#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


import logging
import os
import sys


def setup_custom_logger(name):
    """
    Custom logger
    """
    formatter = logging.Formatter(
        fmt='%(asctime)s %(levelname)-2s {0} %(message)s'.format(name),
        datefmt='%Y-%m-%d %H:%M:%S')
    log_path = "logs/{0}.log".format(name)
    if not os.path.exists("logs"):
        os.makedirs("logs")
    with open(log_path, "w"):
        pass
    handler = logging.FileHandler(log_path, mode="a")
    handler.setFormatter(formatter)
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(screen_handler)
    return logger
