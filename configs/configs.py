# -*- coding: utf-8 -*-
# """
# configs.py
# Created on Feb 18, 2025
# @ Author: Mazhar
# """

import logging
from typing import Any

import yaml

logger: logging.Logger = logging.getLogger(name="app.logs")

DATA_COLLECTION_CONFIGS = "./configs/data_collection_cfg.yaml"


cfgs: dict = {}
try:
    with open(file=DATA_COLLECTION_CONFIGS, mode="r") as file:
        cfgs = yaml.safe_load(stream=file)
except FileNotFoundError:
    logger.error(msg=f"{DATA_COLLECTION_CONFIGS} not found.")
finally:
    if not cfgs:
        logger.error(msg="No configuration found in the YAML file.")
        exit(code=1)
