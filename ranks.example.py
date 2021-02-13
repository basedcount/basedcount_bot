# Rank Objects and Functions

class Rank:
	def __init__(self, value, name, message):
		self.value = value
		self.name = name
		self.message = message

# Retrieve Rank Name
def rankName(count, user):
	rank = ' '
	for r in rankList:
		if count >= r.value:
			rank = r.name
	return rank

# Retrieve Rank-Up Message
def rankMessage(count):
	rankMessage = ''
	for r in rankList:
		if count == r.value:
			rankMessage = r.message
	return rankMessage

# Add ranks to list
rankList = []
def add(value, name, message):
	rankList.append(Rank(value, name, message))

#	 ---Value---	    ---Rank Name---								---Rank Message---
add(	0		, 	'House of Cards'						, 	"You are technically standing, but don't shake the table.")
add(	5		, 	'Sapling'								, 	'You are not particularly strong but you are at least likely to handle a steady breeze.')
add(	10		, 	'Office Chair'							, 	'You cannot exactly be pushed over, but perhaps if thrown...')
add(	20		, 	'Basket Ball Hoop (filled with sand)'	, 	'You are not a pushover by any means, but you do still occasionally get dunked on.')
add(	35		, 	'Sumo Wrestler'							, 	'You are adept in the ring, but you still tend to rely on simply being bigger than the competition.')
add(	50		, 	'Concrete Foundation'					, 	'You are acceptably based, but beware of leaks...')
add(	75		, 	'Giant Sequoia'							, 	'I am not sure how many people it would take to dig you up, but that root system extends quite deep.')
add(	100		, 	'Empire State Building'					, 	'Some say there is a hidden river that still runs through your base. Shall we go digging?')
add(	200		, 	'Great Pyramid of Giza'					, 	'You once spent thousands of years as the tallest man-made object, but your ass is still square.')
add(	350		, 	'NASA Vehicle Assembly Building'		, 	'Famous for housing the Saturn V, you are one of the largest buildings by volume ever built.')
# And more...


