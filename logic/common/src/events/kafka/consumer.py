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
# from confluent_kafka import Consumer as KafkaConsumer
# import json

LOGGER = setup_custom_logger(__name__)


class SOConsumer():
    """
    Consumer on a given Kafka topic.
    """

    def __init__(self, topic: str):
        self.config = FullConfParser()
        self.events_category = self.config.get("events.yaml")
        self.kafka_section = self.events_category.get("kafka")
        self.host = self.kafka_section.get("host")
        self.port = int(self.kafka_section.get("port"))
        self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=["{}:{}".format(self.host, self.port)],
                group_id="so-consumer",
                auto_offset_reset="earliest",
                enable_auto_commit=True)
        # self.consumer = KafkaConsumer({
        #     "bootstrap.servers": "{}:{}".format(self.host, self.port),
        #     "group.id": "so-consumer",
        #     "auto.offset.reset": "earliest"})
        # value_deserializer=lambda x: json.loads(x.decode("utf-8")))
        self.topic = topic

    def read(self, topic: str = None):
        if topic is not None:
            self.consumer.subscribe(topic)
            # self.consumer.subscribe([topic])
        # for msg in self.consumer.poll():
        #     yield msg
        #     # return msg
        return [x for x in self.consumer.poll()]
        # return [x for x in self.consumer.poll(1.0)]
