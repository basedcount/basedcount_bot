# Sensitive and Important Data

class Bot:
	def __init__(self, client_id, client_secret, user_agent, username, password, admin, mPassword):
		self.client_id = client_id
		self.client_secret = client_secret
		self.user_agent = user_agent
		self.username = username
		self.password = password
		self.admin = admin
		self.mPassword = mPassword

bot = Bot()

savePath = '/Desktop/basedcount_bot/'
backupSavePath = '/Desktop/Backup/'