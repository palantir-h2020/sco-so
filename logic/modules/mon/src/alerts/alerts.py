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
alerts_metrics = db["alerts_metrics"]

class Alerts():
    """
    Retrieve list of registered alerts
    """
    def retrieve_registered_alerts(self, vnf_id, metric_name):
        if (vnf_id is None) and (metric_name is None):
            mongo_list = []
            for i in alerts_metrics.find():
                mongo_dict = {
                    "vnf-id": "",
                    "metric-name": "",
                    "metric-command": "",
                    "data": "",
                    }
                mongo_dict["vnf-id"] = i["vnf_id"]
                mongo_dict["metric-name"] = i["metric_name"]
                mongo_dict["metric-command"] = i["metric_command"]
                mongo_dict["data"] = i["data"]
                mongo_list.append(mongo_dict)
            return mongo_list
        else:
            if metric_name is None:
                mongo_list = []
                for i in alerts_metrics.find({"vnf_id": vnf_id}):
                    mongo_dict = {
                        "vnf-id": "",
                        "metric-name": "",
                        "metric-command": "",
                        "data": "",
                        }
                    mongo_dict["vnf-id"] = i["vnf_id"]
                    mongo_dict["metric-name"] = i["metric_name"]
                    mongo_dict["metric-command"] = i["metric_command"]
                    mongo_dict["data"] = i["data"]
                    mongo_list.append(mongo_dict)
                return mongo_list
            else:
                if vnf_id is None:
                    mongo_list = []
                    for i in alerts_metrics.find({"metric_name": metric_name}):
                        mongo_dict = {
                            "vnf-id": "",
                            "metric-name": "",
                            "metric-command": "",
                            "data": "",
                            }
                        mongo_dict["vnf-id"] = i["vnf_id"]
                        mongo_dict["metric-name"] = i["metric_name"]
                        mongo_dict["metric-command"] = i["metric_command"]
                        mongo_dict["data"] = i["data"]
                        mongo_list.append(mongo_dict)
                    return mongo_list
                else:
                    mongo_list = []
                    for i in alerts_metrics.find({"vnf_id": vnf_id, "metric_name": metric_name}):
                        mongo_dict = {
                            "vnf-id": "",
                            "metric-name": "",
                            "metric-command": "",
                            "data": "",
                            }
                        mongo_dict["vnf-id"] = i["vnf_id"]
                        mongo_dict["metric-name"] = i["metric_name"]
                        mongo_dict["metric-command"] = i["metric_command"]
                        mongo_dict["data"] = i["data"]
                        mongo_list.append(mongo_dict)
                    return mongo_list
