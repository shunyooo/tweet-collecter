import GetOldTweets3 as got
from logger import get_module_logger
import multiprocessing as multi
from functools import partial
import datetime as dt
import pandas as pd
from time import time
import utils
from config import config
import logging
logger = get_module_logger(__name__)

con = config['crawl']
BUFFER_TWEET_LENGTH = int(con['BUFFER_TWEET_LENGTH'])


def crawl_tweets(query, begindate, enddate, lang='ja', crawled_callback=None,):
    """
    query で begindate から enddate の日付範囲でクロールする。
    crawled_callback は取得毎に得られた tweets_list が渡されるコールバック。
    """

    query_report = f'{query}, {begindate} ~ {enddate}, {lang}'

    crawled_tweet_num = 0  # クロールした総件数

    logger.info(f'''
cpu count : {multi.cpu_count()}
crawl : {query_report}
バッファサイズ : {BUFFER_TWEET_LENGTH:.0f}''')

    date2query = lambda d: d.strftime('%Y-%m-%d')
    tweetCriteria = got.manager.TweetCriteria().setQuerySearch(query)\
        .setSince(date2query(begindate))\
        .setUntil(date2query(enddate))\
        .setLang(lang)

    callback_received_buffer = partial(
        _callback_received_buffer, crawled_callback=crawled_callback, query=query_report)
    tweet_list_got = got.manager.TweetManager.getTweets(
        tweetCriteria, receiveBuffer=callback_received_buffer)


def _callback_received_buffer(tweet_obj_list, query, crawled_callback):
    if len(tweet_obj_list) == 0:
        return

    tweet_dict_list = _tweet_list_to_unique_df(
        tweet_obj_list).to_dict(orient='records')
    logger.debug(f'{query}: got {len(tweet_obj_list)}（unique: {len(tweet_dict_list)}） tweets')
    if crawled_callback is not None:
        crawled_callback(tweet_dict_list)


def _tweet_list_to_unique_df(tweet_list):
    _tweet_list = [_tweet_to_dict(t) for t in tweet_list]
    df_unique = pd.DataFrame(_tweet_list).drop_duplicates(
        'tweet_id', keep='first')
    return df_unique


def _tweet_to_dict(tweet):
    # DB用にkeyを変更
    _dict = tweet.__dict__

    def _rename_attr(from_attr, to_attr):
        nonlocal _dict
        _dict[to_attr] = _dict.pop(from_attr)

    _rename_attr('author_id', 'user_id')
    _rename_attr('id', 'tweet_id')
    _rename_attr('to', 'to_username')
    _rename_attr('favorites', 'like_count')
    _rename_attr('replies', 'reply_count')
    _rename_attr('retweets', 'retweet_count')
    _rename_attr('permalink', 'url')
    _rename_attr('date', 'timestamp')
    _rename_attr('urls', 'media_urls')

    # 空文字をNoneに
    empty_to_none = lambda s: s if s != '' else None
    _dict = {k: empty_to_none(v) for k, v in _dict.items()}

    return _dict


if __name__ == '__main__':
    begindate = dt.date(2019, 6, 3)
    enddate = dt.date(2019, 6, 4)
    test_callback = lambda ts: logger.info(f'{len(ts)}件のツイートをクロールしました.')
    crawl_tweets('ダンジョン飯', begindate=begindate, enddate=enddate,
                 crawled_callback=test_callback)
