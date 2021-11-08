# Anti-cheating functions

# Python Libraries
import json
import praw
from datetime import timedelta, datetime

# basedcount_bot Libraries
from passwords import bot, mongoPass

# Connect to Reddit
reddit = praw.Reddit(client_id=bot.client_id,
			client_secret=bot.client_secret,
			user_agent=bot.user_agent,
			username=bot.username,
			password=bot.password)

def connectMongo_History():
	cluster = MongoClient(mongoPass)
	dataBased = cluster['dataBased']
	return dataBased['basedHistory']


def checkForCheating(user, parentAuthor):
	basedHistory = connectMongo_History()

	# Add users to database
	userProfile = basedHistory.find_one({'name':user})
	if userProfile == None:
		basedHistory.update_one({'name': user}, {'$set': {parentAuthor: 1}}, upsert=True)
	else:
		if parentAuthor not in userProfile:
			basedHistory.update_one({'name': user}, {'$set': {parentAuthor: 1}})
		else:
			basedHistory.update_one({'name': user}, {'$set': {parentAuthor: userProfile[parentAuthor] + 1}})

	
def sendCheatReport():
	basedHistory = connectMongo_History()
	userProfile = basedHistory.find({})

	# Add Suspicious Users
	content = ''
	for user in userProfile:
		for key in user:
			if (key != '_id' and key != 'name'):
				if user[key] > 5:
					content = content + user['name'] + ' based ' + str(key) + ' ' + str(user[key]) + ' times.\n'

	# Send Cheat Report to Admin
	if content != '':
		reddit.redditor(bot.admin).message('Cheat Report', content)

	basedHistory.delete_many({})