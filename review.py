import datetime
import time
import random
class ReviewStateMapper:
	def __init__(self):
		self.mapper = {
			'0': datetime.timedelta(minutes=5),
			'1': datetime.timedelta(minutes=30),
			'2': datetime.timedelta(hours=12),
			'3': datetime.timedelta(days=1),
			'4': datetime.timedelta(days=2),
			'5': datetime.timedelta(days=4),
			'6': datetime.timedelta(days=7),
			'7': datetime.timedelta(days=15),
		}
	def convertToIntervalSec(self, state):
		state= str(state)
		return self.mapper[state].total_seconds()
class listWordExistedError(Exception):
	def __init__(self):
		pass
class reviewListPersistence:
	def __init__(self, username, db):
		self._username = username
		self._db = db
	def cleanup(self):
		self._db.reviewlist.remove({'reviewState': {'$gte': 8}})
	def getWholeReviewList(self):
		return self._db.reviewlist.find({'username': self._username})
	def _convertToReviewSysWordDocs(self, reviewWord):
		return {'username': self._username, 'word':reviewWord['word']}
	def insertReviewSysPack(self, reviewPack):
		if not reviewPack:
			return
		self._db.reviewpacks.insert(map(self._convertToReviewSysWordDocs, reviewPack))
	def getWord(self):
		try:
			return self._db.reviewpacks.find({'username': self._username}, {'word': True})[0]['word']
		except IndexError:
			return None
	def getWords(self):
		def mapper(doc):
			return doc['word']
		return map(mapper, self._db.reviewpacks.find({'username': self._username}, {'word': True}))
	def reviewPackisExsisted(self):
		try:
			self._db.reviewpacks.find({'username': self._username}, {'_id': True})[0]
		except IndexError:
			return False
		else:
			return True
	def _reviewListisExisisted(self, collection, listnum):
		try:
			self._db.reviewlist.find({'belongTo.collection': collection, 'belongTo.list': listnum})[0]
		except IndexError:
			return False
		else:
			return True
	def insertReviewList(self, words, CollectionName, listNum):	
		def mapper(collection, listnum):
			currentTime = time.time()
			return lambda word: {'username': self._username, 'reviewState': 0, 'lastTimeReview': currentTime, 'belongTo':{'collection': collection, 'list': listnum}, 'word': word}	
		exsisted = self._reviewListisExisisted(CollectionName, listNum)
		if exsisted:
			raise listWordExistedError()
		else:
			docs = map(mapper(CollectionName, listNum), words)
			self._db.reviewlist.insert(docs)
	def removeReviewListWords(self, words):
		self._db.reviewpacks.remove({'word': {'$in': words}})	
	def getWordDocPack(self, word):
		return self._db.reviewpacks.find({'username': self._username, 'word': word})[0]
	def getWordDoc(self, word):
		return self._db.reviewlist.find({'username': self._username, 'word': word})[0]
	def reviewDone(self, word):
		self._db.reviewlist.update({'username': self._username, 'word': word}, {'$set': {'lastTimeReview': time.time()}, '$inc': {'reviewState': 1}})
class Review:
	def __init__(self, db, username):
		self._per = reviewListPersistence(username, db)
		self._mapper = ReviewStateMapper()
	def _shouldReview(self, doc):
		incTime = self._mapper.convertToIntervalSec(int(doc['reviewState']))
		lastTimeReview = doc['lastTimeReview']
		nextTimeReview = lastTimeReview + incTime
		currentTime = time.time()
		if currentTime >= nextTimeReview:
			return True
		else:
			return False
	def createReviewPack(self):
		wholeReviewList = self._per.getWholeReviewList()
		shouldReviewList = list(filter(self._shouldReview, wholeReviewList))
		random.shuffle(shouldReviewList)
		self._per.insertReviewSysPack(shouldReviewList)
	def getWord(self):
		if self._per.reviewPackisExsisted():
			return self._per.getWord()
		else:
			self.createReviewPack()
			return self._per.getWord()
	def getWords(self):
		if self._per.reviewPackisExsisted():
			return self._per.getWords()
		else:
			self.createReviewPack()
			return self._per.getWords()
	def addToReviewList(self, words, CollectionName, listNum):
		self._per.insertReviewList(words, CollectionName, listNum)
	def _addSingleWordDoc(self, word):
		self._per.insertReviewSysPack([word])
	def removeReviewListWords(self, words):
		words = list(words)
		self._per.removeReviewListWords(words)
	def removeReviewListWord(self, word):
		words = [word]
		self.removeReviewListWords(words)
	def reviewDone(self, word):
		self._per.reviewDone(word)
		self._per.cleanup()
	def downRviewListWordPriority(self, word):
		doc = self._per.getWordDocPack(word)
		self.removeReviewListWord(word)
		self._addSingleWordDoc(doc)
	def isTotured(self, word):
		doc = self._per.getWordDoc(word)
		reviewState = doc['reviewState']
		if reviewState >= 7:
			return True
		else:
			return False