import os
from pathlib import Path

import requests
from static.config import UrlConfig
from static.dump import Dump
from windows_pathlib import WindowsPathlib


class Constant(Dump):
    ALWAYS_EXTRACT_FROM_DMM = "ALWAYS_EXTRACT_FROM_DMM"
