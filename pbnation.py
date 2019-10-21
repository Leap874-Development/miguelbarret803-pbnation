import requests
import re
import bs4

import config

def board_url(board):
	return config.SITE + 'forumdisplay.php?f=%s' % board

def thread_url(thread):
	return config.SITE + 'printthread.php?t=%s' % thread

def thread_url_user(thread):
	return config.SITE + 'showthread.php?t=%s' % thread

def get_body(raw_html):
	cleanr = re.compile('<.*?>')
	ct = re.sub(cleanr, ' ', raw_html)
	ct = ct.replace('&gt', '>')
	ct = ct.replace('&lt', '<')
	ct = ct.replace('\t', '')
	clean = ''
	for line in ct.split('\n'):
		if line.strip():
			clean += line.strip() + '\n'
	clean = clean.replace('\n', ' ')
	clean = clean[:config.PREVIEW_LENGTH].strip()
	return ' '.join(clean.split()[:-1]) + '...'

def poll_board(board):
	with open('records.txt') as f:
		sent = [ a for a in f.read().split('\n') ]

	resp = requests.get(board_url(board), headers=config.HEADERS)
	soup = bs4.BeautifulSoup(resp.text, features='lxml')

	block = soup.find('tbody', id='threadbits_forum_%s' % board)
	threads = block.find_all('tr')
	to_send = []

	for thread in threads:
		icon = thread.find('img')['src']
		tid = int(thread.find('td')['id'].split('_')[-1])
		is_locked = 'lock' in icon

		if str(tid) not in sent:
			to_send.append(tid)

	return to_send

def get_board_name(board):
	resp = requests.get(board_url(board), headers=config.HEADERS)
	soup = bs4.BeautifulSoup(resp.text, features='lxml')

	is_title = lambda x: x.startswith('external.php')
	title = soup.find_all('link', href=is_title)[1]['title'].split(' - ')[0]

	return title

def get_thread_info(thread):
	# part one for basic info, title body etc
	resp = requests.get(thread_url(thread), headers=config.HEADERS)
	soup = bs4.BeautifulSoup(resp.text, features='lxml')

	is_poster = lambda x: x.startswith('font-size:')

	comments = soup.find_all('td', {'class': 'page'})
	original = comments[0]

	poster = original.find('td', style=is_poster).text.strip()
	date = original.find('td', align='right').text.strip()

	try:
		title = original.find('strong').text.strip()
	except AttributeError as e:
		title = None

	body = original.findChildren('div', recursive=False)[1]
	desc = get_body(str(body))

	# part two for images and profile picture, other user stuff
	resp = requests.get(thread_url_user(thread), headers=config.HEADERS)
	soup = bs4.BeautifulSoup(resp.text, features='lxml')

	is_profile = lambda x: x.startswith('https://www.pbnation.com/images/')

	body = soup.find('div', {'id': 'posts'})
	prof = body.find_all('img', src=is_profile)[1]['src']

	if not title:
		title = ' '.join(body[:20].split()[:-1])

	return {
		'desc': desc,
		'user': poster,
		'date': date,
		'title': title,
		'tid': thread,
		'prof': prof
	}

print(get_board_name(13))

# 1819453 1819575
# poll_board(13)
# print(get_thread_info(5523234))
