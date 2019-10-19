import tweepy
from utils import update_tweet_info
from databases import refresh_session
from apis import api
from const import JP_LOCATION_LIST

from logger import get_module_logger
logger = get_module_logger(__name__)


class DBStreamListener(tweepy.StreamListener):

    def on_status(self, tw):
        logger.debug(f'got {tw.id_str}')
        session = refresh_session()
        update_tweet_info(session, tw)


def main():
    try:
        myStreamListener = DBStreamListener()
        myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
        myStream.filter(locations=JP_LOCATION_LIST)

    except Exception as e:
        logger.debug(e)
        main()

if __name__ == '__main__':
    main()
