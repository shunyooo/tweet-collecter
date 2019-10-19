#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import models

from config import config


def get_db_url():
    return f"{dbi['DBMS']}://{dbi['USER']}:{dbi['PASS']}@{dbi['HOST']}:{dbi['PORT']}/{dbi['DB']}?charset=utf8mb4"


def get_db_ssl_args():
    args = {}

    def set_if_exist(dbi_key, set_key):
        nonlocal args
        if dbi_key in dbi:
            args[set_key] = dbi[dbi_key]

    set_if_exist('SSL_KEY', 'key')
    set_if_exist('SSL_CA', 'ca')
    set_if_exist('SSL_CERT', 'cert')
    return {'ssl': args}

Base = declarative_base()
# MySQLに接続。
dbi = config['db']
url = get_db_url()
engine = create_engine(
    url, echo=dbi['ECHO'] == 'True', connect_args=get_db_ssl_args())
models.Base.metadata.create_all(engine)
# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()


def refresh_session():
    global session
    del session
    session = Session()
    return session
