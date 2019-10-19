import datetime as dt
from database import insert_tweets, insert_search_query, init_database
from tweet_crawl import crawl_tweets
import argparse
import traceback
from logger import get_module_logger

logger = get_module_logger(__name__)


def valid_date(s):
    try:
        tdatetime = dt.datetime.strptime(s, "%Y-%m-%d")
        return dt.date(tdatetime.year, tdatetime.month, tdatetime.day)
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def crawl_and_insert_tweets_to_db(query, begindate=None, enddate=None, lang=None):
    if begindate is None:
        begindate = dt.date(2006, 3, 21)
    if enddate is None:
        enddate = dt.date.today()
    # クロールとDBへの挿入。
    query_dict = {'query': query, 'since_date': begindate,
                  'untill_date': enddate, 'lang': lang}
    search_query_id = insert_search_query(query_dict)
    crawl_tweets(query, begindate, enddate, lang=lang,
                 crawled_callback=lambda ts: insert_tweets(ts, search_query_id))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='クロールするやつです')
    parser.add_argument('query', help='検索クエリ')
    parser.add_argument('--since', help='since YYYY-MM-DD', type=valid_date)
    parser.add_argument('--until', help='until YYYY-MM-DD', type=valid_date)
    parser.add_argument("--lang", type=str, default='ja',
                        help="Set this flag if you want to query tweets in \na specific language. You can choose from:\n"
                             "en (English)\nar (Arabic)\nbn (Bengali)\n"
                             "cs (Czech)\nda (Danish)\nde (German)\nel (Greek)\nes (Spanish)\n"
                             "fa (Persian)\nfi (Finnish)\nfil (Filipino)\nfr (French)\n"
                             "he (Hebrew)\nhi (Hindi)\nhu (Hungarian)\n"
                             "id (Indonesian)\nit (Italian)\nja (Japanese)\n"
                             "ko (Korean)\nmsa (Malay)\nnl (Dutch)\n"
                             "no (Norwegian)\npl (Polish)\npt (Portuguese)\n"
                             "ro (Romanian)\nru (Russian)\nsv (Swedish)\n"
                             "th (Thai)\ntr (Turkish)\nuk (Ukranian)\n"
                             "ur (Urdu)\nvi (Vietnamese)\n"
                             "zh-cn (Chinese Simplified)\n"
                             "zh-tw (Chinese Traditional)"
                        )
    args = parser.parse_args()

    try:
        crawl_and_insert_tweets_to_db(args.query, args.since, args.until, args.lang)
    except Exception as e:
        traceback_str = traceback.format_exc()
        info = "{}\n{}".format(str(e), traceback_str)
        logger.critical(info)
