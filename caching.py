import pymongo
class WordCache():
    def __init__(self, db):
        self._db = db
        self._db.cachedWords.create_index([("word", pymongo.DESCENDING),("type", pymongo.DESCENDING), ("tag", pymongo.DESCENDING)])
        pass
    def insertCache(self, word, T, tag, data):
        self._db.cachedWords.update({'word': word, "type": T, "tag": tag}, {'$set': {tag: data}}, upsert = True)
        pass
    def findCache(self, word, T, tag):
        doc = self._db.cachedWords.find({'word':word, 'type':T, "tag": tag}, {tag: True})
        return doc
