def validPath(path):
	#TODO: test me!!! (doen't matter because I will be hashing filenames)
	validPathChars = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&\'()+,-./;=@[]^_`{}~ \t')
	if (not path) or path.startswith('/') or path.startswith('~/') or '..' in path or '//' in path or (not set(path).issubset(validPathChars)) or len(path) > 255:
		return False
	return True

def validHash(h):
	'''checks if h is a lowercase sha256 hexdigest'''
	if len(h) != 64: return False
	for c in h:
		if c not in '0123456789abcdef':
			return False
	return True

def require(cond, msg):
	if not cond:
		raise Exception(msg)
