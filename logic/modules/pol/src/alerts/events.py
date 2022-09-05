#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.config.parser.fullparser import FullConfParser
from common.db.manager import DBManager
import requests
import time
import pymongo


db_manager = DBManager()
myclient = pymongo.MongoClient(
    "mongodb://{}:{}".format(db_manager.host, db_manager.port)
)
db_pol = myclient[db_manager.db_name]
db_mon = myclient["mon"]
alert_register = db_pol["alert_register"]
alerts_metrics = db_mon["alerts_metrics"]


class Events:
    """
    Defining specific event depending on the metric monitoring
    """

    def parse_config(self):
        parser = FullConfParser()
        pol = parser.get("pol.yaml")
        alerts = pol.get("alerts")
        monitoring = alerts.get("monitoring")
        self.scrape_interval = monitoring.get("scrape_interval")

    def events(self, request):
        self.parse_config()
        request_body = request.json
        self.alert_name = request_body.get("alert-name")
        self.metric_name = request_body.get("metric-name")

        alert_name_list = []
        for name in alert_register.find():
            names = name["alert_name"]
            alert_name_list.append(names)

        if self.alert_name in alert_name_list:
            start_time = time.time()
            monitoring_period = self.scrape_interval

            while True:
                self.retrive_alert_data()
                operator = self.alert_data["operator"]
                threshold = self.alert_data["threshold"]
                time_validity = self.alert_data["time-validity"]
                hook_type = self.alert_data["hook-type"]
                hook_endpoint = self.alert_data["hook-endpoint"]

                self.retrive_alert_metric_data()
                vnf_id = self.alert_metric_data["vnf-id"]
                data = int(self.alert_metric_data["data"])

                if (eval("{} {} {}".format(data, operator, threshold))) == True:
                    webhook = {
                        "vnf-id": vnf_id,
                        "metric-name": self.metric_name,
                        "threshold": threshold,
                        "data": data,
                        "alert-name": self.alert_name,
                    }
                    requests.post(
                        hook_endpoint, "", webhook
                    )
                    print("{}. Sending alarm to {}".format(vnf_id, hook_type))
                else:
                    print("monitoring...{}".format(vnf_id))
                sleep_time = monitoring_period - (
                    (time.time() - start_time) % monitoring_period
                )
                time.sleep(sleep_time)

        else:
            return "Alert is not registered"

    def retrive_alert_data(self):
        for i in alert_register.find({"alert_name": self.alert_name}):
            self.alert_data = {
                "alert-name": "",
                "threshold": "",
                "operator": "",
                "time-validity": "",
                "hook-type": "",
                "hook-endpoint": "",
            }
            self.alert_data["alert-name"] = i["alert_name"]
            self.alert_data["threshold"] = i["threshold"]
            self.alert_data["operator"] = i["operator"]
            self.alert_data["time-validity"] = i["time_validity"]
            self.alert_data["hook-type"] = i["hook_type"]
            self.alert_data["hook-endpoint"] = i["hook_endpoint"]

    def retrive_alert_metric_data(self):
        self.alert_metric_data_list = []
        for i in alerts_metrics.find({"metric_name": self.metric_name}):
            self.alert_metric_data = {
                "vnf-id": "",
                "metric-name": "",
                "metric-command": "",
                "data": "",
            }
            self.alert_metric_data["vnf-id"] = i["vnf_id"]
            self.alert_metric_data["metric-name"] = i["metric_name"]
            self.alert_metric_data["metric-command"] = i["metric_command"]
            self.alert_metric_data["data"] = i["data"]
            self.alert_metric_data_list.append(self.alert_metric_data)
        return self.alert_metric_data_list
