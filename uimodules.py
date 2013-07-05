import tornado.web
class navbar(tornado.web.UIModule):
	def render(self):
		return self.render_string("navbar.html")