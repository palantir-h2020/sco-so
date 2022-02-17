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
from common.server.http import content
from kafka import KafkaProducer
import json
import time

LOGGER = setup_custom_logger(__name__)


class SOProducer():
    """
    Producer on a given Kafka topic.
    """

    def __init__(self, topic: str = None):
        self.config = FullConfParser()
        self.events_category = self.config.get("events.yaml")
        self.kafka_section = self.events_category.get("kafka")
        self.host = self.kafka_section.get("host")
        self.port = int(self.kafka_section.get("port"))
        # Note: value_serializer implies writing everything as JSON
        self.producer = KafkaProducer(
                bootstrap_servers=["{}:{}".format(self.host, self.port)],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
                )
        self.topic = topic

    def write(self, data):
        # Enforce writing in JSON as much as possible
        data = content.convert_to_json(data)
        pkt = self.producer.send(
                self.topic,
                data)
        time.sleep(0.3)
        return pkt
