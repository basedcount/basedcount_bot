# basedcount_bot ⣿
# FAQ: https://reddit.com/r/basedcount_bot/comments/iwhkcg/basedcount_bot_info_and_faq/

# Python Libraries
import json
import praw
from datetime import timedelta, datetime
import traceback
from subprocess import call
from os import path
from datetime import timedelta, datetime
import signal
import time

# basedcount_bot Libraries
from commands import based, myBasedCount, basedCountUser, mostBased, removePill
from flairs import checkFlair
from passwords import bot, bannedWords, modPasswords
from cheating import checkForCheating, sendCheatReport
from backupDrive import backupDataBased


# Connect to Reddit
reddit = praw.Reddit(client_id=bot.client_id,
			client_secret=bot.client_secret,
			user_agent=bot.user_agent,
			username=bot.username,
			password=bot.password)

# Parameters
subreddit = reddit.subreddit('PoliticalCompassMemes')
version = 'Bot v2.11.1'
infoMessage = 'I am a bot created to keep track of how based users are. '\
'Check out the [FAQ](https://reddit.com/r/basedcount_bot/comments/iwhkcg/basedcount_bot_info_and_faq/). '\
'I also track user [pills](https://reddit.com/r/basedcount_bot/comments/l23lwe/basedcount_bot_now_tracks_user_pills/).\n\n'\
'If you have any suggestions or questions, please message them to me with the subject '\
'of "Suggestion" or "Question" to automatically forward them to a human operator.\n\n'\
'> based - adj. - to be in possession of viewpoints acquired through logic or observation '\
'rather than simply following what your political alignment dictates, '\
'often used as a sign of respect but not necessarily agreement\n\n'\
+version+'\n\n'\
'**Commands: /info | /mybasedcount | /basedcount username | /mostbased | /removepill pill**'

# Vocabulary
excludedAccounts = ['basedcount_bot', 'VredditDownloader']
excludedParents = ['basedcount_bot']
botName_Variations = ['/u/basedcount_bot ', 'u/basedcount_bot ', 'basedcount_bot ', '/u/basedcount_bot', 'u/basedcount_bot', 'basedcount_bot']

based_Variations = ['based', 'baste', 'basado', 'basiert',
					'basato', 'fundiert', 'fondatum', 'bazita',
					'מבוסס', 'oparte', 'bazowane', 'basé', 'baseado',
					'gebaseerd', 'bazirano', 'perustuvaa', 'perustunut',
					'основано', '基于', 'baseret', 'بايسد, ',
					'na základě', 'basert', 'bazirano', 'baserad',
					'basat', 'ベース', 'bazat', 'berdasar', 'Базирано',
					'gebasseerd', 'Oj +1 byczq +1', 'Oj+1byczq+1']

pillExcludedStrings_start = ['based', 'baste', 'and ', 'but ', 'and-', 'but-', ' ', '-', 'r/', '/r/',
					'basado', 'basiert',
					'basato', 'fundiert', 'fondatum', 'bazita',
					'מבוסס', 'oparte', 'bazowane', 'basé', 'baseado',
					'gebaseerd', 'bazirano', 'perustuvaa', 'perustunut',
					'основано', '基于', 'baseret', 'بايسد, ',
					'na základě', 'basert', 'bazirano', 'baserad',
					'basat', 'ベース', 'bazat', 'berdasar', 'Базирано',
					'gebasseerd', 'Oj +1 byczq +1', 'Oj+1byczq+1']

pillExcludedStrings_end = [' and', ' but', ' ', '-']

myBasedCount_Variations = ['/mybasedcount']
basedCountUser_Variations = ['/basedcount']
mostBased_Variations = ['/mostbased']

time.sleep(10)
backupDataBased()
run = True

def checkMail():
	inbox = reddit.inbox.unread(limit=30)
	for message in inbox:
		if run == False:
				closeBot()
		message.mark_read()
		currentTime = datetime.now().timestamp()
		if ((message.created_utc > (currentTime-180)) and (message.was_comment is False)):
			content = str(message.body)
			author = str(message.author)

# --------- Check Questions and Suggestions and then reply
			if ('suggestion' in str(message.subject).lower()) or ('question' in str(message.subject).lower()):
				if str(message.subject).lower() in 'suggestion':
					message.reply('Thank you for your suggestion. I have forwarded it to a human operator.')
				if str(message.subject).lower() in 'question':
					message.reply('Thank you for your question. I have forwarded it to a human operator, and I should reply shortly with an answer.')
				reddit.redditor(bot.admin).message(str(message.subject) + ' from ' + author, content)

# --------- Check for mod commands
			for mpass in modPasswords:
				if (content.startswith(mpass.password)):
					if author == mpass.user:
						cleanContent = content.replace(mpass.password + ' ', '')
						if cleanContent.startswith('/removepill '):
							cleanContent = cleanContent.replace('/removepill ', '')
							user_pill_split = cleanContent.split(" ", 1)
							replyMessage = removePill(user_pill_split[0], user_pill_split[1])

# --------- Check for user commands
			if '/info' in content.lower():
					message.reply(infoMessage)

			for v in myBasedCount_Variations:
				if v in content.lower():
					replyMessage = myBasedCount(author)
					message.reply(replyMessage)
					break

			for v in basedCountUser_Variations:
				if v in content.lower():
					replyMessage = basedCountUser(content)
					message.reply(replyMessage)
					break

			for v in mostBased_Variations:
				if v in content.lower():
					replyMessage = mostBased()
					message.reply(replyMessage)
					break

			if content.lower().startswith('/removepill'):
				replyMessage = removePill(author, content)
				message.reply(replyMessage)



def readComments():
	try:
		for comment in subreddit.stream.comments(skip_existing=True):
			if run == False:
				closeBot()

			checkMail()

			# Get data from comment
			author = str(comment.author)
			if author not in excludedAccounts:
				commenttext = str(comment.body)

				# Remove bot mentions from comment text
				for v in botName_Variations:
					if v in commenttext:
						commenttext.replace(v, '')

# ------------- Based Check
				for v in based_Variations:
					if (commenttext.lower().startswith(v))and not (commenttext.lower().startswith('based on ') or commenttext.lower().startswith('based off ')):

						# Get data from parent comment
						parent = str(comment.parent())
						parentComment = reddit.comment(id=parent)

						#See if parent is comment (pass) or post (fail)
						try:
							parentAuthor = str(parentComment.author)
							parentTextHandler = parentComment.body
							parentText = str(parentTextHandler).lower()
							parentFlair = parentComment.author_flair_text
						except:
							parentAuthor = str(comment.submission.author)
							parentText = 'submission is a post'
							parentFlair = comment.submission.author_flair_text
						flair = str(checkFlair(parentFlair))

						# Make sure bot isn't the parent
						if (parentAuthor not in excludedParents) and (parentAuthor not in author) and (comment.author_flair_text != 'None'):

							# Check for cheating
							cheating = False
							for v in based_Variations:
								if parentText.lower().startswith(v) and (len(parentText) < 50):
									cheating = True

							# Check for pills
							pill = 'None'
							if 'pilled' in commenttext.lower():
								pill = commenttext.lower().partition('pilled')[0]
								if (len(pill) < 70) and ('.' not in pill):

									# Clean pill string beginning
									pillClean = 0
									while pillClean < len(pillExcludedStrings_start):
										for pes in pillExcludedStrings_start:
											if pill.startswith(pes):
												pill = pill.replace(pes, '', 1)
												pillClean = 0
											else:
												pillClean += 1

									# Clean pill string ending
									pillClean = 0
									while pillClean < len(pillExcludedStrings_end):
										for pes in pillExcludedStrings_end:
											if pill.endswith(pes):
												pill = pill[:-1]
												pillClean = 0
											else:
												pillClean += 1
								else:
									pill = 'None'

								# Make sure pill is acceptable
								for w in bannedWords:
									if w in pill:
										pill = 'None'

							# Calculate Based Count and build reply message
							if not cheating:
								if flair != 'Unflaired':
									replyMessage = based(parentAuthor, flair, pill)

									# Build list of users and send Cheat Report to admin
									checkForCheating(author, parentAuthor)

								# Reply
								else:
									break
									# replyMessage = "Don't base the Unflaired scum!"
								if replyMessage:
										comment.reply(replyMessage)
								break

# ------------- Commands
				if commenttext.lower().startswith('/info'):
					comment.reply(infoMessage)

				for v in myBasedCount_Variations:
					if v in commenttext.lower():
						replyMessage = myBasedCount(author)
						comment.reply(replyMessage)
						break

				for v in basedCountUser_Variations:
					if commenttext.lower().startswith(v):
						replyMessage = basedCountUser(commenttext)
						comment.reply(replyMessage)
						break

				for v in mostBased_Variations:
					if v in commenttext.lower():
						replyMessage = mostBased()
						comment.reply(replyMessage)
						break

				if commenttext.lower().startswith('/removepill'):
					replyMessage = removePill(author, commenttext)
					comment.reply(replyMessage)
					break



# - Exception Handler
	except praw.exceptions.APIException as e:
		if (e.error_type == "RATELIMIT"):
			delay = re.search("(\d+) minutes?", e.message)
			if delay:
				delay_seconds = float(int(delay.group(1)) * 60)
				time.sleep(delay_seconds)
				readComments()
			else:
				delay = re.search("(\d+) seconds", e.message)
				delay_seconds = float(delay.group(1))
				time.sleep(delay_seconds)
				readComments()
		else:
			print(e.message)



# Execute
def main():

	# Start
	try:
		checkMail()
		readComments()
		print('End Cycle')

	# Record info if an error is encountered
	except Exception:
		print('Error occurred:' + str(datetime.today().strftime('%Y-%m-%d')))
		traceback.print_exc()
	#main()


# Save dataBased when server shuts down
def handler_stop_signals(signum, frame):
	global run
	run = False

signal.signal(signal.SIGINT, handler_stop_signals)
signal.signal(signal.SIGTERM, handler_stop_signals)

def closeBot():
	sendCheatReport()
	print('Shutdown complete.')
	exit()


while run:
	main()