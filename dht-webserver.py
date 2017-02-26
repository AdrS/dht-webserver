from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet import reactor
from hashlib import sha256
from urllib import unquote
from util import *
import sys, os

class GetFile(Resource):
	isLeaf = True
	def __init__(self, path):
		Resource.__init__(self)
		self.path = path

	def render_GET(self, request):
		print request.path
		#TODO: see if we have file locally
		#if on another server, redirect
		if not validPath(self.path):
			request.setResponseCode(404)
			return "404 file not found"

		self.id = sha256(self.path).hexdigest()

		request.setHeader(b"content-type", b"text/plain")
		return "get file:" + self.id + "\nTODO: finish me!!!"

class DownloadFile(Resource):
	def getChild(self, name, request):
		return GetFile(request.path[len("/download/"):])

class PostFile(Resource):
	def render_POST(self, request):
		print "POST"
		print request.content.read()
		#TODO: parse and validate upload
		request.write("TODO: finish me!!!")
		request.finish()
		return NOT_DONE_YET

class UploadFile(Resource):
	def render_GET(self, request):
		request.setHeader(b"content-type", b"text/html")
		return '''
		<!doctype html>
		<html>
		<body>
			<form action="/post" method="post" enctype="multipart/form-data">
			<input type="file" name="ufile">
			<input type="submit" value="submit">
			</form>
		</body>
		</html>
		'''
		

if __name__ == '__main__':
	port = 8080
	base = os.getcwd()

	if len(sys.argv) == 2:
		#if single parameter is an integer, then it must be port
		if sys.argv[1].isdigit():
			port = int(sys.argv[1])
		else:
			base = sys.argv[1]
	elif len(sys.argv) == 3:
		if sys.argv[1].isdigit():
			port = int(sys.argv[1])
			base = sys.argv[2]
		else:
			port = int(sys.argv[2])
			base = sys.argv[1]
	elif len(sys.argv) > 3:
		print "usage: %s [<base dir>] [<port>]" % sys.argv[0]
		sys.exit(1)

	root = Resource()
	root.putChild("download", DownloadFile())
	root.putChild("post", PostFile())
	root.putChild("upload", UploadFile())

	reactor.listenTCP(port, Site(root))
	print "Base directory: ", base
	print "starting server on port %s..." % port
	reactor.run()
