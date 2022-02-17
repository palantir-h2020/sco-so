#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


import os
import sys
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../..")))
from common.config.parser.fullparser import FullConfParser
from common.log.log import setup_custom_logger
from kafka import KafkaConsumer
# import json

LOGGER = setup_custom_logger(__name__)


class SOConsumer():
    """
    Consumer on a given Kafka topic.
    """

    def __init__(self, topic: str = None):
        self.config = FullConfParser()
        self.events_category = self.config.get("events.yaml")
        self.kafka_section = self.events_category.get("kafka")
        self.host = self.kafka_section.get("host")
        self.port = int(self.kafka_section.get("port"))
        self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=["{}:{}".format(self.host, self.port)],
                group_id=None,
                auto_offset_reset="earliest",
                enable_auto_commit=True)
        # value_deserializer=lambda x: json.loads(x.decode("utf-8")))
        self.topic = topic

    def read_wait(self):
        for msg in self.consumer:
            yield msg
            # return msg

    def read_next(self):
        return next(self.consumer)
