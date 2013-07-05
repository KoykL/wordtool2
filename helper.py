import re
import json
def group(iterator, num):
	tmp = []
	for count, each in enumerate(iterator, start = 1):
		tmp.append(each)
		if count % num == 0:
			yield tmp
			tmp = []
	if tmp != None:
		yield tmp
def trim(str):
	str = re.sub(r'^\s\s*','', str)
	str = re.sub(r'\s\s*$','', str)
	return str
def makeRpl(status_code, message, data=None):
	return json.dumps({'status_code': status_code, 'message': message, 'data': data})