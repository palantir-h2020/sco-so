#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved

from common.db.models.prometheus_targets import PrometheusTargets
from common.db.models.prometheus_targets_operation import\
    PrometheusTargetsOperation
from common.server.http.http_code import HttpCode
from datetime import datetime

import copy
import json
import shutil


class PrometheusTargetsHandler(object):

    def __init__(self, targets_file_name: str):
        self.targets_file_name = targets_file_name
        self.allowed_operations = ["add", "replace", "delete"]

    def _check_allowed_operation(self, operation: str) -> bool:
        return operation in self.allowed_operations

    def _get_targets_from_file(self) -> list:
        targets_dict = self._read_file()
        return targets_dict[0]["targets"]

    def _get_targets_from_db(self) -> list:
        """
        Retrieve the latest generated document, with the most
        up-to-date list of targets.
        """
        try:
            return PrometheusTargets.objects.order_by("-id").first().targets
        except Exception:
            return []

    def _construct_target_model_list_targets(
            self, operation: str, current_target: str,
            new_target: str) -> list:
        if not self._check_allowed_operation(operation):
            return []
        db_targets = copy.deepcopy(self._get_targets_from_db())
        # At this point the db_targets list should have been
        # validated to be in a proper state to operate with
        if operation == "add":
            db_targets.append(new_target)
        elif operation == "replace":
            current_target_pos = db_targets.index(current_target)
            db_targets[current_target_pos] = new_target
        elif operation == "delete":
            current_target_pos = db_targets.index(current_target)
            del(db_targets[current_target_pos])
        return db_targets

    def _construct_target_model(
            self, operation: str, current_target: str,
            new_target: str) -> PrometheusTargets:
        target_model = PrometheusTargets()
        db_targets = self._construct_target_model_list_targets(
            operation, current_target, new_target)
        target_model.targets = db_targets
        target_model.date = datetime.now()
        target_op_model = PrometheusTargetsOperation()
        target_op_model.operation = operation
        target_op_model.current_target = current_target
        target_op_model.new_target = new_target
        target_model.modification = target_op_model
        return target_model

    def _read_file(self, file_name: str = None) -> str:
        file_content = ""
        # Take by default the targets file passed to the instance
        if file_name is None:
            file_name = self.targets_file_name
        with open(file_name, "r") as targets_file:
            file_content = json.loads(targets_file.read())
        return file_content

    def _write_file(self, content: str):
        with open(self.targets_file_name, "w") as targets_file:
            targets_file.write(content)

    def validate_content_against_previous_conf(self, new_content: dict):
        """
        Verify the updated contents against the backup file
        in order to determine there is no loss of information
        regrading the structure (at least check everything but the
        updated list of targets).

        :param   new_content: dictionary with current contents (similar in
                  structure to the "self.targets_file_name" file contents)
        :return: boolean indicating whether two contents are similar (except
                  for the "targets" section") or not
        """
        current_content = self._read_file("%s.bak" % self.targets_file_name)
        del(current_content[0]["targets"])
        # The new content must be copied as a new object in memory, or
        # otherwise the content to be written would be modified/compromised
        new_content_cp = copy.deepcopy(new_content)
        del(new_content_cp[0]["targets"])
        is_valid_content = (current_content == new_content_cp)
        print("Debug: validity of new data: %s" % str(is_valid_content))
        return is_valid_content

    def _update_contents(self, targets_list: list):
        shutil.copyfile(self.targets_file_name,
                        "%s.bak" % self.targets_file_name)
        targets_dict = self._read_file()
        targets_dict[0]["targets"] = targets_list
        if self.validate_content_against_previous_conf(targets_dict):
            self._write_file(json.dumps(targets_dict))

    def list_targets(self) -> list:
        return self._get_targets_from_db()

    def add_target(self, url: str) -> HttpCode:
        db_targets = self._get_targets_from_db()
        # An already existing target cannot be added
        if url == "":
            return HttpCode.BAD_REQUEST
        if url in db_targets:
            return HttpCode.CONFLICT
        targets = self._construct_target_model("add", "", url)
        targets.save()
        # ...
        targets_list = self._get_targets_from_file()
        targets_list.append(url)
        self._update_contents(targets_list)
        # TODO: introduce means to verify the content is properly
        # updated w.r.t. to the request
        if url in targets_list:
            return HttpCode.OK
        else:
            return HttpCode.INTERNAL_ERROR

    def replace_target(self, old_url: str, new_url: str) -> HttpCode:
        db_targets = self._get_targets_from_db()
        # A non-existing target cannot be replaced
        if old_url == "" or new_url == "":
            return HttpCode.BAD_REQUEST
        if old_url not in db_targets:
            return HttpCode.CONFLICT
        targets = self._construct_target_model("replace", old_url, new_url)
        targets.save()
        # ...
        targets_list = self._get_targets_from_file()
        index_target = targets_list.index(old_url)
        targets_list[index_target] = new_url
        self._update_contents(targets_list)
        # TODO: introduce means to verify the content is properly
        # updated w.r.t. to the request
        if old_url in targets_list:
            return HttpCode.INTERNAL_ERROR
        else:
            if new_url in targets_list:
                return HttpCode.OK

    def delete_target(self, url: str) -> HttpCode:
        db_targets = self._get_targets_from_db()
        # A non-existing target cannot be deleted
        if url == "":
            return HttpCode.BAD_REQUEST
        if url not in db_targets:
            return HttpCode.CONFLICT
        targets = self._construct_target_model("delete", url, "")
        targets.save()
        # ...
        targets_list = self._get_targets_from_file()
        index_target = targets_list.index(url)
        del(targets_list[index_target])
        self._update_contents(targets_list)
        # TODO: introduce means to verify the content is properly
        # updated w.r.t. to the request
        if url in targets_list:
            return HttpCode.INTERNAL_ERROR
        else:
            return HttpCode.OK
