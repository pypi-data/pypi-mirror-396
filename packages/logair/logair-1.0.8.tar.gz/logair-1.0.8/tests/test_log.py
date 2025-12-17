# Copyright (c) ZhangYundi.
# Licensed under the MIT License. 
# Created on 2025/7/18 20:30
# Description:

from logair import get_logger

if __name__ == '__main__':
    logger_a = get_logger(__name__, fname="mod_a")
    # logger_b = get_logger("B")
    # logger_b.info("info from B")
    logger_a.info("info from A")
    logger_a.warning("warning from A")
    logger_a.info("test long info, all bala bala bala... and bala bala bala")