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
# from confluent_kafka import Producer as KafkaProducer
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
        # self.producer = KafkaProducer({
        #     "bootstrap.servers": "{}:{}".format(self.host, self.port)
        #     })
        self.topic = topic

    def receipt(self, err, msg):
        if err is not None:
            print("Error: {}".format(err))
        else:
            message = "Produced message on topic {} with value of {}\n".format(
                    msg.topic(), msg.value().decode("utf-8"))
            print(message)

    def write(self, data):
        # Enforce writing in JSON as much as possible
        data = content.convert_to_json(data)
        pkt = self.producer.send(
                self.topic,
                data)
        # self.producer.poll()
        # self.producer.produce(
        #         producer_topic,
        #         json.dumps(data).encode("utf-8"),
        #         callback=self.receipt)
        # self.producer.flush()
        time.sleep(0.3)
        return pkt
