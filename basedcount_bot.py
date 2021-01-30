# basedcount_bot
# FAQ: https://reddit.com/r/basedcount_bot/comments/iwhkcg/basedcount_bot_info_and_faq/

# Python Libraries
import json
import praw
from datetime import timedelta, datetime
import traceback
from subprocess import call
from os import path
from datetime import timedelta, datetime

# Custom Libraries
from commands import based, myBasedCount, basedCountUser, mostBased, removePill
from flairs import checkFlair
from admin import commandsList
from passwords import bot, savePath, backupSavePath
from cheating import checkForCheating, sendCheatReport


# Connect to Reddit
reddit = praw.Reddit(client_id=bot.client_id,
			client_secret=bot.client_secret,
			user_agent=bot.user_agent,
			username=bot.username,
			password=bot.password)

# Parameters
subreddit = reddit.subreddit('PoliticalCompassMemes')
version = 'Bot v2.5.2'
infoMessage = 'I am a bot created to keep track of how based users are. '
				+ 'Check out the [FAQ](https://reddit.com/r/basedcount_bot/comments/iwhkcg/basedcount_bot_info_and_faq/). '
				+ 'I also track user [pills](https://reddit.com/r/basedcount_bot/comments/l23lwe/basedcount_bot_now_tracks_user_pills/)'
				+ '\n\nIf you have any suggestions or questions, please message them to me with the subject '
				+ 'of "Suggestion" or "Question" to automatically forward them to a human operator. '
				+ '\n\n> based - adj. - to be in possession of viewpoints acquired through logic or observation '
				+ 'rather than simply following what your political alignment dictates, '
				+ 'often used as a sign of respect but not necessarily agreement'
				+ '\n\n' + version
				+ '\n\n**Commands: /info | /mybasedcount | /basedcount username | /mostbased | /removepill**'

# Vocabulary
excludedAccounts = ['basedcount_bot', 'VredditDownloader']
excludedParents = ['basedcount_bot']
botName_Variations = ['/u/basedcount_bot ', 'u/basedcount_bot ', 'basedcount_bot ', '/u/basedcount_bot', 'u/basedcount_bot', 'basedcount_bot']
based_Variations = ['based', 'baste']
myBasedCount_Variations = ['/mybasedcount']
basedCountUser_Variations = ['/basedcount']
mostBased_Variations = ['/mostbased']
bannedWords = ['nigger', 'nigga', 'negro', 'child', 'pedo', 'faggot', 'rape']



def checkMail():
	inbox = reddit.inbox.unread(limit=30)
	for message in inbox:
		message.mark_read()
		currentTime = datetime.now().timestamp()
		if ((message.created_utc > (currentTime-180)) and (message.was_comment is False)):
			content = str(message.body)

# --------- Check Questions and Suggestions and then reply
			if ('suggestion' in str(message.subject).lower()) or ('question' in str(message.subject).lower()):
				if str(message.subject).lower() in 'suggestion':
					message.reply('Thank you for your suggestion. I have forwarded it to a human operator.')
				if str(message.subject).lower() in 'question':
					message.reply('Thank you for your question. I have forwarded it to a human operator, and I should reply shortly with an answer.')
				reddit.redditor(bot.admin).message(str(message.subject) + ' from ' + str(message.author), content)

# --------- Check for admin commands
			if content.startswith(bot.mPassword):
				string = bot.mPassword + ' '
				cleanContent = content.replace(string,'')

				for c in commandsList:
					if cleanContent.startswith(c.name):
						c.function(message, cleanContent)

# --------- Check for user commands
			if '/info' in content.lower():
					message.reply(infoMessage)

			for v in myBasedCount_Variations:
				if v in content.lower():
					replyMessage = myBasedCount(message.author)
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
				replyMessage = removePill(message.author, content)
				message.reply(replyMessage)



def readComments():
	try:
		for comment in subreddit.stream.comments(skip_existing=True):
			checkMail()
			backupData()

			author = str(comment.author)
			if author not in excludedAccounts:
				commenttext = str(comment.body)

				# Remove bot mentions from comment text
				for v in botName_Variations:
					if v in commenttext:
						commenttext.replace(v, '')

# ------------- Based Check
				for v in based_Variations:
					if (commenttext.lower().startswith(v)) and not (commenttext.lower().startswith('based on') or commenttext.lower().startswith('based off')):

						# Get data from parent
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
						if (parentAuthor not in excludedParents) and (parentAuthor not in author):

							# Check for cheating
							cheating = False
							for v in based_Variations:
								if parentText.lower().startswith(v) and (len(parentText) < 50):
									cheating = True

							# Check for pills
							pill = 'None'
							if 'pilled' in commenttext.lower():
								pill = commenttext.partition('pilled')[0]
								if (len(pill) < 50) and ('.' not in pill):
									for v in based_Variations:
										if pill.lower().startswith(v):
											pill = pill.lower().replace(v, '')
									if pill.startswith(' and '):
										pill = pill.lower().replace(' and ', '')
									if pill.startswith(' but '):
										pill = pill.lower().replace(' but ', '')
									if pill[-1]=='-':
										pill = pill[:-1]
									if pill[-1]==' ':
										pill = pill[:-1]
									if pill[0]==' ':
										pill = pill[1:]
								for w in bannedWords:
									if w in pill:
										pill = 'None'

							# Calculate based count and decide what to reply
							if not cheating:
								if flair != 'Unflaired':
									replyMessage = based(parentAuthor, flair, pill)
									checkForCheating(author, parentAuthor)
									sendCheatReport()
								else:
									replyMessage = "Don't base the Unflaired scum!"
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



def backupData():
	with open(savePath + 'dataBased.json') as dataBased:
		basedCountDatabase = json.load(dataBased)
	with open(backupSavePath + 'dataBased.json' + str(datetime.now().date()), 'w') as dataBased:
		json.dump(basedCountDatabase, dataBased)



# Execute
def main():
	try:
		checkMail()
		readComments()
		backupData()
		print('End Cycle')
	except Exception:
		print('Error occurred:' + str(datetime.today().strftime('%Y-%m-%d')))
		traceback.print_exc()
	main()

main()