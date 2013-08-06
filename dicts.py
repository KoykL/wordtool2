import urllib.request
import urllib.parse
import bs4
import re
class BaseDict:
	def __init__(self):
		pass
	def getDef(self, word):
		raise NotImplementedError()
class YouDaoDict():
	def __init__(self, word):
		self.word = word
		self.inited = False
	def getSoup(self):
		query = urllib.parse.urlencode({'q':self.word})
		with urllib.request.urlopen('http://dict.youdao.com/search?{query}'.format(query=query)) as f:
			#self.soup = bs4.BeautifulSoup(f, "lxml")
			self.soup = bs4.BeautifulSoup(f, "html.parser")
	def lazyInit(self):
		if not self.inited:
			self.getSoup()
			self.inited = True
	def getDef(self):
		lazyInit()
		soup = self.soup
		defElements = soup.select('#phrsListTab > .trans-container > ul > li')
		defs = [str(defElement.string) for defElement in defElements]
		return defs
	def getEgSentence(self):
		lazyInit()
		def extractSen(s):
			eng = " ".join(s.find_all("p")[0].stripped_strings)
			eng = re.sub(r'\s*\.',r'.',eng)
			chn = "".join(s.find_all("p")[1].stripped_strings)
			return (eng, chn)
		soup = self.soup
		senElements = soup.select('#bilingual > ul > li')
		return [extractSen(sen) for sen in senElements]
	def getDefAndEgSen(self):
		defs = self.getDef(word)
		sen = self.getDef(word)
		if (defs != None) and (sen != None):
			d = {
				"Definition": defs,
				"Example Sentence": sen
			}
			return d
		else:
			return None
class CachedYouDaoDict(YouDaoDict):
	def __init__(self, db):
		self._db = db
		super().__init__(word)
	def getCacheDef(self, word):
		doc = self._db.cachedWords.find({'word':word}, {'Definition': True})
		if doc:
			doc = doc[0]
			d = doc['Definition'],
			return d
		else:
			return None
	def getCacheSen(self, word):
		doc = self._db.cachedWords.find({'word':word}, {'Example Sentence': True})
		if doc:
			doc = doc[0]
			d = [tuple(each) for each in doc["Example Sentence"]]
			return d
		else:
			return None
	def getCache(self, word):
		defs = self.getCacheDef(word)
		sen = self.getCacheSen(word)
		if (defs != None) and (sen != None):
			d = {
				"Definition": defs,
				"Example Sentence": sen
			}
			return d
		else:
			return None
	def setCacheDef(self, word, definition):
		self._db.cachedWords.update({'word': word}, {'$set': {'Definition': definition}}, {'upsert': True})
	def setCacheSen(self, word, sentence):
		self._db.cachedWords.update({'word': word}, {'$set': {'Example Sentence': [list(each) for each in sentence]}}, {'upsert': True})
	def getDef(self, word):
		d = self.getCacheDef(word)
		if d:
			return d
		mydef = super().getDef()
		self.setCacheDef(word, mydef)
		return mydef
	def getEgSentence(self, word):
		d = self.getCacheSen(word)
		if d:
			return d
		sen = super().getEgSentence()
		self.setCacheSen(word, sen)
		return sen
	def getDefAndEgSen(self):
		raise NotImplementedError()
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