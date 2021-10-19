# Anti-cheating functions

# Python Libraries
import json
import praw
from datetime import timedelta, datetime

# basedcount_bot Libraries
from passwords import bot

# Connect to Reddit
reddit = praw.Reddit(client_id=bot.client_id,
			client_secret=bot.client_secret,
			user_agent=bot.user_agent,
			username=bot.username,
			password=bot.password)


def checkForCheating(author, parentAuthor):
	with open('cheatingDatabase.json') as database:
		cheatingDatabase = json.load(database)

	# Add users to database
	if author not in cheatingDatabase['users']:
		cheatingDatabase['users'][author] = {parentAuthor:1}
	else:
		if parentAuthor not in cheatingDatabase['users'][author]:
			cheatingDatabase['users'][author][parentAuthor] = 1
		else:
			count = cheatingDatabase['users'][author][parentAuthor]
			cheatingDatabase['users'][author][parentAuthor] = count+1

	with open('cheatingDatabase.json', 'w') as database:
		json.dump(cheatingDatabase, database)

	
def sendCheatReport():
	with open('cheatingDatabase.json') as database:
		cheatingDatabase = json.load(database)

	# Add Suspicious Users
	content = ''
	for user in cheatingDatabase['users']:
		for key in cheatingDatabase['users'][user]:
			if cheatingDatabase['users'][user][key] > 5:
				content = content + user + ' based ' + key + ' ' + str(cheatingDatabase['users'][user][key]) + ' times.\n'

	# Send Cheat Report to Admin
	if content != '':
		reddit.redditor(bot.admin).message('Cheat Report', content)