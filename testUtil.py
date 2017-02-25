from util import *
def test_validPath():
	assert(not validPath('asf\x01'))
	assert(not validPath('a'*300))
	assert(not validPath('~/yo'))
	assert(not validPath('/yoasf jskalfjsdk '))
	assert(not validPath('yoasf //jskalfjsdk '))
	assert(not validPath('yoasf jskalfjsdk/'))
	assert(not validPath('yoasf jskalfj\tsdk'))
	assert(validPath('asf'))
	assert(validPath('asf.txt'))
	assert(validPath('asdf sad f 6579878()- + /asf.txt'))

def test_validHash():
	assert(validHash('a'*64))
	#only lowercase allowed
	assert(not validHash('A'*64))
	assert(not validHash('548237ae'))
	assert(not validHash('5'*65))
	assert(validHash('2005469a2150d5742483be25e97065346847a58bd0b0f24a4523e10cae85782c'))

def test_require():
	try:
		require(False, "test message")
		assert(False)
	except Exception as e:
		assert(e.message == "test message")
	require(True, "asf")

if __name__ == '__main__':
	test_validPath()
	test_validHash()
	test_require()
