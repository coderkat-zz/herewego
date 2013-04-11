import model
import sqlalchemy.exc
import feedparser # python library that parses feeds in RSS, Atom, and RDF

sources = {"New York Times":'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml', "NPR News":'http://www.npr.org/rss/rss.php?id=1001', "BBC":'http://feeds.bbci.co.uk/news/rss.xml', "CNN":'http://rss.cnn.com/rss/cnn_topstories.rss'}

# seed db! open rss file, read it, parse it, create object, 
# add obj to session, commit, and repeat til done

def load_stories(source, session):
	# use feedparser to grab & parse the rss feed
	parsed = feedparser.parse(sources[source])
	# go through each entry in the RSS feed to pull out elements for Stories
	for i in range(len(parsed.entries)):
		title = parsed.entries[i].title
		url = parsed.entries[i].link
		source = source
		# pull abstract, parse out extra crap that is sometimes included 
		abstract = (parsed.entries[i].description.split('<'))[0]
		# connect with db
		story = model.Stories(title=title, url=url, abstract=abstract, source=source)
		# add story to db
		session.add(story)
		# commit 
		session.commit()
		
def load_tags(source, session):
	pass

def main(session):
	for item in sources:
		load_stories(item, session)

if __name__ == "__main__":
	s = model.session
	main(s)