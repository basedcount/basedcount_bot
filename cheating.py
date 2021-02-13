# Anti-cheating functions

# Python Libraries
import json
from datetime import timedelta, datetime

# basedcount_bot Libraries
from passwords import savePath, bot


def checkForCheating(author, parentAuthor):
	with open(savePath + 'cheatingDatabase.json') as database:
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

	with open(savePath + 'cheatingDatabase.json', 'w') as database:
		json.dump(cheatingDatabase, database)

	
def sendCheatReport():
	global reset
	now = datetime.now()
	seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
	
	# Prepare Cheat Report
	if seconds_since_midnight > 84000:
		if reset == True:
			with open(savePath + 'cheatingDatabase.json') as database:
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

			# Clean Database
			cheatingDatabase['users'] = {}
			with open(savePath + 'cheatingDatabase.json', 'w') as database:
				json.dump(cheatingDatabase, database)
			reset = False

	# Set trigger to go off near midnight
	if seconds_since_midnight < 84000:
		reset = True

reset = False