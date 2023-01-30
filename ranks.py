# Rank Objects and Functions

class Rank:
	def __init__(self, value, name, message):
		self.value = value
		self.name = name
		self.message = message

def rankName(count, user):
	rank = ' '
	for r in rankList:
		if count >= r.value:
			rank = r.name
	if count >= 10000:
		rank = "u/" + str(user) + "'s Mom"
	return rank

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
add(	20		, 	'Basketball Hoop (filled with sand)'	, 	'You are not a pushover by any means, but you do still occasionally get dunked on.')
add(	35		, 	'Sumo Wrestler'							, 	'You are adept in the ring, but you still tend to rely on simply being bigger than the competition.')
add(	50		, 	'Concrete Foundation'					, 	'You are acceptably based, but beware of leaks...')
add(	75		, 	'Giant Sequoia'							, 	'I am not sure how many people it would take to dig you up, but that root system extends quite deep.')
add(	100		, 	'Empire State Building'					, 	'Some say there is a hidden river that still runs through your base. Shall we go digging?')
add(	200		, 	'Great Pyramid of Giza'					, 	'You once spent thousands of years as the tallest man-made object, but your ass is still square.')
add(	350		, 	'NASA Vehicle Assembly Building'		, 	'Famous for housing the Saturn V, you are one of the largest buildings by volume ever built.')
add(	500		, 	'Boeing Everett Factory'				, 	'You are the largest building ever created by man!')
add(	750		, 	'Mount Fuji'							, 	'The people of Tokyo often stare at you in wonder.')
add(	1000	, 	'Denali'								, 	'You are the largest mountain in North America.')
add(	2000	, 	'Annapurna'								, 	'You were the first 8000m mountain ever summited, and many climbers have died trying to best you.')
add(	3500	, 	'Mount Everest'							, 	'You are the tallest and most famous mountain in the world!')
add(	5000	, 	'Mauna Kea'								, 	'You have an absolutely massive base extending all the way from deep in the floor of the Pacific Ocean.')
add(	7500	, 	'Olympus Mons'							, 	'With 5km-tall sides created by a shield volcano over several million years, your base is unimaginably huge!')
add(	10000	, 	'Top Rank'								, 	"There really is nothing larger or more basic in the entire universe! It's fucking beautiful.")


