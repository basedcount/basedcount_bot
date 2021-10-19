# Admin Commands Library

import json
from subprocess import call

class Command:
	def __init__(self, name, function):
		self.name = name
		self.function = function


# === Commands ===

def pingCommand(message, content=None):
	message.reply('Ping!')

def stopCommand(message, content=None):
	message.reply('Bot paused.')
	exit()

def shutdownCommand(message, content=None):
	message.reply('Bot deactivated. All functions terminated.')
	call("sudo shutdown -h now", shell=True)

def appendCommand(message, content):
	# Parse content for data
	if 'u/' in content:
		string = 'append u/'
	else:
		string = 'append '
	cleanContent = content.replace(string,'')
	contentSplit = cleanContent.split(' ', 1)
	user = contentSplit[0]
	count = contentSplit[1]

	# Update based count and reply
	with open('dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)
	if 'count' not in str(basedCountDatabase['users'][user]):
		basedCountDatabase['users'][user] = {'count':str(count)}
	else:
		basedCountDatabase['users'][user]['count'] = str(count)
	with open('dataBased.json', 'w') as dataBased:
		json.dump(basedCountDatabase, dataBased)
	message.reply('User u/' + user + ' updated with count: ' + count)

def checkCommand(message, content):
	if 'u/' in content:
		string = 'check u/'
	else:
		string = 'check '
	user = content.replace(string,'')

	try:
		with open('dataBased.json') as dataBased:
			basedCountDatabase = json.load(dataBased)
		message.reply('User u/' + user + ' count: ' + basedCountDatabase['users'][user]['count'])
	except:
		message.reply('I dont see that user in my records.')

def dataCommand(message, content=None):
	with open('dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)
	message.reply('Total Users: ' + str(len(basedCountDatabase['users'])))

def infoCommand(message, content=None):
	commandsString = ''
	for c in commandsList:
		commandsString = commandsString + ' | ' + c.name
	messageReply = 'Commands: ' + commandsString
	message.reply(messageReply)


# Add commands to list
commandsList = []
def add(name, function):
	commandsList.append(Command(name, function))

add('ping', pingCommand)
add('stop', stopCommand)
add('shutdown', shutdownCommand)
add('append', appendCommand)
add('check', checkCommand)
add('data', dataCommand)
add('info', infoCommand)
