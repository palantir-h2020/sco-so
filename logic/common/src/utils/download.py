#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021-present i2CAT
# All rights reserved


from tempfile import mkdtemp
from urllib.error import HTTPError
import os


class DownloadException(Exception):
    pass


def fetch_content(url):
    if not url.startswith("http"):
        return None
    tmp_folder = mkdtemp()
    tmp_file = url.split("/")[-1]
    tmp_path = os.path.join(tmp_folder, tmp_file)
    try:
        import urllib
        data = urllib.urlretrieve(url, tmp_path)
    except AttributeError:
        import urllib.request
        try:
            data = urllib.request.urlopen(url).read()
        except HTTPError:
            raise DownloadException
    f = open(tmp_path, "wb")
    f.write(data)
    f.close()
    return tmp_path
