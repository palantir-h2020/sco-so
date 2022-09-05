#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.db.models.alerts.alerts_registration import AlertRegister
from datetime import datetime
from common.db.manager import DBManager
import pymongo

db_manager = DBManager()
myclient = pymongo.MongoClient(
    "mongodb://{}:{}".format(db_manager.host, db_manager.port)
)
db = myclient[db_manager.db_name]
alert_register = db["alert_register"]


class AlertsRegister():
    """
    Alert registration 
    """
    def retrieve_json_body(self, request) -> None:
        request_body = request.json
        self.alert_name = request_body.get("alert-name")
        self.threshold = request_body.get("threshold")
        self.operator = request_body.get("operator")
        self.time_validity = request_body.get("time-validity")
        self.hook_type = request_body.get("hook-type")
        self.hook_endpoint = request_body.get("hook-endpoint")
        self.operator_list = ["==", "<", ">", "<=", ">="]
        pass

    def registration(self, request):
        self.retrieve_json_body(request)       
        if request.method == "POST":
            try:
                alert_name_list = []
                for name in alert_register.find():
                    names = name["alert_name"]
                    alert_name_list.append(names)

                if self.alert_name in alert_name_list:
                    return "Alert name is already registered, use other name"
                else:
                    if self.operator in self.operator_list:
                        self.mongodb_alert_registration()
                        return "OK"
                    else:
                        return "Operator must be: <, ==, >, <=, >="
            except:
                if self.operator in self.operator_list:
                    self.mongodb_alert_registration()
                    return "OK"
                else:
                    return "Operator must be: <, ==, >, <=, >="

        elif request.method == "PUT":
            alert_register.update_one({}, {"$set": {"alert-name": "list"}})
            return "PUT"

        elif request.method == "DELETE":
            alert_register.delete_one({"alert-name": "__so_pol__example"})
            return "Delete"

    def mongodb_alert_registration(self):
        alert_register = AlertRegister()
        alert_register.alert_name = self.alert_name
        alert_register.threshold = self.threshold
        alert_register.operator = self.operator
        alert_register.time_validity = self.time_validity
        alert_register.hook_type = self.hook_type
        alert_register.hook_endpoint = self.hook_endpoint
        alert_register.date = datetime.now()
        alert_register.save()
