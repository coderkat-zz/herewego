# Grab full article text using Decruft's version of Readability (w/lxml)
# Run Decruft html through BeautifulSoup to remove all markup

from decruft import Document
import urllib2
from bs4 import BeautifulSoup

f = urllib2.urlopen('http://www.bbc.co.uk/news/world-22184232')

w = (Document(f.read()).summary())

soup = BeautifulSoup(w)

text = (soup.get_text())
return text

# was trying to get this saved to a .txt file: not actually necessary w/in 
# the functionality of my program, can pass it straight to my classification
# methods (as yescorpus, nocorpus, or testing) --> this will basically
# be used on every news article url we interact with 