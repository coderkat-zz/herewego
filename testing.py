import requests

api_key = "6165aba5d247b43a9539e31e45def1b3c0881b7d"

r = requests.get('https://readability.com/api/content/v1/parser?token=api_key&url="http://blog.readability.com/2011/02/step-up-be-heard-readability-ideas/"')

print r
