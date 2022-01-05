# User Commands Library

# Python Libraries
import json
from collections import Counter
from random import randint
import pymongo
from pymongo import MongoClient

# basedcount_bot Libraries
import ranks
from passwords import mongoPass

# No Based Count replies
myBasedNoUserReply = ["Hmm... I don't see you in my records, as it appears you aren't very based. I guess nobody's perfect.",
						"[mybasedcount_clever_response_1](https://www.youtube.com/watch?v=YzKM5g_FwYU&ab_channel=TheMar%C3%ADas)",
						"[mybasedcount_clever_response_2](https://www.youtube.com/watch?v=PNbBDrceCy8&ab_channel=TheWhoVEVO)",
						"[mybasedcount_clever_response_3](https://i.kym-cdn.com/photos/images/original/001/535/068/29d.jpg)",
						"[mybasedcount_clever_response_4](https://qph.fs.quoracdn.net/main-qimg-3999c004b514b9bfc6ba09527bfcd724)",
						"[mybasedcount_clever_response_5](https://media1.giphy.com/media/Q7LP0tm86sBWIqjFCL/giphy.gif)",
						"[mybasedcount_clever_response_6](https://www.youtube.com/watch?v=KeLtNnHEipA&ab_channel=AlltheAnime)",
						"[mybasedcount_clever_response_7](https://www.youtube.com/watch?v=pmGNo8RL5kM&ab_channel=YeahYeahYeahsVEVO)",
						"[mybasedcount_clever_response_8](https://www.youtube.com/watch?v=M5QGkOGZubQ&ab_channel=Fayroe)"]

basedCountNoUserReply = ["Yeah... I got nothing.",
						"[basedcount_clever_response_1](https://www.youtube.com/watch?v=XXJ99MJ67gw&ab_channel=pepperjackcheese1)",
						"[basedcount_clever_response_2](https://pics.me.me/never-met-him-trump-be-like-18509974.png)",
						"[basedcount_clever_response_3](https://www.youtube.com/watch?v=ZTFfdEeB6j8&ab_channel=EnglishSingsing)",
						"[basedcount_clever_response_4](https://media1.giphy.com/media/Q7LP0tm86sBWIqjFCL/giphy.gif)",
						"[basedcount_clever_response_5](https://i.pinimg.com/originals/cd/c5/ff/cdc5ffaf883b13e7bcd834e464ab971a.png)",
						"[basedcount_clever_response_6](https://www.youtube.com/watch?v=Cs57e-viIKw&ab_channel=ButtonsTheDragon)",
						"[basedcount_clever_response_7](https://www.youtube.com/watch?v=tOlh-g2dxrI&ab_channel=e7magic)"]

def connectMongo():
	cluster = MongoClient(mongoPass)
	dataBased = cluster['dataBased']
	return dataBased['users']

# === User Commands ===

def based(user, flair, pill):

	# Retrieve User Data
	count = addBasedCount(user, flair)
	pills = addPills(user, pill)
	rank = ranks.rankName(int(count), user)
	rankUp = ranks.rankMessage(int(count))

	# Build Reply Message
	replyMessage = ''
	if ((int(count)%5) == 0):
		replyMessage = "u/" + user + "'s Based Count has increased by 1. Their Based Count is now " + str(count) + '. \n\n Rank: '+ rank + '\n\n Pills: ' + pills + "\n\n I am a bot. Reply /info for more info."
		if rankUp:
			replyMessage = "u/" + user + "'s Based Count has increased by 1. Their Based Count is now " + str(count) + '. \n\n Congratulations, u/' + user + "! You have ranked up to " + rank + '! ' + rankUp + '\n\n Pills: ' + pills 
	elif int(count) == 1:
		replyMessage = 'u/' + user + " is officially based! Their Based Count is now 1. \n\n Rank: House of Cards"  + '\n\n Pills: ' + pills + "\n\n I am a bot. Reply /info for more info."
	return replyMessage


def myBasedCount(user):

	# Retrieve User Data
	count = str(checkBasedCount(user))
	pills = checkPills(user)

	# Build Reply Message
	if int(count) > 0:
		rank = ranks.rankName(int(count), user)
		replyMessage = "Your Based Count is " + count + ". \n\n" + 'Rank: ' + rank + "\n\n" + 'Pills: ' + pills
	else:
		replyMessage = myBasedNoUserReply[randint(0, len(myBasedNoUserReply)-1)]
	return replyMessage


def basedCountUser(string):

	# Take comment text string and remove everything except the username
	excludedStrings = ['/u/', 'u/', 'basedcount_bot ', '/basedcount ']
	for s in excludedStrings:
		if s in string:
			string = string.replace(s,'')
	user = string

	# Retrieve User Data
	count = str(checkBasedCount(user))
	pills = checkPills(user)

	# Build Reply Message
	if int(count) > 0:
		rank = ranks.rankName(int(count), user)
		replyMessage = user + "'s Based Count is " + count + ". \n\n" + 'Rank: ' + rank + "\n\n" + 'Pills: ' + pills
	else:
		replyMessage = basedCountNoUserReply[randint(0,len(basedCountNoUserReply)-1)]
	return replyMessage


def mostBased():
	dataBased = connectMongo()

	# Retrieve Data
	results = dataBased.find().sort('count', -1).limit(10)

	# Build Most Based List
	mostCountFlair = []
	u = 1
	for r in results:
		mostUserName = r['name']
		mostCount = str(r['count'])
		mostFlair = r['flair']
		mostCountFlair.append(str(str(u) + '. ' + mostUserName + '  |  ' + mostCount + '  |  ' + mostFlair + '\n\n'))
		u += 1

	# Build Reply Message
	replyMessage = '--The Top 10 Most Based Users--\n\n' + mostCountFlair[0] + mostCountFlair[1] + mostCountFlair[2] + mostCountFlair[3] + mostCountFlair[4] + mostCountFlair[5] + mostCountFlair[6] + mostCountFlair[7] + mostCountFlair[8] + mostCountFlair[9]
	return replyMessage



# === Databased Searching and Updating ===

def addBasedCount(user, flair):
	dataBased = connectMongo()
	# Check if existing user and calculate based count
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		dataBased.update_one({'name': user}, {'$set': {'flair': flair, 'count': 1, 'pills': 'None'}}, upsert=True)
		return 1
	else:
		dataBased.update_one({'name': user}, {'$set': {'flair': flair, 'count': userProfile['count'] + 1}})
		return userProfile['count'] + 1


def checkBasedCount(user):
	dataBased = connectMongo()
	# Check if existing user and calculate based count
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		return '0'
	else:
		return int(userProfile['count'])


def checkPills(user):
	dataBased = connectMongo()
	# Check if existing user and calculate pill list
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		return 'None'
	return "Pills have been temporarily disabled. Don't worry; pills are still being counted!" #str(userProfile['pills'])


def addPills(user, pill):
	dataBased = connectMongo()

	# Check if user exists
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		return 'None'

	if pill != 'None':
		# User doesn't have any previous pill data
		if userProfile['pills'] == 'None':
			dataBased.update_one({'name': user}, {'$set': {'pills': pill}})
			return "Pills have been temporarily disabled. Don't worry; pills are still being counted!" #pill

		# User has previous pill data
		oldPills = userProfile['pills']

		# Check for duplicates, then add and save
		if (((', ' + pill + ',') not in oldPills) and not oldPills.endswith(', ' + pill) and not oldPills.startswith(pill)):
			pill = ', ' + pill
			dataBased.update_one({'name': user}, {'$set': {'pills': userProfile['pills'] + pill}})
			return "Pills have been temporarily disabled. Don't worry; pills are still being counted!" #userProfile['pills'] + pill

	return "Pills have been temporarily disabled. Don't worry; pills are still being counted!" #userProfile['pills']


def removePill(user, string):
	dataBased = connectMongo()

	# Parse data and get the bare string
	delete = string.lower().replace('/removepill ', '')

	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		return 'You do not have any pills!'
	oldPills = userProfile['pills']

	# Check if pill exists and try to delete
	if (', ' + delete + ',') in oldPills:
		pills = oldPills.replace(', ' + delete + ',', ',')
	elif oldPills.startswith(delete):
		pills = oldPills[len(delete):]
	elif oldPills.endswith(delete):
		pills = oldPills[:-len(delete)]
	else:
		return "I didn't see that pill in your list."

	# Clean pill list to fix the hole
	if pills.startswith(', '):
		pills = pills[2:]
	if pills.endswith(', '):
		pills = pills[:-2]
	if ", , " in pills:
		pills = pills.replace(", , ", ", ")
	if ", ," in pills:
		pills = pills.replace(", ,", ", ")
	if "  " in pills:
		pills = pills.replace("  ", " ")
	if pills == '':
		pills = 'None'
	dataBased.update_one({'name': user}, {'$set': {'pills': pills}})

	# Build Reply Message
	return "Pill removed. Your pills: " + pills