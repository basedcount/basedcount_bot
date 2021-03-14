# User Commands Library

# Python Libraries
import json
from collections import Counter
from random import randint

# basedcount_bot Libraries
import ranks
from passwords import savePath

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

	# Retrieve Data
	mostCountFlair = []
	with open(savePath + 'dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)
	cnt = Counter()
	for k, v in basedCountDatabase['users'].items():
		cnt[k] = int(v['count'])

	# Build Most Based List
	mostBasedList = cnt.most_common(10)
	for u in range(len(mostBasedList)):
		if mostBasedList[u][0] in basedCountDatabase['users']:
			mostUserName = mostBasedList[u][0]
			mostCount = str(basedCountDatabase['users'][mostUserName]['count'])
			try:
				mostFlair = str(basedCountDatabase['users'][mostUserName]['flair'])
			except:
				mostFlair = 'Flair Not Recorded'
			if mostFlair in 'Unflaired':
				mostFlair = 'Unflaired Scum'
			mostCountFlair.append(str(str(u + 1) + '. ' + mostUserName + '  |  ' + mostCount + '  |  ' + mostFlair + '\n\n'))

	# Build Reply Message
	replyMessage = '--The Top 10 Most Based Users--\n\n' + mostCountFlair[0] + mostCountFlair[1] + mostCountFlair[2] + mostCountFlair[3] + mostCountFlair[4] + mostCountFlair[5] + mostCountFlair[6] + mostCountFlair[7] + mostCountFlair[8] + mostCountFlair[9]
	cnt.clear()
	return replyMessage



# === Databased Searching and Updating ===

def addBasedCount(user, flair):
	with open(savePath + 'dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)

	# Check if existing user and calculate based count
	if user not in basedCountDatabase['users']:
		count = 1
		basedCountDatabase['users'][user] = {}
	else:
		count = int(basedCountDatabase['users'][user]['count']) + 1

	# Update databased
	if 'count' not in str(basedCountDatabase['users'][user]):
		basedCountDatabase['users'][user] = {'count':str(count)}
	else:
		basedCountDatabase['users'][user]['count'] = str(count)
	basedCountDatabase['users'][user]['flair'] = flair
	with open(savePath + 'dataBased.json', 'w') as dataBased:
		json.dump(basedCountDatabase, dataBased)
	return count


def checkBasedCount(user):
	with open(savePath + 'dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)

	# Check if existing user and calculate based count
	if user not in basedCountDatabase['users']:
		count = 0
	else:
		count = int(basedCountDatabase['users'][user]['count'])
	return count


def checkPills(user):
	with open(savePath + 'dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)

	# Check if existing user and calculate pill list
	if user not in basedCountDatabase['users']:
		return 'None'
	if 'pills' not in basedCountDatabase['users'][user]:
		return 'None'
	return str(basedCountDatabase['users'][user]['pills'])


def addPills(user, pill):
	with open(savePath + 'dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)

	# Check if user exists
	if user not in basedCountDatabase['users']:
		return 'None'

	# Build pill list
	if pill != 'None':

		# User doesn't have any previous pill data
		if 'pills' not in basedCountDatabase['users'][user]:
			basedCountDatabase['users'][user]['pills'] = {}
			basedCountDatabase['users'][user]['pills'] = pill
			with open(savePath + 'dataBased.json', 'w') as dataBased:
				json.dump(basedCountDatabase, dataBased)
			return pill

		# User has previous pill data
		oldPills = str(basedCountDatabase['users'][user]['pills'])

		# Check for duplicates, then add and save
		if (((', ' + pill + ',') not in oldPills) and not oldPills.endswith(', ' + pill)):
			basedCountDatabase['users'][user]['pills'] = oldPills + ', ' + pill
			with open(savePath + 'dataBased.json', 'w') as dataBased:
				json.dump(basedCountDatabase, dataBased)
			pills = oldPills + ', ' + pill
		else:
			pills = oldPills
		return pills

	# Retrieve pill data for reply message without adding new pill data
	else:
		if 'pills' in basedCountDatabase['users'][user]:
			return basedCountDatabase['users'][user]['pills']
		return 'None'


def removePill(user, string):

	# Parse data and get the bare string
	delete = string.lower().replace('/removepill ', '')

	with open(savePath + 'dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)
	oldPills = str(basedCountDatabase['users'][user]['pills'])

	# Check if pill exists and try to delete
	if delete in oldPills:
		pills = oldPills.replace(delete, '')
	else:
		return "I didn't see that pill in your list."

	# Clean pill list to fix the hole
	if pills.startswith(', '):
		pills = pills[2:]
	if pills.endswith(', '):
		pills = pills[:-2]
	if ", , " in pills:
		pills = pills.replace(", , ", ", ")
	basedCountDatabase['users'][user]['pills'] = pills

	with open(savePath + 'dataBased.json', 'w') as dataBased:
			json.dump(basedCountDatabase, dataBased)

	# Build Reply Message
	return "Pill removed. Your pills: " + pills