__title__ = "logiclayer-merge"
__description__ = "Logiclayer-Merge instance"

import os
import logging

from logiclayer import LogicLayer
from src.logiclayer_merge import MergeModule
from tesseract_olap import OlapServer

logging.basicConfig(level=logging.DEBUG)

olap_backend = os.environ["TESSERACT_BACKEND"]
olap_schema = os.environ["TESSERACT_SCHEMA"]
allowed_domains = os.environ.get("ALLOWED_DOMAINS", "")

olap = OlapServer(backend=olap_backend, schema=olap_schema)
mod = MergeModule(olap=olap, allowed_domains=allowed_domains)
mod.startup_tasks()
layer = LogicLayer()
layer.add_module('/merge', mod)
