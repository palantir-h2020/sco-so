#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

#from common.config.parser.fullparser import FullConfParser
from mongoengine import connect, disconnect

#import threading

class MongoConnector():
    """
    Connector to access MongoDB.
    """

    #def __init__(self):
        #self.__mutex = threading.Lock()
        #self.config = FullConfParser()
        #self.db_category = self.config.get("db.yaml")
        #self.db_general = self.db_category.get("general")
        #self.host = self.db_general.get("host")
        #self.port = int(self.db_general.get("port"))
        #self.db_db = self.db_category.get("db")
        #self.db_name = self.db_db.get("name")
    disconnect()
    connect(host="mongodb://so-db:27017/mon")
