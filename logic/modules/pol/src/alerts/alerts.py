#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.db.manager import DBManager
import pymongo


db_manager = DBManager()
myclient = pymongo.MongoClient(
    "mongodb://{}:{}".format(db_manager.host, db_manager.port)
)
db = myclient[db_manager.db_name]
alert_register = db["alert_register"]

class Alerts():
    """
    Retrieve list of registered alerts
    """
    def retrieve_registered_alerts(self):
        mongo_list = []
        for i in alert_register.find():
            mongo_dict = {
                "alert-name": "",
                "threshold": "",
                "operator": "",
                "time-validity": "",
                "hook-type": "",
                "hook-endpoint": "",
                }
            mongo_dict["alert-name"] = i["alert_name"]
            mongo_dict["threshold"] = i["threshold"]
            mongo_dict["operator"] = i["operator"]
            mongo_dict["time-validity"] = i["time_validity"]
            mongo_dict["hook-type"] = i["hook_type"]
            mongo_dict["hook-endpoint"] = i["hook_endpoint"]
            mongo_list.append(mongo_dict)
        return mongo_list
