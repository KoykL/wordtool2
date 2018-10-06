import urllib.request
import urllib.parse
import bs4
import re
import caching
class BaseDict:
	def __init__(self, word):
		self.word = word
		pass
	def getData(self):
		raise NotImplementedError()
class YouDaoDict(BaseDict):
	def __init__(self, word):
		super().__init__(word)
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
		self.lazyInit()
		soup = self.soup
		defElements = soup.select('#phrsListTab > .trans-container > ul > li')
		defs = [str(defElement.string) for defElement in defElements]
		if defs == []:
				defs.append("")	
		return defs
	def getEgSentence(self):
		self.lazyInit()
		def extractSen(s):
			eng = " ".join(s.find_all("p")[0].stripped_strings)
			eng = re.sub(r'\s*\.',r'.',eng)
			chn = "".join(s.find_all("p")[1].stripped_strings)
			return (eng, chn)
		soup = self.soup
		senElements = soup.select('#bilingual > ul > li')
		sen = [extractSen(sen) for sen in senElements]
		if sen == []:
				sen.append(("",""))
		return sen
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
	def getData(self):
		return {
			"def": self.getDef(),
			"sen": self.getEgSentence()
		}

class CachedYouDaoDict(YouDaoDict):
	def __init__(self, word, db, wordCache):
		self.cache = wordCache
		super().__init__(word)
	def getCacheDef(self):
		word = self.word
		doc = self.cache.findCache(word=word, T="youdao", tag="Definition")
		try:
			doc = doc[0]
			doc["Definition"]
		except (IndexError, KeyError):
			return None
		else:
			d = doc['Definition']
			if d == [""]:
				return None
			else:
				return d	
	def getCacheSen(self):
		word = self.word
		doc = self.cache.findCache(word=word, T="youdao", tag="Example Sentence")
		try:
			doc = doc[0]
			doc["Example Sentence"]
		except (IndexError, KeyError):
			return None
		else:
			d = [tuple(each) for each in doc["Example Sentence"]]	
			if d == [("","")]:
				return None
			return d
	def setCacheDef(self, definition):
		word = self.word
		self.cache.insertCache(word, T="youdao", tag="Definition", data=definition)
	def setCacheSen(self, sentence):
		word = self.word
		self.cache.insertCache(word, T="youdao", tag="Example Sentence", data=[list(each) for each in sentence])
	def getDef(self):
		d = self.getCacheDef()
		if d:
			return d
		mydef = super().getDef()
		self.setCacheDef(mydef)
		return mydef
	def getEgSentence(self):
		d = self.getCacheSen()
		if d:
			return d
		sen = super().getEgSentence()
		self.setCacheSen(sen)
		return sen
	def getData(self):
		return {
			"def": self.getDef(),
			"sen": self.getEgSentence()
		}
class EtymDict(BaseDict):
	def __init__(self, word):
		super().__init__(word)
		self.inited = False
	def getSoup(self):
		word = self.word
		with urllib.request.urlopen('https://www.etymonline.com/word/{word}'.format(word=word)) as f:
			#self.soup = bs4.BeautifulSoup(f, "lxml")
			self.soup = bs4.BeautifulSoup(f, "html.parser")
	def lazyInit(self):
		if not self.inited:
			self.getSoup()
			self.inited = True
	def getEtym(self):
		self.lazyInit()
		soup = self.soup
		secs = soup.find_all('section')
		etym = ' '.join(secs[0].stripped_strings) if len(secs) > 0 else ''
		return etym
	def getData(self):
		return {
			"etym": self.getEtym()
		}

class CachedEtymDict(EtymDict):
	def __init__(self, word, db, wordCache):
		self.cache = wordCache
		super().__init__(word)
	def getCacheEtym(self):
		word = self.word
		doc = self.cache.findCache(word=word, T="etymoline", tag="etym")
		try:
			doc = doc[0]
			doc["etym"]
		except (IndexError, KeyError):
			return None
		else:
			d = doc['etym']
			if d == [""]:
				return None
			else:
				return d
	def setCacheEtym(self, etym):
		word = self.word
		self.cache.insertCache(word, T="etymoline", tag="etym", data=etym)
	def getEtym(self):
		d = self.getCacheEtym()
		if d:
			return d
		myetym = super().getEtym()
		self.setCacheEtym(myetym)
		return myetym
	def getData(self):
		return {
			"etym": self.getEtym(),
		}
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
