#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.config.parser.fullparser import FullConfParser
from common.db.manager import DBManager
from common.db.models.prometheus_targets import PrometheusTargets
import pymongo
import requests


db_manager = DBManager()
myclient = pymongo.MongoClient(
    "mongodb://{}:{}".format(db_manager.host, db_manager.port)
)
db = myclient[db_manager.db_name]
custom_metrics = db["custom_metrics"]

class Metrics:
    """
    Base class to retrieve all metrics from the Prometheus node exporter and DB.
    """

    def parser_config(self):
        self.general_conf = FullConfParser()
        self.mon_conf = self.general_conf.get("mon.yaml")
        self.mon_category = self.mon_conf.get("prometheus")
        self.mon_subcategory = self.mon_category.get("exporter")
        self.protocol = self.mon_subcategory.get("protocol")
        self.query_endpoint = self.mon_subcategory.get("query_endpoint")

    def retrieve_targets_list(self):
        self.targets_list = PrometheusTargets.objects.order_by("-id")\
                            .first().targets
        return self.targets_list

    def exporter_metrics(self, xnf_id, metric_name):
        self.retrieve_targets_list()
        self.parser_config()
        if (xnf_id is None) and (metric_name is None):
            metrics_list = []
            for target in self.targets_list:
                exporter_data = requests.get(
                    "{}://{}/{}".format(
                        self.protocol, target, self.query_endpoint)
                )
                exporter_data_text = exporter_data.text
                metrics_list.append(exporter_data_text)
            return metrics_list
        else:
            if metric_name is None:
                if xnf_id in self.targets_list:
                    exporter_data = requests.get(
                        "{}://{}/{}".format(
                            self.protocol, xnf_id, self.query_endpoint)
                    )
                    exporter_data_text = exporter_data.text
                    return exporter_data_text
                else:
                    return "{} Target is not registered".format(xnf_id)
            else:
                if xnf_id is None:
                    return ""
                else:
                    if xnf_id in self.targets_list:
                        exporter_data = requests.get(
                            "{}://{}/{}".format(
                                self.protocol, xnf_id, self.query_endpoint)
                        )
                        exporter_data_text = exporter_data.text
                        return exporter_data_text
                    else:
                        return "{} Target is not registered".format(xnf_id)

    def mongodb_metrics(self, xnf_id, metric_name):
        if (xnf_id is None) and (metric_name is None):
            try:
                mongo_list = []
                for target in self.targets_list:
                    for i in custom_metrics.find({"xnf_id": target}):
                        mongo_dict = {
                            "xnf-id": "",
                            "metric-name": "",
                            "metric-command": "",
                            "data": "",
                        }
                        mongo_dict["xnf-id"] = i["xnf_id"]
                        mongo_dict["metric-name"] = i["metric_name"]
                        mongo_dict["metric-command"] = i["metric_command"]
                        mongo_dict["data"] = i["data"]
                        mongo_list.append(mongo_dict)
                return mongo_list
            except Exception:
                return "{} {}".format(
                        "An error ocurred with your request.",
                        "Check your MongoDB connection")
        else:
            if metric_name is None:
                if xnf_id in self.targets_list:
                    mongo_list = []
                    for i in custom_metrics.find({"xnf_id": xnf_id}):
                        mongo_dict = {
                            "xnf-id": "",
                            "metric-name": "",
                            "metric-command": "",
                            "data": "",
                        }
                        mongo_dict["xnf-id"] = i["xnf_id"]
                        mongo_dict["metric-name"] = i["metric_name"]
                        mongo_dict["metric-command"] = i["metric_command"]
                        mongo_dict["data"] = i["data"]
                        mongo_list.append(mongo_dict)
                    return mongo_list
                else:
                    return "{} Target is not registered".format(xnf_id)
            else:
                if xnf_id is None:
                    mongo_list = []
                    for i in custom_metrics.find({"metric_name": metric_name}):
                        mongo_dict = {
                            "xnf-id": "",
                            "metric-name": "",
                            "metric-command": "",
                            "data": "",
                        }
                        mongo_dict["xnf-id"] = i["xnf_id"]
                        mongo_dict["metric-name"] = i["metric_name"]
                        mongo_dict["metric-command"] = i["metric_command"]
                        mongo_dict["data"] = i["data"]
                        mongo_list.append(mongo_dict)
                    return mongo_list
                else:
                    if xnf_id in self.targets_list:
                        mongo_list = []
                        for i in custom_metrics.find({
                                "xnf_id": xnf_id,
                                "metric_name": metric_name}):
                            mongo_dict = {
                                "xnf-id": "",
                                "metric-name": "",
                                "metric-command": "",
                                "data": "",
                            }
                            mongo_dict["xnf-id"] = i["xnf_id"]
                            mongo_dict["metric-name"] = i["metric_name"]
                            mongo_dict["metric-command"] = i["metric_command"]
                            mongo_dict["data"] = i["data"]
                            mongo_list.append(mongo_dict)
                        return mongo_list
                    else:
                        return "{} Target is not registered".format(xnf_id)
