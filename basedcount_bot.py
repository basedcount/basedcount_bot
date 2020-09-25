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
from commands import based, myBasedCount, basedCountUser, mostBased
from flairs import checkFlair
from admin import commandsList
from passwords import bot, savePath, backupSavePath


# Connect to Reddit
reddit = praw.Reddit(client_id=bot.client_id,
			client_secret=bot.client_secret,
			user_agent=bot.user_agent,
			username=bot.username,
			password=bot.password)

# Parameters
subreddit = reddit.subreddit('politicalcompassmemes')
version = 'Bot v2.2.1'
infoMessage = 'I am a bot created to keep track of how based users are. If you have any suggestions or questions, please message them to me with the subject of "Suggestion" or "Question" to automatically forward them to a human operator. You can also check out the [FAQ](https://reddit.com/r/basedcount_bot/comments/iwhkcg/basedcount_bot_info_and_faq/).\n\n> based - adj. - to be in possession of viewpoints acquired through logic or observation rather than simply following what your political alignment dictates, often used as a sign of respect but not necessarily agreement\n\n' + version + '\n\n Commands: /info | /mybasedcount | /basedcount username | /mostbased'

# Vocabulary
excludedAccounts = ['basedcount_bot', 'VredditDownloader']
excludedParents = ['basedcount_bot']
botName_Variations = ['basedcount_bot', 'u/basedcount_bot', '/u/basedcount_bot']
based_Variations = ['based', 'baste']
myBasedCount_Variations = ['/mybasedcount']
basedCountUser_Variations = ['/basedcount']
mostBased_Variations = ['/mostbased']



def checkMail():
	inbox = reddit.inbox.unread(limit=30)
	for message in inbox:
		message.mark_read()
		currentTime = datetime.now().timestamp()
		if ((message.created_utc > (currentTime-180)) and (message.was_comment is False)):
			content = str(message.body)

# --------- Check Questions and Suggestions and then reply
			if (str(message.subject).lower() in 'suggestion') or (str(message.subject).lower() in 'question'):
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
					if commenttext.startswith(v):
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
						if parentAuthor not in excludedParents:

							# Check for cheating
							cheating = False
							for v in based_Variations:
								if parentText.lower().startswith(v):
									cheating = True

							# Calculate based count and decide what to reply
							if not cheating:
								replyMessage = based(parentAuthor, flair)
								if replyMessage:
									comment.reply(replyMessage)
								break

# ------------- Commands
				if commenttext.lower().startswith('/info'):
					comment.reply(infoMessage)

				for v in myBasedCount_Variations:
					if commenttext.lower().startswith(v):
						replyMessage = myBasedCount(author)
						comment.reply(replyMessage)
						break

				for v in basedCountUser_Variations:
					if commenttext.lower().startswith(v):
						replyMessage = basedCountUser(commenttext)
						comment.reply(replyMessage)
						break

				for v in mostBased_Variations:
					if commenttext.lower().startswith(v):
						replyMessage = mostBased()
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
	with open(backupSavePath + 'dataBased.json', 'w') as dataBased:
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
