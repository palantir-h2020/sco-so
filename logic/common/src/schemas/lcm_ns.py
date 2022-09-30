#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from enum import Enum


class NSInstanceActionExecWaitForData(str, Enum):
    # Async method
    none = "NONE"
    # Wait for action ID
    action_id = "ACTION_ID"
    # Wait for the full output of the action
    action_output = "ACTION_OUTPUT"
