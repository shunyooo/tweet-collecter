from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DATETIME, DATE, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from logger import get_module_logger
from config import config

logger = get_module_logger(__name__)


def get_db_url():
    return f"{dbi['DBMS']}://{dbi['USER']}:{dbi['PASS']}@{dbi['HOST']}:{dbi['PORT']}/{dbi['DB']}?charset=utf8mb4"

Base = declarative_base()
# MySQLに接続。
dbi = config['db']
url = get_db_url()
engine = create_engine(url, echo=True)
# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()


class CrawlProgress(Base):
    """クロールのプログレス"""
    __tablename__ = 'crawl_progresses'
    id = Column(Integer, primary_key=True)
    host_name = Column(String(100))
    search_query_id = Column(Integer,
                             ForeignKey('search_queries.id',
                                        onupdate='CASCADE', ondelete='CASCADE'),
                             index=True)
    tweet_count = Column(Integer)  # 何ツイートクロールしたか
    day_count = Column(Integer)   # 何日クロールしたか
    goal_day_count = Column(Integer)  # 何日クロールする予定か
    # 0:PENDING, 1:RUNNING, 2:SUCCESS, 3:ERROR FINISH
    state = Column(Integer, index=True)
    created_at = Column(DATETIME, default=datetime.now, nullable=False)
    updated_at = Column(DATETIME, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<crawl_progress ({self.search_query_id}, {self.tweet_count} tweets, {self.day_count} days>'


class SearchQuery(Base):
    """検索クエリ"""
    __tablename__ = 'search_queries'

    id = Column(Integer, primary_key=True)
    query = Column(String(100), index=True)
    since_date = Column(DATE)
    untill_date = Column(DATE)
    lang = Column(String(30))
    tweet = relationship("Tweet")
    created_at = Column(DATETIME, default=datetime.now, nullable=False)
    updated_at = Column(DATETIME, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<search_query ({self.id}, {self.query}>'


class Tweet(Base):
    """ツイート"""
    __tablename__ = 'tweets'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(String(100), nullable=False, index=True)
    search_query_id = Column(Integer,
                             ForeignKey('search_queries.id',
                                        onupdate='CASCADE', ondelete='CASCADE'),
                             index=True)
    username = Column(String(100), index=True)
    user_id = Column(String(100), index=True)
    text = Column(Text, nullable=False)
    url = Column(Text, nullable=False)
    like_count = Column(Integer, index=True)
    reply_count = Column(Integer, index=True)
    retweet_count = Column(Integer, index=True)
    to_username = Column(String(100), index=True)
    mentions = Column(Text)
    hashtags = Column(Text)
    media_urls = Column(Text)
    timestamp = Column(DATETIME, nullable=False)
    sentiments = relationship("TweetSentiments")
    created_at = Column(DATETIME, default=datetime.now, nullable=False)
    updated_at = Column(DATETIME, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<tweet ({self.tweet_id}, {self.user_id}, {self.text}, {self.url}>'


class TweetSentiments(Base):
    """ツイートの感情分析結果保持用"""
    __tablename__ = 'tweet_sentiments'

    id = Column(Integer, primary_key=True)
    tweet_id = Column(Integer,
                      ForeignKey('tweets.id', onupdate='CASCADE',
                                 ondelete='CASCADE'),
                      index=True)
    model_name = Column(String(100), index=True)
    value = Column(Float, index=True)
    created_at = Column(DATETIME, default=datetime.now, nullable=False)
    updated_at = Column(DATETIME, default=datetime.now, nullable=False)

    def __repr__(self):
        return f'<tweet_sentiments ({self.id}, {self.tweet_id}, {self.model_name}, {self.value}>'


def insert_search_query(search_query, session=None):
    if session is None:
        session = get_session()
    q = session.execute(SearchQuery.__table__.insert(), search_query)
    session.commit()
    return q.inserted_primary_key[0]


def insert_tweets(tweet_list, search_query_id, session=None):
    if session is None:
        session = get_session()
    for t in tweet_list:
        t['search_query_id'] = search_query_id
    # logger.debug(tweet_list)
    session.execute(Tweet.__table__.insert(), tweet_list)
    session.commit()


def get_session():
    global session
    return session


def refresh_session():
    global session
    del session
    session = Session()
    return session


def init_database():
    engine.execute('DROP TABLE IF EXISTS {}'.format(
        CrawlProgress.__tablename__))
    engine.execute('DROP TABLE IF EXISTS {}'.format(
        TweetSentiments.__tablename__))
    engine.execute('DROP TABLE IF EXISTS {}'.format(Tweet.__tablename__))
    engine.execute('DROP TABLE IF EXISTS {}'.format(SearchQuery.__tablename__))

    # テーブル作成
    Base.metadata.create_all(engine)

if __name__ == '__main__':
    print(get_db_url())
    if 'y' in input('DBを初期化しますか？[y/n]: '):
        init_database()
