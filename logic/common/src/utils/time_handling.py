#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from datetime import datetime


class TimeHandling:

    @staticmethod
    def ms_to_rfc3339(time_ms: int) -> str:
        try:
            creation_time = int(time_ms) * 1000
            creation_time = datetime.fromtimestamp(creation_time/1000.0)
            creation_time = creation_time.isoformat("T") + "Z"
        except Exception:
            creation_time = time_ms
        return creation_time
