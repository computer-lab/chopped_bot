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
import flickr_api
from oauth2client.client import SignedJwtAssertionCredentials
from cStringIO import StringIO
from time import sleep

def rescale(img, width, height, force=True):
	"""Rescale the given image, optionally cropping it to make sure the result image has the specified width and height."""


	max_width = width
	max_height = height
	if not force:
		img.thumbnail((max_width, max_height), Image.ANTIALIAS)
	else:
		src_width, src_height = img.size
		src_ratio = float(src_width) / float(src_height)
		dst_width, dst_height = max_width, max_height
		dst_ratio = float(dst_width) / float(dst_height)

		if dst_ratio < src_ratio:
			crop_height = src_height
			crop_width = crop_height * dst_ratio
			x_offset = float(src_width - crop_width) / 2
			y_offset = 0
		else:
			crop_width = src_width
			crop_height = crop_width / dst_ratio
			x_offset = 0
			y_offset = float(src_height - crop_height) / 3
		img = img.crop((int(x_offset), int(y_offset), int(x_offset)+int(crop_width), int(y_offset)+int(crop_height)))
		img = img.resize((dst_width, dst_height), Image.ANTIALIAS)

	output_data = img.save('background.png')


	return output_data


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


def tweet_image(image, txt, consumer_key, consumer_secret, access_token, access_token_secret):
    api = twitter_api(consumer_key, consumer_secret, access_token, access_token_secret)
    api.update_with_media(image, status=txt)
    os.remove(image)


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

farts = True

consumer_key, consumer_secret, access_token, access_token_secret = creds()

normal_array, weird_array =  build_arrays()


flickr_api.set_keys(api_key = '5143fde92484db1943a4f851f8463c93', api_secret = '81af5151a3f0d903')

while farts is True:

	normal1, normal2 = retrieve_two_elements(normal_array)
	weird1, weird2 = retrieve_two_elements(weird_array)
	print weird2
	w = flickr_api.Photo.search(text=weird2,per_page=200,page=1)
	photos = []
	for p in w:
		photos.append(p)
	p = random.choice(photos)
	gotphoto = False
	while gotphoto is False:
		try:
			p.save("image.png",size_label = 'Original')
			print 'Got Photo'
			gotphoto = True
		except Exception:
			print 'Did not get photo, retrying'
			p = random.choice(photos)
			p.save("image.png",size_label = 'Original')
			print 'Got Photo'
			gotphoto = True
			pass


	new_height = int(340)
	new_width  = int(350)
	im = Image.open('image.png')
	background = rescale(im,new_width,new_height)
	background = Image.open('background.png')
	new_background = Image.new('RGBA', (540,340))
	x, y = background.size
	new_background.paste(background, (190,0))
	new_background.save('background.png')

	img = Image.open('template.png')
	font = ImageFont.truetype('Arial Bold.ttf', 14)
	draw = ImageDraw.Draw(img)
	print normal1, normal2, weird1, weird2
	draw_words(normal1,80,14)
	draw_words(weird1,130,13)
	draw_words(normal2,180,12)
	draw_words(weird2,230,13)
	img.save('foreground.png')
	foreground = Image.open('foreground.png')
	background = Image.open('background.png')
	background.paste(foreground, (0, 0),foreground)
	background.save('output.png')

	txt = normal1 + '\n' + weird1 + '\n' + normal2 + '\n' + weird2

	tweet_image('output.png', txt, consumer_key, consumer_secret, access_token, access_token_secret)
	print 'Tweeted ... now waiting'
	time.sleep(random.randint(38200,43200))

