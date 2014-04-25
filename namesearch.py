'''
	A command-line program for searching a clean State Dept Consular names JSON file
'''
import json

def main():
	last = raw_input('LAST name (or part of last name): ')
	first = raw_input('FIRST name (or part of first name):')
	results = []

	try:
		fp = open('output_clean.json')
	except IOError:
		print 'There was an error opening the JSON data file. Please make sure that the file [output_clean.json] has been properly generated!'

	data = fp.read()
	fp.close()
	all_names = json.loads(data)
	del data

	print 'Searching ' + str(all_names['count']) + ' listed entries...'

	people = all_names['people']
	for person in people:
		if last in person['last_name']:
			if first in person['first_name']:
				results.append(person)

	if len(results) > 0:
		print 'Found ' + str(len(results)) + ' matches:'
		for result in results:
			print '=========='
			prettyDisplay(result)
			print '=========='
	else:
		print '================='
		print 'Found No results.'
		print '================='	

def prettyDisplay(person):
	print 'NAME: ' + person['first_name'] + ' ' + person['last_name']
	print 'POSITIONS: '
	count = 0
	for position in person['positions']:
		count += 1
		print str(count)
		for key in position:
			print '-------> ' + key + ': ' + position[key]

if __name__ == '__main__':
	main()