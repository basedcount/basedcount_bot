# |============|
# |   flairs   |
# |============|

class Flair:
	def __init__(self, name, tag):
		self.name = name
		self.tag = tag

def checkFlair(flair_text):
	if flair_text==None:
		return 'Unflaired'
	for f in range(len(flairList)):
		if flairList[f].tag in str(flair_text):
			return flairList[f].name
	return str(flair_text)

# Add flairs to list
flairList = []
def add(name, tag):
	flairList.append(Flair(name, tag))

add('Unflaired', 'None')
add('Grey Centrist', ':CENTG:')
add('Centrist', ':centrist:')
add('AuthCenter', ':auth:')
add('AuthLeft', ':authleft:')
add('AuthRight', ':authright:')
add('LibCenter', ':lib:')
add('LibLeft', ':libleft:')
add('LibRight', ':libright:')
add('Purple LibRight', ':libright2:')
add('Left', ':left:')
add('Right', ':right:')
