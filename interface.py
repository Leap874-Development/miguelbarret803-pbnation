import discord
import asyncio

import pbnation
import config

client = discord.Client()

async def status_task():
	await client.wait_until_ready()

	while True:
		await do_update()
		await asyncio.sleep(config.UPDATE_FREQ)

@client.event
async def on_message(message):
	if message.author == client.user:
		return

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')

async def do_update():
	print('Starting process')
	embeds = get_embeds()
	for embed, channel_id in embeds:
		channel = client.get_channel(channel_id)
		await channel.send(embed=embed)
	print('Completed update')

def make_embed(thread, board):
	info = pbnation.get_thread_info(thread)
	print(info)

	if config.BOARD_NAME:
		author = '%s - %s' % (board, info['user'])
	else:
		author = info['user']
	
	embed = discord.Embed(
		title=info['title'],
		description=info['desc'],
		url=pbnation.thread_url_user(thread),
		color=config.COLOR)
	embed.set_author(name=author, icon_url=info['prof'])
	return embed

def get_embeds():
	embeds = []
	channels = []
	for board in config.BOARDS:
		print('=> ' + str(board))
		board_name = pbnation.get_board_name(board)
		to_send = pbnation.poll_board(board)
		print(to_send)

		with open('records.txt', 'a') as f:
			for post in to_send:
				try:
					embed = make_embed(post, board_name)
					f.write('%s\n' % post)
					print('Created embed for %s' % post)
					embeds.append(embed)
					channels.append(config.BOARDS[board])
				except Exception as e:
					print(e)
	return zip(embeds, channels)

# https://discordapp.com/api/oauth2/authorize?client_id=611000022120792064&permissions=0&scope=bot
client.loop.create_task(status_task())
client.run(config.TOKEN)
