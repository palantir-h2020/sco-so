#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2022-present i2CAT
# All rights reserved


class FileHandling:
    @staticmethod
    def extract_common_path(
          abs_path: str, rel_p_s: str, delim: str = "") -> str:
        """
        Given an absolute reference path and a relative path,
        find the common directory to the two of them, in a way
        that it is not repeated - and it can be used to be prepended
        to the relative path.

        E.g., with ref_path=/opt/common/utils/something.py and
        other_path=./deploy/local/somefile.json, the
        result will be "/opt".
        """

        common_path = ""
        abs_p_s = abs_path.split("/")
        rel_p_s = rel_p_s.split("/")

        if delim is not None and len(delim) > 0:
            # print("delim: " + str(delim))
            common_idx = abs_p_s.index(delim)
            # print("common_idx: " + str(common_idx))
            if common_idx >= 0:
                common_path = "/".join(abs_p_s[:common_idx-1])
                # print("common_path: " + str(common_path))
                return common_path

        common_path_bit = ""
        for s1_i in abs_p_s:
            # print("s1: " + str(s1_i))
            for s2_i in rel_p_s:
                # print("s2: " + str(s2_i))
                if s1_i == s2_i:
                    common_path_bit = s1_i
                    break

        # print("...")
        # print(common_path_bit)
        common_idx = abs_p_s.index(common_path_bit)
        # print(common_idx)
        if common_idx >= 0:
            common_path = "/".join(abs_p_s[:common_idx-1])
        return common_path
