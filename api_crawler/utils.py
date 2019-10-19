#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from contextlib import closing
from logging import getLogger
import json
import requests
import tweepy
from sqlalchemy.orm import load_only
import models
from apis import api
from databases import Session


logger = getLogger(__name__)


def int_or_None(s):
    if s is None:
        return None
    else:
        return int(s)


def download_media(rsession, media_urls, local_media_file):
    try:
        os.makedirs('media')
    except FileExistsError:
        pass
    filename = os.path.join('media', local_media_file)
    for (i, media_url) in enumerate(media_urls):
        with closing(rsession.get(media_url, stream=True)) as r:
            if r.status_code == 404:
                if i == len(media_urls) - 1:
                    logger.warning(
                        'Media not found and giving up fetching: %s',
                        media_url)
                continue
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)


def update_tweet_info(session, tw):
    entities = tw.entities.copy()
    if hasattr(tw, 'extended_entities'):
        for (k, v) in tw.extended_entities.items():
            entities[k] = v

    update_user_info(session, tw.user)
    if hasattr(tw, 'quoted_status'):
        quoted_status = tw.quoted_status
        if type(quoted_status) == dict:
            quoted_status = tweepy.Status.parse(api, quoted_status)
        update_tweet_info(session, quoted_status)
    if hasattr(tw, 'retweeted_status'):
        update_tweet_info(session, tw.retweeted_status)

    tw_db = session.query(models.Tweet)\
        .options(load_only("id"))\
        .filter_by(id=int(tw.id_str))\
        .one_or_none()
    if tw_db is None:
        tw_db = models.Tweet(id=int(tw.id_str))
        session.add(tw_db)
    if tw.coordinates is not None:
        tw_db.coordinates_longitude = tw.coordinates['coordinates'][0]
        tw_db.coordinates_latitude = tw.coordinates['coordinates'][1]
    else:
        tw_db.coordinates_longitude = None
        tw_db.coordinates_latitude = None
    tw_db.created_at = tw.created_at
    if hasattr(tw, 'current_user_retweet'):
        tw_db.current_user_retweet = \
            int_or_None(tw.current_user_retweet['id_str'])
    else:
        tw_db.current_user_retweet = None
    tw_db.favorite_count = tw.favorite_count
    tw_db.favorited = tw.favorited
    tw_db.filter_level = getattr(tw, 'filter_level', None)
    tw_db.in_reply_to_screen_name = tw.in_reply_to_screen_name
    tw_db.in_reply_to_status_id = int_or_None(tw.in_reply_to_status_id_str)
    tw_db.in_reply_to_user_id = int_or_None(tw.in_reply_to_user_id_str)
    tw_db.lang = tw.lang
    if hasattr(tw, 'place') and tw.place is not None:
        place = {}
        for k in ['attributes', 'country', 'code', 'country_code',
                  'full_name', 'id', 'name', 'place_type', 'url']:
            if hasattr(tw.place, k):
                place[k] = getattr(tw.place, k)
        place['bounding_box'] = {}
        place['bounding_box']['coordinates'] = \
            tw.place.bounding_box.coordinates
        place['bounding_box']['type'] = \
            tw.place.bounding_box.type
        tw_db.place = json.dumps(place)
    else:
        tw_db.place = None
    tw_db.possibly_sensitive = getattr(tw, 'possibly_sensitive', None)
    tw_db.quoted_status_id = \
        int_or_None(getattr(tw, 'quoted_status_id_str', None))
    if hasattr(tw, 'scopes') and tw.scopes is not None:
        tw_db.scopes = json.dumps(tw.scopes)
    else:
        tw_db.scopes = None
    tw_db.retweet_count = tw.retweet_count
    tw_db.retweeted = tw.retweeted
    if hasattr(tw, 'retweeted_status'):
        tw_db.retweeted_status_id = int_or_None(tw.retweeted_status.id_str)
    else:
        tw_db.retweeted_status_id = None
    tw_db.source = tw.source
    tw_db.source_url = tw.source_url
    tw_db.text = tw.text
    tw_db.truncated = tw.truncated
    tw_db.user_id = int_or_None(tw.user.id_str)
    if hasattr(tw, 'withheld_copyright'):
        tw_db.withheld_copyright = tw.withheld_copyright
    else:
        tw_db.withheld_copyright = None
    if hasattr(tw, 'withheld_in_countries'):
        tw_db.withheld_in_countries = tw.withheld_in_countries
    else:
        tw_db.withheld_in_countries = None
    if hasattr(tw, 'withheld_scope'):
        tw_db.withheld_scope = tw.withheld_scope
    else:
        tw_db.withheld_scope = None
    session.commit()

    if not hasattr(tw, 'retweeted_status'):
        for m in entities.get('media', []):
            update_media_info(session, tw, m)
        for ht in entities.get('hashtags', []):
            tweet_id = int(tw.id_str)
            indices_begin = ht['indices'][0]
            indices_end = ht['indices'][1]
            ht_db = session.query(models.TweetHashtag)\
                .options(load_only("tweet_id", "indices_begin",
                                   "indices_end"))\
                .filter_by(tweet_id=tweet_id,
                           indices_begin=indices_begin,
                           indices_end=indices_end)\
                .one_or_none()
            if ht_db is None:
                ht_db = models.TweetHashtag(tweet_id=int(tw.id_str),
                                            indices_begin=indices_begin,
                                            indices_end=indices_end)
                session.add(ht_db)
            ht_db.text = ht['text']
            session.commit()
        for url in entities.get('urls', []):
            tweet_id = int(tw.id_str)
            indices_begin = url['indices'][0]
            indices_end = url['indices'][1]
            url_db = session.query(models.TweetUrl)\
                .options(load_only("tweet_id", "indices_begin",
                                   "indices_end"))\
                .filter_by(tweet_id=tweet_id,
                           indices_begin=indices_begin,
                           indices_end=indices_end)\
                .one_or_none()
            if url_db is None:
                url_db = models.TweetUrl(tweet_id=int(tw.id_str),
                                         indices_begin=indices_begin,
                                         indices_end=indices_end)
                session.add(url_db)
            url_db.url = url['url']
            url_db.display_url = url['display_url']
            url_db.expanded_url = url['expanded_url']
            session.commit()
        for sym in entities.get('symbols', []):
            tweet_id = int(tw.id_str)
            indices_begin = sym['indices'][0]
            indices_end = sym['indices'][1]
            sym_db = session.query(models.TweetSymbol)\
                .options(load_only("tweet_id", "indices_begin",
                                   "indices_end"))\
                .filter_by(tweet_id=tweet_id,
                           indices_begin=indices_begin,
                           indices_end=indices_end)\
                .one_or_none()
            if sym_db is None:
                sym_db = models.TweetSymbol(tweet_id=int(tw.id_str),
                                            indices_begin=indices_begin,
                                            indices_end=indices_end)
                session.add(sym_db)
            sym_db.text = sym['text']
            session.commit()
        for um in entities.get('user_mentions', []):
            tweet_id = int(tw.id_str)
            indices_begin = um['indices'][0]
            indices_end = um['indices'][1]
            um_db = session.query(models.TweetUserMention)\
                .options(load_only("tweet_id", "indices_begin",
                                   "indices_end"))\
                .filter_by(tweet_id=tweet_id,
                           indices_begin=indices_begin,
                           indices_end=indices_end)\
                .one_or_none()
            if um_db is None:
                um_db = models.TweetUserMention(tweet_id=int(tw.id_str),
                                                indices_begin=indices_begin,
                                                indices_end=indices_end)
                session.add(um_db)
            um_db.user_id = int(um['id_str'])
            um_db.screen_name = um['screen_name']
            um_db.name = um['name']
            session.commit()


def update_user_info(session, u):
    if hasattr(u, 'status') and u.status is not None:
        update_tweet_info(session, u.status)

    u_db = session.query(models.User)\
        .options(load_only("id"))\
        .filter_by(id=int(u.id_str))\
        .one_or_none()
    if u_db is None:
        u_db = models.User(id=int(u.id_str))
        session.add(u_db)
    u_db.created_at = u.created_at
    u_db.default_profile = u.default_profile
    u_db.default_profile_image = u.default_profile_image
    u_db.description = u.description
    _entities = getattr(u, 'entities', None)
    u_db.entities = json.dumps(_entities) if _entities is not None else None
    u_db.favourites_count = u.favourites_count
    u_db.follow_request_sent = u.follow_request_sent
    u_db.followers_count = u.followers_count
    u_db.friends_count = u.friends_count
    u_db.geo_enabled = u.geo_enabled
    u_db.is_translator = u.is_translator
    u_db.lang = u.lang
    u_db.listed_count = u.listed_count
    u_db.location = u.location
    u_db.name = u.name
    u_db.profile_background_color = u.profile_background_color
    u_db.profile_background_image_url = u.profile_background_image_url
    u_db.profile_background_image_url_https = \
        u.profile_background_image_url_https
    u_db.profile_background_tile = u.profile_background_tile
    u_db.profile_banner_url = getattr(u, 'profile_banner_url', None)
    u_db.profile_image_url = u.profile_image_url
    u_db.profile_image_url_https = u.profile_image_url_https
    u_db.profile_link_color = u.profile_link_color
    u_db.profile_sidebar_border_color = u.profile_sidebar_border_color
    u_db.profile_sidebar_fill_color = u.profile_sidebar_fill_color
    u_db.profile_text_color = u.profile_text_color
    u_db.profile_use_background_image = u.profile_use_background_image
    u_db.protected = u.protected
    u_db.screen_name = u.screen_name
    u_db.show_all_inline_media = getattr(u, 'show_all_inline_media', None)
    if hasattr(u, 'status') and u.status is not None:
        u_db.status_id = int_or_None(u.status.id_str)
    else:
        u_db.status_id = None
    u_db.statuses_count = u.statuses_count
    u_db.time_zone = u.time_zone
    u_db.url = u.url
    u_db.utc_offset = u.utc_offset
    u_db.verified = u.verified
    u_db.withheld_in_countries = getattr(u, 'withheld_in_countries', None)
    u_db.withheld_scope = getattr(u, 'withheld_scope', None)
    session.commit()


def update_media_info(session, tw, m):
    m_db = session.query(models.Media)\
        .options(load_only("id"))\
        .filter_by(id=int(m['id_str']))\
        .one_or_none()
    if m_db is None:
        m_db = models.Media(id=int(m['id_str']))
        session.add(m_db)

    m_db.tweet_id = int(tw.id_str)
    m_db.media_url = m['media_url']
    m_db.media_url_https = m['media_url_https']
    m_db.url = m['url']
    m_db.display_url = m['display_url']
    m_db.expanded_url = m['expanded_url']
    m_db.sizes = json.dumps(m['sizes'])
    m_db.type = m['type']
    m_db.indices_begin = m['indices'][0]
    m_db.indices_end = m['indices'][1]
    if 'video_info' in m:
        m_db.video_info = json.dumps(m['video_info'])
    else:
        m_db.video_info = None

    m_db.locally_available = False
    m_db.locally_required = False
    session.commit()


def download_all_media(session):
    with requests.Session() as rsession:
        while True:
            media = session.query(models.Media)\
                .options(load_only('media_url_https', 'video_info'))\
                .filter_by(locally_required=True)\
                .filter_by(locally_available=False)\
                .limit(50)\
                .all()
            if len(media) == 0:
                break
            for m in media:
                urls = [
                    m.media_url_https + ':orig',
                    m.media_url_https + ':large',
                    m.media_url_https,
                ]
                try:
                    download_media(rsession, urls, m.local_media_name)
                    m.locally_available = True
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.exception(
                        "Exception during fetching media %s",
                        m.media_url_https)

    while True:
        media = session.query(models.Media)\
            .options(load_only())\
            .filter_by(locally_required=False)\
            .filter_by(locally_available=True)\
            .limit(50)\
            .all()
        if len(media) == 0:
            break
        for m in media:
            try:
                filename = os.path.join('media', m.local_media_name)
                try:
                    os.remove(filename)
                except FileNotFoundError as e:
                    pass
                m.locally_available = False
                session.commit()
            except Exception as e:
                session.rollback()
                logger.exception(
                    "Exception during deleting media %s",
                    m.local_media_name)


def update_local_requirements():
    session = Session()
    while True:
        media = session.query(models.Media)\
            .options(load_only())\
            .filter_by(locally_required=None)\
            .limit(50)\
            .all()
        if len(media) == 0:
            break
        for m in media:
            m.locally_required = m.locally_available
            session.commit()


def main():
    session = Session()
    count = 200
    while True:
        try:
            tws = api.home_timeline(count=count)
            logger.info(
                "got %d tweets from home timeline (count=%d)",
                len(tws), count)
            for tw in tws:
                try:
                    update_tweet_info(session, tw)
                except Exception as e:
                    session.rollback()
                    logger.exception(
                        "Exception during recording tweet %d",
                        tw.id)
            logger.info("Recorded tweets to db")
            download_all_media(session)
            logger.info("Downloaded all media")
        except Exception as e:
            session.rollback()
            logger.exception("Exception during fetching home timeline")
        time.sleep(70)

    return 0
