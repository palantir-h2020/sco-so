#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


import copy
import json
import shutil


class PrometheusTargetsHandler(object):

    def __init__(self, targets_file_name: str):
        self.targets_file_name = targets_file_name

    def _get_targets(self) -> list:
        targets_dict = self.read_file()
        return targets_dict[0]["targets"]

    def read_file(self, file_name: str = None) -> str:
        file_content = ""
        # Take by default the targets file passed to the instance
        if file_name is None:
            file_name = self.targets_file_name
        with open(file_name, "r") as targets_file:
            file_content = json.loads(targets_file.read())
        return file_content

    def write_file(self, content: str):
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
        current_content = self.read_file("%s.bak" % self.targets_file_name)
        del(current_content[0]["targets"])
        # The new content must be copied as a new object in memory, or
        # otherwise the content to be written would be modified/compromised
        new_content_cp = copy.deepcopy(new_content)
        del(new_content_cp[0]["targets"])
        is_valid_content = (current_content == new_content_cp)
        print("Debug: validity of new data: %s" % str(is_valid_content))
        return is_valid_content

    def update_contents(self, targets_list: list):
        shutil.copyfile(self.targets_file_name,
                        "%s.bak" % self.targets_file_name)
        targets_dict = self.read_file()
        targets_dict[0]["targets"] = targets_list
        if self.validate_content_against_previous_conf(targets_dict):
            self.write_file(json.dumps(targets_dict))

    def add_target(self, url: str):
        targets_list = self._get_targets()
        targets_list.append(url)
        self.update_contents(targets_list)
        # TODO: introduce means to verify the content is properly
        # updated w.r.t. to the request

    def replace_target(self, old_url: str, new_url: str):
        targets_list = self._get_targets()
        index_target = targets_list.index(old_url)
        targets_list[index_target] = new_url
        self.update_contents(targets_list)
        # TODO: introduce means to verify the content is properly
        # updated w.r.t. to the request

    def delete_target(self, url: str):
        targets_list = self._get_targets()
        index_target = targets_list.index(url)
        del(targets_list[index_target])
        self.update_contents(targets_list)
        # TODO: introduce means to verify the content is properly
        # updated w.r.t. to the request
