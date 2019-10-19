from config import config
import tweepy


api_con = config['api']
auth = tweepy.OAuthHandler(api_con['API_KEY'], api_con['API_SECRET_KEY'])
auth.set_access_token(api_con['ACCESS_TOKEN'], api_con['ACCESS_TOKEN_SECRET'])

api = tweepy.API(auth)
