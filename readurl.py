from bs4 import BeautifulSoup
from urllib2 import urlopen

base_url = 'http://thecaucus.blogs.nytimes.com/2013/04/10/latest-updates-on-obamas-budget-proposal/?partner=rss&emc=rss'

def get_text():
	html = urlopen(base_url).read()
	soup = BeautifulSoup(html, 'lxml')

get_text()
print soup