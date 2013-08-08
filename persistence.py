import pymongo
import itertools
#This module is a transition between the structure used by underlying database and abstracted one used throughout wordtool.
class CollectionDatabase:
	def __init__(self):
		self._db = pymongo.MongoClient(w=0).wordtool
	def getCollectionDocs(self, username, optimize = {}):
		return self._db.collections.find({'username': username}, optimize)
	def getCollectionDocByName(self, username, collectionName,  optimize = {}):
		return self._db.collections.find({'username': username, 'collectionName': collectionName}, optimize)[0]
	def getCollectionDocByNameSliced(self, username, collectionName, slicedField, slice):
		return self._db.collections.find({'username': username,'collectionName': collectionName}, {slicedField: {'$slice': slice}})[0]
	def insertCollectionDoc(self, username, collectionName):
		return self._db.collections.insert({'collectionName': collectionName, 'username': username, 'listslen': 0, 'lists':[]})
	def removeCollectionDoc(self, username, collectionName):
		return self._db.collections.remove({'collectionName': collectionName, 'username': username})		
	def updateCollectionDoc(self, username, collectionName, updateSpec):
		return self._db.collections.update({'collectionName': collectionName, 'username': username}, updateSpec)
	def getUnderlyingDb(self):
		return self._db

	#review list part
class Persistence:
	def __init__(self):
		self._db = CollectionDatabase()
	#Read Region
	def collectionisExisted(self, username, collectionName):
		try:
			self._db.getCollectionDocByName(username, collectionName)
		except IndexError:
			return False
		else:
			return True
	def collectionisInited(self, username, collectionName):
		doc = self._db.getCollectionDocByName(username, collectionName, {'listslen': True})
		if int(doc['listslen']) == 0:
			return False
		else:
			return True
	def _getCollectionNameFromDoc(self, doc):
		return doc['collectionName']
	def _getPreviewFromDoc(self, doc):
		lists = doc['lists']
		iter = (word for list in lists for word in map(self._getWordNamePartFromDoc, list))
		return " ".join(itertools.islice(iter, 10))
	def _getWordNamePartFromDoc(self, doc):
		return doc['name']
	def _getCollectionNameAndPreviewFromDoc(self, doc):
		return (self._getCollectionNameFromDoc(doc), self._getPreviewFromDoc(doc))
	def getCollectionNames(self, username):
		collectionsDoc = self._db.getCollectionDocs(username, {'collectionName': True})
		collectionsDoc = collectionsDoc if collectionsDoc else []
		return map(self._getCollectionNameFromDoc, collectionsDoc)
	def getCollectionNamesAndPreview(self, username):
		collectionsDoc = self._db.getCollectionDocs(username, {'collectionName': True, 'lists': True})
		collectionsDoc = collectionsDoc if collectionsDoc else []
		return map(self._getCollectionNameAndPreviewFromDoc, collectionsDoc)
	def getList(self, username, collectionName, listNum):
		listIndex = listNum - 1
		docs= self._db.getCollectionDocByNameSliced(username, collectionName, 'lists', [listIndex, 1])['lists'][0]
		return map(self._getWordNamePartFromDoc, docs)
	def getListsLen(self, username, collectionName):
		doc = self._db.getCollectionDocByName(username, collectionName, {'listslen': True})
		return doc['listslen']
	#End of Read Region
	#Write Region
	def addList(self, username, collectionName):
		self._db.updateCollectionDoc(username, collectionName, {'$inc': {'listslen': 1}, '$push': {'lists': []}})
	def insertCollection(self, username, collectionName):
		self._db.insertCollectionDoc(username, collectionName)
	def removeCollection(self, username, collectionName):
		self._db.removeCollectionDoc(username, collectionName)
	def removeListByPos(self, username,collectionName, listNum):
		listIndex = listNum - 1
		listId = "lists.{listIndex}".format(listIndex=listIndex)
		self._db.updateCollectionDoc(username, collectionName, {'$unset': {listId: 1}})
		self._db.updateCollectionDoc(username, collectionName, {'$pull': {"lists": None}})
		self._db.updateCollectionDoc(username, collectionName, {'$inc': {"listslen": -1}})
	def addWord(self, username,collectionName, listNum, word):
		listIndex = listNum - 1
		listId = "lists.{listIndex}".format(listIndex=listIndex)
		wordCap = {'name': word}
		self._db.updateCollectionDoc(username, collectionName,{'$addToSet': {listId: wordCap}})
	def deleteWord(self, username,collectionName, listNum, word):
		#associated with refactor
		listIndex = listNum - 1
		listId = "lists.{listIndex}".format(listIndex=listIndex)
		listQueryId = "{listId}.name".format(listId=listId)
		listRemoveId = "{listId}.$".format(listId=listId)
		db = self.getUnderlyingDb()
		db.collections.update({'collectionName': collectionName, 'username': username,listQueryId: word}, {'$unset': {listRemoveId: 1}})
		db.collections.update({'collectionName': collectionName, 'username': username}, {'$pull': {listId: None}})
	#end of write region
	#Temporary solution. Refactoring needed: this exposed underlying database object.
	def getUnderlyingDb(self):
		return self._db.getUnderlyingDb()
