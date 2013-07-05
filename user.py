import hashlib
import random
class Userdb:
	def __init__(self, db):
		self._db = db
	def getUserDoc(self, username):
		try:
			return self._db.users.find({'_id': username})[0]
		except IndexError:
			return None
	def newUser(self, username, password):
		self._db.users.insert({'_id': username, 'password': password})
	def usernameTaken(self, username):
		if self.getUserDoc(username):
			return True
		else:
			return False
	def getPass(self, username):
		doc = self.getUserDoc(username)
		if doc:
			return doc['password']
		else:
			return ""
class User:
	def __init__(self, db):
		self._db=Userdb(db)
	def _calcHash(self, password):
		m = hashlib.sha512()
		m.update(bytes(password, "utf-8"))
		return m.hexdigest()
	def addSalt(self, password, salt):
		return password + salt
	def newUser(self, username, password):
		saltedpass = self.addSalt(password, username)
		hashedpass = self._calcHash(saltedpass)
		self._db.newUser(username, hashedpass)
	def comparePass(self, username, password):
		dbPass = self._db.getPass(username)
		saltedpass = self.addSalt(password, username)
		hashedpass = self._calcHash(saltedpass)
		return hashedpass == dbPass