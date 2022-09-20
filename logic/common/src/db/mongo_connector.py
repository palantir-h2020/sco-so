#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from mongoengine import disconnect
# from mongoengine import connect, disconnect
# import threading


class MongoConnector():
    """
    Connector to access MongoDB.
    """

    def __init__(self):
        # self.__mutex = threading.Lock()
        self.config = FullConfParser()
        self.db_category = self.config.get("db.yaml")
        self.db_general = self.db_category.get("general")
        self.host = self.db_general.get("host")
        self.port = int(self.db_general.get("port"))
        self.db_db = self.db_category.get("db")
        self.db_name = self.db_db.get("name")
        self.db_user = self.db_db.get("user")
        self.db_password = self.db_db.get("password")
        # Why is the first disconnect() needed?
        # See: https://stackoverflow.com/questions/67817378/
        # error-you-have-not-defined-a-default-connection-while-connecting-multiple-data
        disconnect()
        # self.db_conn = connect(self.db_name,
        #    alias="default", tz_aware=True,
        #    host=self.host, port=self.port,
        #    username=self.db_user,
        #    password=self.db_password)
        # self.db_conn = connect(host="mongodb://so-{}:{}/mon".format(
        #     self.host, self.port))

    def __del__(self):
        disconnect()
