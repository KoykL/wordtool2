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
	def getWholeReviewListNotInReviewPack(self):
		return self._db.reviewlist.find({'username': self._username, 'inReviewPack': False})
	def _convertToReviewSysWordDocs(self, reviewWord):
		return {'username': self._username, 'word':reviewWord['word'], 'belongTo':reviewWord['belongTo']}
	def insertReviewSysPack(self, reviewPack):
		def getId(doc):
			return doc['_id']
		if not reviewPack:
			return
		self._db.reviewpacks.insert(map(self._convertToReviewSysWordDocs, reviewPack))
		ids = list(map(getId, reviewPack))
		self._db.reviewlist.update({'_id':{'$in': ids}}, {'$set': {'inReviewPack': True}}, multi=True)
	def getWord(self):
		try:
			return self._db.reviewpacks.find({'username': self._username}, {'word': True})[0]['word']
		except IndexError:
			return None
	def getWordDocFromReviewPackRandom(self):
		try:
			return self._db.reviewpacks.find({'username': self._username}, {'word': True, 'belongTo':True})[0]
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
	def removeReviewListWordsFromSingleList(self, collection, list, words):
		self._db.reviewpacks.remove({'word': {'$in': words}, 'belongTo.collection': collection, 'belongTo.list': list})
	def getWordDocFromReviewpack(self, collection, list, word):
		return self._db.reviewpacks.find({'username': self._username, 'word': word, 'belongTo.list':list, 'belongTo.collection':collection})[0]
	def getWordDoc(self, collection, list, word):
		return self._db.reviewlist.find({'username': self._username, 'word': word, 'belongTo.list':list, 'belongTo.collection':collection})[0]
	def reviewDone(self, collection, list, word):
		self._db.reviewlist.update({'username': self._username, 'word': word, 'belongTo.list': list, 'belongTo.collection': collection}, {'$set': {'lastTimeReview': time.time(), 'inReviewPack': False}, '$inc': {'reviewState': 1}})
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
		wholeReviewList = self._per.getWholeReviewListNotInReviewPack()
		shouldReviewList = list(filter(self._shouldReview, wholeReviewList))
		random.shuffle(shouldReviewList)
		self._per.insertReviewSysPack(shouldReviewList)
	def getWord(self):
		if self._per.reviewPackisExsisted():
			return self._per.getWord()
		else:
			self.createReviewPack()
			return self._per.getWord()
	def getWordDoc(self):
		if self._per.reviewPackisExsisted():
			return self._per.getWordDocFromReviewPackRandom()
		else:
			self.createReviewPack()
			return self._per.getWordDocFromReviewPackRandom()
	def getWords(self):
		if self._per.reviewPackisExsisted():
			return self._per.getWords()
		else:
			self.createReviewPack()
			return self._per.getWords()
	def addToReviewList(self, words, CollectionName, listNum):
		self._per.insertReviewList(words, CollectionName, listNum)
	#deprecated
	def _addSingleWordDoc(self, word):
		self._per.insertReviewSysPack([word])
	def removeReviewListWordsFromSingleList(self, collection, list, words):
		words = list(words)
		self._per.removeReviewListWordsFromSingleList( collection, list, words)
	def removeReviewListWordFromSingleList(self, collection, list, word):
		words = [word]
		self.removeReviewListWordsFromSingleList(collection, list, words)
	def reviewDone(self, collection, list, word):
		self._per.reviewDone(collection, list, word)
		self._per.cleanup()
	def isTotured(self, collection, list, word):
		doc = self._per.getWordDoc(collection, list, word)
		reviewState = doc['reviewState']
		if reviewState >= 7:
			return True
		else:
			return False
	#following is dirty
	def downRviewListWordPriority(self, collection, list, word):
		doc = self._per.getWordDocFromReviewpack(collection, list, word)
		self.removeReviewListWordFromSingleList(collection, list, word)#to do
		self._addSingleWordDoc(doc)
	