from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet import reactor
from hashlib import sha256
from urllib import unquote
from util import *
import sys, os, FileStore, shutil

class GetFile(Resource):
	isLeaf = True
	def __init__(self, path):
		Resource.__init__(self)
		self.path = path
	
	def notFound(self, request):
		request.setHeader(b"content-type", b"text/plain")
		request.setResponseCode(404)
		return "404 file not found"
	
	def render_GET(self, request):
		print request.path
		if not validPath(self.path):
			return self.notFound(request)

		fid = sha256(self.path).hexdigest()

		#if on another server, redirect
		if not fileStore.isLocal(fid):
			request.setResponseCode(301)
			dest = 'http://' + fileStore.getHost(fid) + request.path
			print dest
			request.setHeader("location", dest)
			return 'Look for file at: %s' % dest
		#if file exists locally, send it
		elif fileStore.existsInIndex(fid) and fileStore.existsOnDisk(fid):
			#TODO: add support for range requests
			with open(fileStore.idToLocalPath(fid), 'rb') as f:
				shutil.copyfileobj(f, request)
			request.finish()
			return NOT_DONE_YET
		else:
			return self.notFound(request)

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
	
	print "Reading files from: ", base
	try:
		fileStore = FileStore.FileStore(base)
	except Exception as e:
		sys.stderr.write('error reading file store: %s\n' % e.message)
		sys.exit(1)

	root = Resource()
	root.putChild("download", DownloadFile())
	root.putChild("post", PostFile())
	root.putChild("upload", UploadFile())

	reactor.listenTCP(port, Site(root))
	print "starting server on port %s..." % port
	reactor.run()
