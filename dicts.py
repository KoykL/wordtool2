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
class CibaDict:
	def __init__(BaseDict):
		pass
	def getDef(self, word):
		query = urllib.parse.quote_plus(word)
		with urllib.request.urlopen('http://www.iciba.com/{query}'.format(query=query)) as f:
			soup = bs4.BeautifulSoup(f, "lxml")
			defPropEs = soup.select('#dict_main .group_pos > p > .fl')
			defEs = soup.select('#dict_main .group_pos > p > .label_list > label')
			defProps = [str(defPropE.string) for defPropE in defPropEs]
			defs = [str(defE.string) for defE in defEs]
			defFull = [defProp + ' ' + definition for defProp, definition in zip(defProps, defs)]
			return defFull