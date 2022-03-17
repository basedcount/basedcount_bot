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

politicalCompass_variations = ['https://www.politicalcompass.org/yourpoliticalcompass?ec=',
								'https://politicalcompass.org/yourpoliticalcompass?ec=',
								'https://www.politicalcompass.org/analysis2?ec=',
								'https://politicalcompass.org/analysis2?ec=',
								'politicalcompass.org/analysis2?ec=',
								'politicalcompass.org/yourpoliticalcompass?ec=',
								'www.politicalcompass.org/analysis2?ec=',
								'www.politicalcompass.org/yourpoliticalcompass?ec=',
								]

sapplyCompass_variations = ['https://sapplyvalues.github.io/results.html?right=',
							'sapplyvalues.github.io/results.html?right=']

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
	compass = checkCompass(user)

	# Build Reply Message
	replyMessage = ''
	if ((int(count)%5) == 0):
		replyMessage = "u/" + user + "'s Based Count has increased by 1. Their Based Count is now " + str(count) + '. \n\n Rank: '+ rank + '\n\n Pills: ' + pills + "\n\n" + 'Compass: ' + compass + "\n\n I am a bot. Reply /info for more info."
		if rankUp:
			replyMessage = "u/" + user + "'s Based Count has increased by 1. Their Based Count is now " + str(count) + '. \n\n Congratulations, u/' + user + "! You have ranked up to " + rank + '! ' + rankUp + '\n\n Pills: ' + pills + "\n\n" + 'Compass: ' + compass + "\n\n I am a bot. Reply /info for more info."
	elif int(count) == 1:
		replyMessage = 'u/' + user + " is officially based! Their Based Count is now 1. \n\n Rank: House of Cards"  + '\n\n Pills: ' + pills + "\n\n" + 'Compass: ' + compass + "\n\n I am a bot. Reply /info for more info."
	return replyMessage


def myBasedCount(user):

	# Retrieve User Data
	count = str(checkBasedCount(user))
	pills = checkPills(user)
	compass = checkCompass(user)

	# Build Reply Message
	if int(count) > 0:
		rank = ranks.rankName(int(count), user)
		replyMessage = "Your Based Count is " + count + ". \n\n" + 'Rank: ' + rank + "\n\n" + 'Pills: ' + pills + "\n\n" + 'Compass: ' + compass
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
	compass = checkCompass(user)

	# Build Reply Message
	if int(count) > 0:
		rank = ranks.rankName(int(count), user)
		replyMessage = user + "'s Based Count is " + count + ". \n\n" + 'Rank: ' + rank + "\n\n" + 'Pills: ' + pills + "\n\n" + 'Compass: ' + compass
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


def myCompass(user, compass):
	dataBased = connectMongo()
	# Check if existing user
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		dataBased.update_one({'name': user}, {'$set': {'flair': 'Unflaired', 'count': 0, 'pills': [], 'compass': [], 'sapply': []}}, upsert=True)

	compass = compass.lower().replace('/mycompass ', '')

	# Parse data from PoliticalCompass.org
	for pcv in politicalCompass_variations:
		if compass.startswith(pcv):
			compass = compass.replace(pcv,'')
			axes_values = compass.split('&soc=')
			dataBased.update_one({'name': user}, {'$set': {'compass': axes_values}})
			eco = axes_values[0]
			soc = axes_values[1]

			# Determine if lib/auth and left/right
			ecoType = quadrantName(eco, 'Left', 'Right')
			socType = quadrantName(soc, 'Lib', 'Auth')
			return 'Your political compass has been updated.\n\nCompass: ' + socType + ' | ' + ecoType

	# Parse data from SapplyValues.github.io
	for scv in sapplyCompass_variations:
		if compass.startswith(scv):
			compass = compass.replace(scv,'')
			url_split = compass.split('&auth=')
			eco = url_split[0]
			url_split2 = url_split[1].split('&prog=')
			soc = url_split2[0]
			prog = url_split2[1]
			sapply_values = [prog, soc, eco]
			dataBased.update_one({'name': user}, {'$set': {'sapply': sapply_values}})

			# Determine if lib/auth and left/right and prog/cons
			ecoType = quadrantName(eco, 'Left', 'Right')
			socType = quadrantName(soc, 'Lib', 'Auth')
			progType = quadrantName(soc, 'Conservative', 'Progressive')
			return 'Your Sapply compass has been updated.\n\nSapply: ' + socType + ' | ' + ecoType + ' | ' + progType
	return "Sorry, but that isn't a valid URL. Please copy/paste the entire test result URL from politicalcompass.org or sapplyvalues.github.io, starting with 'https'."



# === Databased Searching and Updating ===

def addBasedCount(user, flair):
	dataBased = connectMongo()
	# Check if existing user and calculate based count
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		dataBased.update_one({'name': user}, {'$set': {'flair': flair, 'count': 1, 'pills': [], 'compass': [], 'sapply': []}}, upsert=True)
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
	return "https://basedcount.com/u/" + user #str(userProfile['pills'])


def addPills(user, pill):
	dataBased = connectMongo()

	# Check if user exists
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		return 'None'

	if pill != 'None':
		# User doesn't have any previous pill data
		if userProfile['pills'] == []:
			dataBased.update_one({'name': user}, {'$push': {'pills': pill}})
			return "https://basedcount.com/u/" + user #pill

		# User has previous pill data
		oldPills = []
		for p in userProfile['pills']:
			try:
				oldPills.append(p['name'])
			except:
				print(user)
				print(pill)
				print(p)
				oldPills.append(p)

		# Check for duplicates, then add and save
		if (pill not in oldPills):
			dataBased.update_one({'name': user}, {'$push': {'pills': pill}})
			return "https://basedcount.com/u/" + user #userProfile['pills'] + pill

	return "https://basedcount.com/u/" + user #userProfile['pills']


def removePill(user, string):
	dataBased = connectMongo()

	# Parse data and get the bare string
	delete = string.lower().replace('/removepill ', '')

	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		return 'You do not have any pills!'
	oldPills = []
	for p in userProfile['pills']:
		oldPills.append(p['name'])

	# Check if pill exists and try to delete
	if (delete not in oldPills):
		return "I didn't see that pill in your list."

	for p in userProfile['pills']:
		if p['name'] == delete:
			dataBased.update_one({'name': user}, {'$pull': {'pills': {'name': delete}}})

	# Build Reply Message
	return "Pill removed. Your pills: " + "https://basedcount.com/u/" + user


def checkCompass(user):
	dataBased = connectMongo()
	# Check if existing user and retrieve compass
	userProfile = dataBased.find_one({'name':user})
	if userProfile == None:
		return 'I did not find that user.'
	compassReply = ''

	# Try to get compass data
	try:
		PCeco = userProfile['compass'][0]
		PCsoc = userProfile['compass'][1]
		PCecoType = quadrantName(PCeco, 'Left', 'Right')
		PCsocType = quadrantName(PCsoc, 'Lib', 'Auth')
		compassReply = 'Compass: ' + PCsocType + ' | ' + PCecoType + '\n\n'
	except:
		pass

	# Try to get sapply data
	try:
		SVeco = userProfile['sapply'][0]
		SVsoc = userProfile['sapply'][1]
		SVprog = userProfile['sapply'][2]

		SVecoType = quadrantName(SVeco, 'Left', 'Right')
		SVsocType = quadrantName(SVsoc, 'Lib', 'Auth')
		SVprogType = quadrantName(SVprog, 'Conservative', 'Progressive')
		compassReply = compassReply + 'Sapply: ' + SVsocType + ' | ' + SVecoType + ' | ' + SVprogType
	except:
		pass
	if compassReply == '':
		return 'This user does not have a compass on record. You can add your compass to your profile by replying with /mycompass politicalcompass.org url or sapplyvalues.github.io url.'
	return compassReply



# === Utils ===

def quadrantName(value, side1, side2):
	if ('-' in value):
		value = value.replace('-', '')
		return side1 + ': ' + value
	else:
		return side2 + ': ' + value