import os
import logging
from logging import getLogger, StreamHandler, Formatter, FileHandler
from slack_log_handler import SlackLogHandler
import datetime
from config import config

config_log = config['log']
LOG_FILE_DIR = None
if config_log.get('LOG_DIR'):
    LOG_FILE_DIR = '{}/log_{}.txt'.format(config_log['LOG_DIR'], datetime.datetime.now().strftime('%Y%m%dT%H%M%S'))
LOG_LEVEL_BASE = logging.__getattribute__(config_log['LOG_LEVEL_BASE'])
LOG_LEVEL_FILE =  logging.__getattribute__(config_log['LOG_LEVEL_FILE'])
LOG_LEVEL_SLACK =  logging.__getattribute__(config_log['LOG_LEVEL_SLACK'])
SLACK_WEBHOOK_URL = config_log.get('SLACK_WEBHOOK_URL')

import subprocess
subprocess.run("dir={}; [ ! -e $dir ] && mkdir -p $dir".format(config_log['LOG_DIR']),shell=True)

HOSTNAME = os.environ.get('HOSTNAME') if os.environ.get('HOSTNAME') is not None else os.uname()[1]

def get_module_logger(name=None):
    global loggers
    if 'loggers' not in globals():
        loggers = {}
    
    if name is None:
        name = __name__
    if loggers.get(name):
        return loggers.get(name)
    
    # logger の基本設定
    logger = getLogger(name)
    logger.setLevel(LOG_LEVEL_BASE)
    formatter = Formatter("%(asctime)s :%(filename)-10s %(lineno)-4d:%(levelname)-8s:%(funcName)-22s:%(message)s")
    
    # 標準出力 Handler
    sh = StreamHandler()
    logger.addHandler(sh)
    sh.setLevel(LOG_LEVEL_BASE)
    sh.setFormatter(formatter)
    
    # ファイル出力 Handler
    if LOG_FILE_DIR is not None:
        fh = FileHandler(LOG_FILE_DIR)
        fh.setLevel(LOG_LEVEL_FILE)
        logger.addHandler(fh)
        fh.setFormatter(formatter)
    
    # slack への通知
    if SLACK_WEBHOOK_URL is not None:
        slack = SlackLogHandler(
            SLACK_WEBHOOK_URL,
            username = HOSTNAME,
            emojis = {
                logging.INFO: ':cubimal_chick:',
                logging.WARNING: ':cloud:',
                logging.ERROR: ':japanese_goblin:',
                logging.CRITICAL: ':exploding_head:',
            }
        )
        slack.setLevel(LOG_LEVEL_SLACK)
        slack.setFormatter(formatter)
        logger.addHandler(slack)
    
    logger.propagate = False
    loggers[name] = logger
    
    ln = lambda nolevel: logging.getLevelName(nolevel)
#     logger.info(f'''
# 【 LOG CONFIG 】
#     - LOG_LEVEL_BASE: {ln(LOG_LEVEL_BASE)},
#     - LOG_FILE_DIR: {LOG_FILE_DIR},
#     - LOG_LEVEL_FILE: {ln(LOG_LEVEL_FILE)},
#     - SLACK_WEBHOOK_URL: {SLACK_WEBHOOK_URL},
#     - LOG_LEVEL_SLACK: {ln(LOG_LEVEL_SLACK)},
#     ''')
    return logger