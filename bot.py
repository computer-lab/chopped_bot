from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import random
import json
import csv
import time
import tweepy
import os
import textwrap
import gspread
from oauth2client.client import SignedJwtAssertionCredentials



def creds():
        with open('creds.json') as data_file:
            data = json.load(data_file)
            consumer_key = data['creds'][0]['consumer_key']
            consumer_secret = data['creds'][0]['consumer_secret']
            access_token = data['creds'][0]['access_token']
            access_token_secret = data['creds'][0]['access_token_secret']
            return consumer_key, consumer_secret, access_token, access_token_secret


def twitter_api(consumer_key, consumer_secret, access_token, access_token_secret):
    consumer_key = consumer_key
    consumer_secret = consumer_secret
    access_token = access_token
    access_token_secret = access_token_secret
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def tweet_image(image, txt):
    api = twitter_api(consumer_key, consumer_secret, access_token, access_token_secret)
    api.update_with_media(tote, status=txt)
    os.remove(tote)


def build_arrays():
	json_key = json.load(open('chopped bot-610249be55b6.json'))
	scope = ['https://spreadsheets.google.com/feeds']
	credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)
	gc = gspread.authorize(credentials)
	sh = gc.open("choppedbot")
	weird_sheet = sh.worksheet("weird")
	normal_sheet = sh.worksheet("normal")
	weird_array = weird_sheet.col_values(1)
	normal_array = normal_sheet.col_values(1)

	return normal_array, weird_array

def retrieve_two_elements(array):
	element1 = random.choice(array)
	element2 = random.choice(array)
	if element2 == element1:
		while element1 == element2:
			element2 = random.choice(array)
		return element1, element2
	else:
		return element1, element2

def draw_words(word,y,wrap):
	if len(word) <= wrap:
		draw.text((57, y),word.upper(),(255,237,143),font=font,anchor='right')
	else:
		words = word.split(' ')
		first_two_words = ' '.join(words[0:2])
		if ((len(words) > 2) and (len(first_two_words) <= wrap)):
			draw.text((57, y),first_two_words.upper(),(255,237,143),font=font,anchor='right')
			words = words[2:]
			nextline = ' '.join(words)
			if len(nextline) <=14:
				draw.text((57, y+14),nextline.upper(),(255,237,143),font=font,anchor='right')
			else:
				y = y + 14
				for w in words:
					draw.text((57, y),nextline.upper(),(255,237,143),font=font,anchor='right')
					y = y + 14


		else:
			draw.text((57, y),words[0].upper(),(255,237,143),font=font,anchor='right')
			words = words[1:]
			nextline = ' '.join(words)
			draw.text((57, y+14),nextline.upper(),(255,237,143),font=font,anchor='right')
#consumer_key, consumer_secret, access_token, access_token_secret = creds()

normal_array, weird_array =  build_arrays()

normal1, normal2 = retrieve_two_elements(normal_array)
weird1, weird2 = retrieve_two_elements(weird_array)
img = Image.open('template.png')
font = ImageFont.truetype('microgramma.ttf', 12)
draw = ImageDraw.Draw(img)
print normal1, normal2, weird1, weird2
draw_words(normal1,80,14)
draw_words(weird1,130,13)
draw_words(normal2,180,12)
draw_words(weird2,230,13)
img.save('sample-out.png')