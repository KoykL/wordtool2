import tornado.web
import json, re, itertools
import helper, requestDispatch, dicts
import review, user
import random
class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		username = self.get_secure_cookie("username")
		if username:
			return username.decode('utf-8')
		else:
			return None
class MainHandler(BaseHandler):
	def get(self):
		self.render('index.html')
class AuthorizationHandler(BaseHandler):
	def post(self):
		username = self.get_argument('username')
		password = self.get_argument('password')
		u = user.User(self.application.db.getUnderlyingDb())
		if u.comparePass(username, password):
			self.set_secure_cookie("username", username)
			redirectUrl='/'
			try:
				redirectUrl = self.get_argument('next')
			except tornado.web.MissingArgumentError:
				pass
			self.redirect(redirectUrl)
		else:
			self.redirect('/login')
class LogoutHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.clear_cookie("username")
		redirectUrl='/'
		try:
			redirectUrl = self.get_argument('next')
		except tornado.web.MissingArgumentError:
			pass
		self.redirect(redirectUrl)
class LoginFormHandler(BaseHandler):
	def get(self):
		redirectUrl='/notebook'
		try:
			redirectUrl = self.get_argument('next')
		except tornado.web.MissingArgumentError:
			pass
		if self.current_user:
			self.redirect(redirectUrl)
		self.render("loginform.html", redirectUrl=redirectUrl)
class SignUpFormHandler(BaseHandler):
	def get(self):
		return self.render('singupform.html')
class UserHandler(BaseHandler):		
	def post(self):
		u = user.User(self.application.db.getUnderlyingDb())
		username = self.get_argument('username')
		password = self.get_argument('password')
		u.newUser(username, password)
		self.redirect('/')
class NotebookHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.redirect('/notebook/collections', permanent=True)
class BaseDataHandler(BaseHandler):
	pass
class ManageCollectionsHandler(BaseDataHandler):
	@tornado.web.authenticated
	def get(self):
		collectionnames = self.application.db.getCollectionNames(self.current_user)
		self.render('managecollections.html', collectionsGrouped = helper.group(collectionnames, 4))
class CollectionsHandler(BaseDataHandler):
	@tornado.web.authenticated
	def get(self):
		l = self.application.db.getCollectionNamesAndPreview(self.current_user)
		self.render("collections.html", collections=helper.group(l, 3))
	@tornado.web.authenticated
	def post(self):
		collectionName = self.get_argument('collectionname')
		def newCollectionWorker():
			if self.application.db.collectionisExisted(self.current_user, collectionName):
				self.redirect('/notebook/collections/new_form')
			else:
				self.application.db.insertCollection(self.current_user, collectionName)
				self.redirect('/notebook/collections')
		def deleteCollectionWorker():
			self.application.db.removeCollection(self.current_user, collectionName)
			self.write(json.dumps({'status_code': 200}))
		disDict = {
			'newcollection': newCollectionWorker,
			'deletecollection': deleteCollectionWorker
		}
		disp = requestDispatch.Dispatcher(dispatchDict=disDict)
		method = self.get_argument('method')
		try:
			disp.dispatch(method)
		except requestDispatch.NoRouteError:
			raise tornado.web.HTTPError(400, "Method is missed or incorrect.")
class CollectionHandler(BaseDataHandler):
	@tornado.web.authenticated
	def get(self, collection):
		if not self.application.db.collectionisInited(self.current_user, collection):
			self.application.db.addList(self.current_user, collection)
		self.redirect("/notebook/collections/{collection}/list1".format(collection=collection))
	@tornado.web.authenticated
	def post(self, collection):
		def newListWorker():
			self.application.db.addList(self.current_user,collection)
			self.write(json.dumps({'status_code': 200}))
		def deleteListWorker():
			self.application.db.removeListByPos(self.current_user, collection, int(self.get_argument('listnum')))
			self.write(json.dumps({'status_code': 200}))
		disDict = {
			'newlist': newListWorker,
			'deletelist': deleteListWorker
		}
		disp = requestDispatch.Dispatcher(dispatchDict=disDict)
		method = self.get_argument('method')
		try:
			disp.dispatch(method)
		except requestDispatch.NoRouteError:
			raise tornado.web.HTTPError(400, "Method is missed or incorrect.")
class ListsHandler(BaseDataHandler):
	@tornado.web.authenticated
	def get(self, collection, listnum):
		self.xsrf_token
		try:
			l = self.application.db.getList(self.current_user, collection, int(listnum))
		except:
			raise tornado.web.HTTPError(404, "List not existed.")
		listslen = int(self.application.db.getListsLen(self.current_user, collection))
		self.render("lists.html", collection=collection, listnum=int(listnum), listslen=listslen, words=helper.group(l, 3))
	@tornado.web.authenticated
	def post(self, collection, listnum):
		word = self.get_argument('word')
		word = helper.trim(word)
		def newWordWorker():	
			if word == "":
				return
			self.application.db.addWord(self.current_user, collection,int(listnum), word)
			self.write(json.dumps({'status_code': 200, 'word': word}))
		def deleteWordWorker():
			self.application.db.deleteWord(self.current_user, collection,int(listnum), word)
			self.write(json.dumps({'status_code': 200}))
		disDict = {
			'newword': newWordWorker,
			'deleteword': deleteWordWorker
		}
		disp = requestDispatch.Dispatcher(dispatchDict=disDict)
		method = self.get_argument('method')
		try:
			disp.dispatch(method)
		except requestDispatch.NoRouteError:
			raise tornado.web.HTTPError(400, "Method is missed or incorrect.")		
class ListsManageHandler(BaseDataHandler):
	@tornado.web.authenticated
	def get(self, collection):
		listslen = int(self.application.db.getListsLen(self.current_user, collection))
		self.render('managelists.html', listsNumGrouped = helper.group(range(1, listslen + 1), 4), collection=collection)
class ReviewListHandler(BaseHandler):
	def initialize(self):
		db=self.application.db.getUnderlyingDb()
		self._rdb = review.Review(db, self.current_user)
	@tornado.web.authenticated
	def get (self):
		l = self._rdb.getWords()
		l = l if l else ""
		l = itertools.islice(l, 3000)
		l = " ".join(l)
		self.render("reviewlist.html", reviewlist = l)
	@tornado.web.authenticated
	def post(self):
		def addListWorker():
			CollectionName = self.get_argument('collectionname')
			listNum = self.get_argument('listnum')
			words = self.application.db.getList(self.current_user, CollectionName, int(listNum))
			try:
				self._rdb.addToReviewList(words, CollectionName, listNum)
			except review.listWordExistedError:
				raise tornado.web.HTTPError('400')
			else:
				self.write(json.dumps({'status_code': 200}))
		def removeListWorker():
			raise NotImplementedError()
		method = self.get_argument('method')
		disDict = {
			'addlist': addListWorker,
			'removelist': removeListWorker
		}
		disp = requestDispatch.Dispatcher(dispatchDict=disDict)
		method = self.get_argument('method')
		try:
			disp.dispatch(method)
		except requestDispatch.NoRouteError:
			raise tornado.web.HTTPError(400, "Method is missed or incorrect.")
class ReviewListManageHandler(BaseHandler):
	@tornado.web.authenticated
	def get (self):
		pass
class ReviewHandler(BaseHandler):
	def initialize(self):
		db=self.application.db.getUnderlyingDb()
		self._rdb = review.Review(db, self.current_user)
	@tornado.web.authenticated
	def get(self):
		word = self._rdb.getWordDoc()
		if word == None:
			self.redirect("/notebook/reviewlist")
		self.render('review.html', word=word['word'], collection=word['belongTo']['collection'], list='list' + word['belongTo']['list'])
	@tornado.web.authenticated
	def post(self):
		word = self.get_argument('word')
		collection = self.get_argument('collection')
		list = self.get_argument('list')
		state = self.get_argument('state')
		def reply(state):
			if state == 'end':
				self.write(helper.makeRpl(210, 'Jorney Ended.'))
			else:
				self.write(helper.makeRpl(200, 'Success.'))
		def rememberWorker():
			self._rdb.removeReviewListWordFromSingleList(word)
			self._rdb.reviewDone(collection, list, word)
			if self._rdb.getWord() == None:
				reply('end')
			else:
				reply('not end')
		def forgetWorker():
			self._rdb.downRviewListWordPriority(word)
			if self._rdb.isTotured(collection, list, word):
				if not self.application.db.collectionisExisted(self.current_user, 'tortured'):
					self.application.db.insertCollection(self.current_user, 'tortured')
				if not self.application.db.collectionisInited(self.current_user, 'tortured'):
					self.application.db.addList(self.current_user, 'tortured')
				listsLen = int(self.application.db.getListsLen())
				self.application.db.addWord(self.current_user, 'tortured', listsLen, word)
			if self._rdb.getWord() == None:
				reply('end')
			else:
				reply('not end')
		disDict = {
			'remember': rememberWorker,
			'forget': forgetWorker
		}
		disp = requestDispatch.Dispatcher(dispatchDict=disDict)
		try:
			disp.dispatch(state)
		except requestDispatch.NoRouteError:
			raise tornado.web.HTTPError(400, None ,"State is missed or incorrect.")
class DefHandler(BaseHandler):
	@tornado.web.authenticated
	def get (self, word):
		fromWhere = {}
		try:
			fromcollection = self.get_argument('fromcollection')
			fromlist = self.get_argument('fromlist')
		except tornado.web.MissingArgumentError:
			pass
		else:
			fromWhere['fromcollection'] = fromcollection
			fromWhere['fromlist'] = fromlist
		db=self.application.db.getUnderlyingDb()
		d = dicts.CachedYouDaoDict(word, db)
		defs = " ".join(d.getDef())
		sens = d.getEgSentence()
		sen = random.choice(sens)
		engSen = sen[0]
		chnSen = sen[1]
		self.render('def.html', definition=defs, word=word, engSentence = engSen, chnSentence = chnSen, fromWhere=fromWhere)
class NewCollectionHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.render("newcollection.html")
class NewListHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self, collection):
		self.render("newlist.html", collection=collection)