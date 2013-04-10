
from flask import Flask
import feedparser # python library that parses feeds in RSS, Atom, and RDF

nyt_rss = 'http://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml'

parse_nyt = feedparser.parse(nyt_rss)

# get a list of titles(list form, uhmmm fixit) in rss feed
titles = []
for i in range(len(parse_nyt.entries)):
	titles.append([parse_nyt.entries[i].title])

# get list of urls 
urls = []
for i in range(len(parse_nyt.entries)):
	urls.append([parse_nyt.entries[i].link])
print urls
