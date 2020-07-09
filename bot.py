import json
import tweepy
import time
import os
import csv
import configparser
import urllib.parse
import sys
from datetime import datetime

def duplicate_check(id):
    value = False
    with open(CACHE_CSV, 'rt', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            if id in row:
                value = True
    f.close()
    return value

def log_post(id, post_url):
    with open(CACHE_CSV, 'a', newline='') as cache:
        date = time.strftime("%Y/%m/%d") + ' ' + time.strftime("%H:%M:%S")
        wr = csv.writer(cache, delimiter=',')
        wr.writerow([id, date, post_url])
    cache.close()

def hour():

	now = datetime.now()
	hour = str(now.hour) + ':' + str(now.minute)

	return hour

def retweet(Search):

	tweet_list = []
	#The 'recent' can be change to 'mixed' or to 'popular' to get different result
	tweet_list = twitter.search(Search, result_type = 'recent', count = 1)
	try:
		tweet = tweet_list[0]
		#Given the amount of tweets the duplicate check shouldn't be necessary but if you search for a really precise term it might be usefull
		if (duplicate_check(tweet.id) == False):
			try:
				#twitter.retweet(tweet.id) could also works, the code below quote the tweets instead
				retweet = twitter.update_status("Here is a bit of hug for your TL :)\n\n" + "https://twitter.com/" + tweet.user.screen_name + "/status/" + tweet.id_str)
				log_post(tweet.id, 'https://twitter.com/' + twitter.me().screen_name + '/status/' + retweet.id_str + '/')
				print("[ OK ] Succesfully retweeted")			
			except:

				print(" [ ERROR ] Error while retweeting")
				log_post(tweet.id, "Error while retweeting")
				
		else:			
			print("[OK] this tweet has already been retweeted")
	except:
		#For some reason sometimes the 0th element of tweet_list is out of bounds and throw this error, don't know how to fix this
		print("[ ERROR ] An unknow error has occur")

#The part below was made by corbindavenport
# Make sure config file exists
try:
    config = configparser.ConfigParser()
    config.read('config.ini')
except BaseException as e:
    print('[EROR] Error while reading config file:', str(e))
    sys.exit()
# General settings
CACHE_CSV = config['BotSettings']['CacheFile']
DELAY_BETWEEN_TWEETS = int(config['BotSettings']['DelayBetweenPosts'])
SEARCH = config['BotSettings']['Search']


# Log into Twitter if enabled in settings

if os.path.exists('twitter.secret'):
# Read API keys from secret file
	twitter_config = configparser.ConfigParser()
	twitter_config.read('twitter.secret')
	ACCESS_TOKEN = twitter_config['Twitter']['AccessToken']
	ACCESS_TOKEN_SECRET = twitter_config['Twitter']['AccessTokenSecret']
	CONSUMER_KEY = twitter_config['Twitter']['ConsumerKey']
	CONSUMER_SECRET = twitter_config['Twitter']['ConsumerSecret']
	try:
	    # Make sure authentication is working
	    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	    twitter = tweepy.API(auth)
	    twitter_username = twitter.me().screen_name
	    print('[ OK ] Sucessfully authenticated on Twitter as @' + twitter_username)
	except BaseException as e:
	    print('[EROR] Error while logging into Twitter:', str(e))
	    print('[EROR] Tootbot cannot continue, now shutting down')
	    exit()
else:
# If the secret file doesn't exist, it means the setup process hasn't happened yet
	print('[WARN] API keys for Twitter not found. Please enter them below (see wiki if you need help).')
	ACCESS_TOKEN = ''.join(
	    input('[ .. ] Enter access token for Twitter account: ').split())
	ACCESS_TOKEN_SECRET = ''.join(
	    input('[ .. ] Enter access token secret for Twitter account: ').split())
	CONSUMER_KEY = ''.join(
	    input('[ .. ] Enter consumer key for Twitter account: ').split())
	CONSUMER_SECRET = ''.join(
	    input('[ .. ] Enter consumer secret for Twitter account: ').split())
	print('[ OK ] Attempting to log in to Twitter...')
	try:
		# Make sure authentication is working
		auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
		auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
		twitter = tweepy.API(auth)
		twitter_username = twitter.me().screen_name
		print('[ OK ] Sucessfully authenticated on Twitter as @' + twitter_username)
		# It worked, so save the keys to a file
		twitter_config = configparser.ConfigParser()
		twitter_config['Twitter'] = {
			'AccessToken': ACCESS_TOKEN,
			'AccessTokenSecret': ACCESS_TOKEN_SECRET,
			'ConsumerKey': CONSUMER_KEY,
			'ConsumerSecret': CONSUMER_SECRET
		}
		with open('twitter.secret', 'w') as f:
			twitter_config.write(f)
		f.close()
	except BaseException as e:
		print('[EROR] Error while logging into Twitter:', str(e))
		print('[EROR] Tootbot cannot continue, now shutting down')
		exit()


# Run the main script
while True:
	#Make a cache file so to store
	if not os.path.exists(CACHE_CSV):
		with open(CACHE_CSV, 'w', newline='') as cache:
			default = ['Status ID', 'Date and time', 'Status link']
			wr = csv.writer(cache)
			wr.writerow(default)
			print('[ OK ] ' + CACHE_CSV + ' file not found, created a new one')
			cache.close()

	#Main process
	retweet(SEARCH)
	print(hour() + ' [ OK ] Sleeping for', DELAY_BETWEEN_TWEETS, 'seconds')
	time.sleep(DELAY_BETWEEN_TWEETS)
	print('[ OK ] Restarting main process...')
