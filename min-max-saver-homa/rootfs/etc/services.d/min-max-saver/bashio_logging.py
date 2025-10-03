"""
Module providing bashio like logging output, e.g.:
[18:29:31] INFO: service starting ...
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)
