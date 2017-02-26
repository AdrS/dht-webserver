from hashlib import sha256
import os
from util import *

'''
FileStore(base) - reads in index (list of files on server)
	and list of other  servers
-----------------------------------------------------------
base - specifies directory where index and files are stored
	local path is specified by id (think git)
-----------------------------------------------------------
base/
	00/
		3f/
			6d768e6c7...
			...
		...
	01/
		...
	fe/
		...
	ff/
		...
	index.txt
	servers.txt
-----------------------------------------------------------
index.txt - stores list of paths stored
-----------------------------------------------------------
path1
path2
 ...
-----------------------------------------------------------
servers.txt - stores 
	idx is index corresponding to entry for this server
	ith row says server with ith ip is responsible for
	files with ids in range ((i - 1)th id, ith id]
-----------------------------------------------------------
idx
<id>  <xxx.xxx.xxx.xxx:port>
...
-----------------------------------------------------------
'''

class FileStore:
	def __init__(self, base=os.getcwd()):
		if base.endswith(os.sep):
			base = base[:-len(os.sep)]
		self.base = base
		#TODO: compress index???
		self.idx_file = open(base + os.sep + 'index.txt')
		self.index_dirty = False

		#parse index
		self.paths = {}
		for path in self.idx_file:
			path = path.rstrip()
			require(validPath(path), 'invalid path')
			fid = self.getId(path)
			require(not self.paths.has_key(fid), 'repeated key')
			self.paths[fid] = path
			#TODO: check that all files actually are on disk???

		#TODO: move server part elsewhere??
		servers_file = open(base + os.sep + 'servers.txt')
		#parse server list
		#first line gives index of current server in list
		self.sid = int(servers_file.readline())
		self.servers = []
		for l in servers_file:
			require(len(l) > 64 + 4, 'invalid server entry')
			sid = l[:64]
			require(validHash(sid), 'invalid id')
			if self.servers:
				require(sid > self.servers[-1][0], 'ids must be in strictly increasing order')
			host = l[65:].strip()
			#TODO: validate host
			self.servers.append((sid, host))
		require(self.servers, 'no servers given')
		require(self.servers[-1][0] == 'f'*64, 'server list does not include range for all possible ids')
		require(0 <= self.sid and self.sid < len(self.servers), 'invalid index into servers list')

	def getServerIndex(self, fid):
		#use binary search
		l = 0
		h = len(self.servers)
		while l < h:
			m = (l + h)/2
			if self.servers[m][0] < fid:
				l = m + 1
			else:
				h = m
		return h

	def isLocal(self, fid):
		return self.getServerIndex(fid) == self.sid

	def getHost(self, fid):
		return self.servers[self.getServerIndex(fid)][1]

	def idToLocalPath(self, fid):
		return self.base + os.sep + fid[:2] + os.sep + fid[2:4] + os.sep + fid[4:]

	def getPath(self, fid):
		return self.paths.get(fid, '')

	def getId(self, path):
		return sha256(path).hexdigest()

	def existsInIndex(self, fid):
		return self.paths.has_key(fid)

	def existsOnDisk(self, fid):
		return os.path.exists(self.idToLocalPath(fid))

	def addFile(self, path, fio, overwrite = False):
		fid = self.getId(path)
		if not overwrite and (self.existsInIndex(fid) or self.existsOnDisk(fid)):
			raise Exception('file already exists')

		try:
			#ensure directories exist
			d = self.base + os.sep + fid[:2] + os.sep + fid[2:4]
			if not os.path.exists(d):
				os.makedirs(d)
			fout = open(self.idToLocalPath(fid), 'wb')
			while True:
				data = fio.read(4096)
				if not data: break
				fout.write(data)
			fout.close()
		except Exception as e:
			raise e
		self.paths[fid] = path
		self.index_dirty = True

	def removeFile(self, fid):
		if not self.existsInIndex(fid): return
		if self.existsOnDisk(fid):
			#TODO: remove empty directories???
			os.remove(self.idToLocalPath(fid))
		del self.paths[fid]
		self.index_dirty = True
	#TODO: add renaming of files???

	def saveIndex(self):
		if self.index_dirty:
			f = open(self.base + os.sep + 'index.txt.tmp', 'w')
			for p in self.paths.values():
				f.write(p)
				f.write('\n')
			f.close()
			os.rename(self.base + os.sep + 'index.txt.tmp', self.base + os.sep + 'index.txt')
		self.index_dirty = False
