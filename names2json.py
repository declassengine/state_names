'''
	Quick helper moduule that will export
	the names dict to a json file with a given names
'''

import json

def save(hash, filename="output.json"):

	try:
		wf = open(filename, "w")
	except IOError:
		print "Could not write to file " + filename
		return 0

	json_text = json.dumps(hash, sort_keys=True, indent=4, separators=(',', ': '))
	wf.write(json_text)
	wf.close()
	return 1
