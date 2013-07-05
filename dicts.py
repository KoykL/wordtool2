import urllib.request
import urllib.parse
import bs4
class BaseDict:
	def __init__(self):
		pass
	def getDef(self, word):
		raise NotImplementedError()
class YouDaoDict:
	def __init__(BaseDict):
		pass
	def getDef(self, word):
		query = urllib.parse.urlencode({'q':word})
		with urllib.request.urlopen('http://dict.youdao.com/search?{query}'.format(query=query)) as f:
			soup = bs4.BeautifulSoup(f, "lxml")
			defElements = soup.select('#phrsListTab > .trans-container > ul > li')
			defs = [str(defElement.string) for defElement in defElements]
			return defs