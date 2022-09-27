#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from common.config.parser.fullparser import FullConfParser
from common.db.manager import DBManager
from common.db.models.prometheus_targets import PrometheusTargets
import pymongo
import requests
import time


db_manager = DBManager()
myclient = pymongo.MongoClient(
    "mongodb://{}:{}@{}:{}".format(
        db_manager.user_id, db_manager.user_password,
        db_manager.host, db_manager.port)
)
db = myclient[db_manager.db_name]
custom_metrics = db["custom_metrics"]


class Metrics:
    """
    Base class to retrieve all metrics from the
    Prometheus node exporter and DB.
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

    def _exporter_filter_metrics(self, exp_metrics):
        metrics_list = []
        exp_met_list = exp_metrics.split("\n")
        exp_met_fil_list = list(filter(
            lambda x: not x.startswith("# "),
            exp_met_list))
        for exp_met_item in exp_met_fil_list:
            try:
                exp_met_item_split = exp_met_item.split(" ")
                metrics_list.append({
                    "metric-name": exp_met_item_split[0],
                    "metric-value": exp_met_item_split[1],
                    })
            except Exception:
                pass
        return metrics_list

    def exporter_metrics(self, xnf_id, metric_name):
        self.retrieve_targets_list()
        self.parser_config()
        try:
            # FIXME lots of code are repeated. Please group code and change
            # variables as needed to group code
            # FIXME parenthesis not needed...
            if (xnf_id is None) and (metric_name is None):
                metrics_list = []
                for target in self.targets_list:
                    exporter_data = requests.get(
                        "{}://{}/{}".format(
                            self.protocol, target, self.query_endpoint)
                    )
                    exporter_data_text = exporter_data.text
                    exporter_data_filtered = self._exporter_filter_metrics(
                            exporter_data_text)
                    metrics_list += exporter_data_filtered
                return metrics_list
            else:
                if metric_name is None:
                    if xnf_id in self.targets_list:
                        exporter_data = requests.get(
                            "{}://{}/{}".format(
                                self.protocol, xnf_id, self.query_endpoint)
                        )
                        exporter_data_text = exporter_data.text
                        exporter_data_filtered = self._exporter_filter_metrics(
                                exporter_data_text)
                        return exporter_data_filtered
                    else:
                        return "Target: \"{}\" is not registered".format(
                                xnf_id)
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
                            exporter_data_filtered = \
                                self._exporter_filter_metrics(
                                        exporter_data_text)
                            return exporter_data_filtered
                        else:
                            return "Target: \"{}\" is not registered".format(
                                    xnf_id)
        except Exception as e:
            err_message = "An error has occurred. " + \
                "Please verify Prometheus Exporter runs in the target"
            err = {"Error": "{}. Details: {}".format(err_message, e)}
            return err

    # FIXME length of lines
    def mongodb_metrics(self, xnf_id, metric_name):
        # FIXME parenthesis should not be needed
        if (xnf_id is None) and (metric_name is None):
            try:
                mongo_list = []
                for target in self.targets_list:
                    # FIXME
                    # This is repeated few lines below. Either you use another
                    # method for these or somehow integrate these to avoid
                    # repetitions
                    # FIXME: "i" is not descriptive. Never use variables which
                    # are not descriptive! Why not "xnf_met" or similar?
                    for i in custom_metrics.find({"xnf_id": target}):
                        mongo_dict = {
                            # FIXME: why not using the given "xnf_id"? Should
                            # not it be the same passed by parameter?
                            # Why not creating a common dictionary at the top
                            # and then update with new data as needed?
                            "xnf-id": "",
                            "metric-name": "",
                            "metric-command": "",
                            "metric-value": None,
                            # FIXME: store in MongoDB the milliseconds when the
                            # metric was taken (adapt the model for this), then
                            # fill this variable from there - and then, if
                            # needed, apply this "%.3f % value" formatting
                            "metric-timestamp": "%.3f" % (time.time()),
                        }
                        # FIXME access to dictionaries
                        mongo_dict["xnf-id"] = i["xnf_id"]
                        mongo_dict["metric-name"] = i["metric_name"]
                        mongo_dict["metric-command"] = i["metric_command"]
                        mongo_dict["metric-value"] = i["data"]
                        mongo_list.append(mongo_dict)
                return mongo_list
            except Exception:
                err_message = "{} {}".format(
                        "An error ocurred with your request.",
                        "Check your MongoDB connection")
                err = {"Error": err_message}
                return err
        else:
            if metric_name is None:
                if xnf_id in self.targets_list:
                    mongo_list = []
                    # FIXME same as above
                    for i in custom_metrics.find({"xnf_id": xnf_id}):
                        mongo_dict = {
                            "xnf-id": "",
                            "metric-name": "",
                            "metric-command": "",
                            "metric-value": None,
                            "metric-timestamp": "%.3f" % (time.time()),
                        }
                        mongo_dict["xnf-id"] = i["xnf_id"]
                        mongo_dict["metric-name"] = i["metric_name"]
                        mongo_dict["metric-command"] = i["metric_command"]
                        mongo_dict["metric-value"] = i["data"]
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
