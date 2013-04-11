import model
import sqlalchemy.exc
import feedparser # python library that parses feeds in RSS, Atom, and RDF

# new york times rss for their news homepage
nyt = 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'

# npr rss news headlines
npr = 'http://www.npr.org/rss/rss.php?id=1001'

# bbc news rss top stories
bbc = 'http://feeds.bbci.co.uk/news/rss.xml'

#cnn rss top stories - will need extra parsing for 
# description from feedparser, they build it in with tons of 
# other shit
cnn = 'http://rss.cnn.com/rss/cnn_topstories.rss'


# use with NYT and CNN!
# grabs 'description' from feedparser and parses out actual
# abstract
# TODO: FIGURE OUT WHERE THIS FITS IN TO DB CONSTRUCTION
def isolate_desc(rss):
	description = (feedparser.parse(rss).entries[0].description.split('<'))[0]
	return description

# get a list of titles in rss feed
def titles(rss):
	titles = []
	# parse rss file
	parsed = feedparser.parse(rss)
	# return list of article titles from rss feed
	for i in range(len(parsed.entries)):
		titles.append(parsed.entries[i].title)
	return titles

# get list of urls 
def urls(rss):
	urls = []
	parsed = feedparser.parse(rss)
	# return list of article urls from rss feed
	for i in range(len(parsed.entries)):
		urls.append(parsed.entries[i].link)
	return urls

# seed db! open rss file, read it, parse it, create object, 
# add obj to session, commit, and repeat til done
#TODO: GET THIS TO WORK?!
def load_stories(source, session):
	parsed = feedparser.parse(source)
	for i in range(len(parsed.entries)):
		title = parsed.entries[i].title
		url = parsed.entries[i].link
		abstract = (parsed.entries[i].description.split('<'))[0]
		# story = model.Stories(title=title, url=url, abstract=abstract)
		# session.add(user)
		# session.commit()


def load_tags(session):
	pass


def main():
	load_stories(nyt)

if __name__ == "__main__":
	main()