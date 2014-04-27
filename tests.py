'''
	This file contains tests for manually evaluating some of the data
	parsed by state_re.py.

	Please excuse any ugliness / sloppiness
'''

import json
import state_re
import random

# Generic function for re-processing the clean files
def getCleanData():
	try:
		fp = open('output.json')
	except IOError:
		print 'Error opening initial output file!'
		return 0
	raw_data = fp.read()
	fp.close()
	raw_hash = json.loads(raw_data)
	del raw_data
	state_re.cleanConsularData(raw_hash)
	del raw_hash

	try:
		cfp = open('output_clean.json')
	except IOError:
		print 'Error opening clean output file!'
		return 0
	data = cfp.read()
	cfp.close()
	c_hash = json.loads(data)
	del data

	return c_hash

# Get num random numbers within the collection of people and return verbose person data
def randomPeople(people, num=15):
	random_people = []

	# Populate a list with num random numbers
	for x in range(0, num):
		random_people.append(random.randint(0, len(people)))

	# Iterate through the random index values on the original people list, printing info along the way
	for random_person in random_people:
		person = people[random_person]
		print '\n======\n' + person['last_name'] + ', ' + person['first_name']

		for position in person['positions']:
			print '\t TITLE: ' + position['title']

			if 'year' in position:
				print '\t\t YEAR: ' + position['year']
			if 'year_range' in position:
				print '\t\t YEARS: ' + position['year_range']
			if 'location' in position:
				print '\t\t LOCATION: '	+ position['location']


# Perform all of the checks and be verbose about it.
def allChecks(people):
	result = {}

	# Dates
	date_result = checkDates(people)
	if(date_result['errors'] > 0):
		print 'There were ' + str(date_result['errors']) + ' DATE errors.'
		print "See result['date_errors'] for more info."

	# Names
	name_result = checkNames(people)
	if(name_result['errors'] > 0):
		print "There were " + str(name_result['errors']) + ' NAME errors.'
		print "See result['name_errors'] for more info."

	# Locations
	loc_result = checkLocations(people)
	if(loc_result['errors'] > 0):
		print 'There were ' + str(loc_result['errors']) + ' LOCATION errors.'
		print "See result['loc_errors'] for more info."

	result['date_errors'] = date_result
	result['name_errors'] = name_result
	result['loc_errors'] = loc_result
	return result 

# Check to see which don't have date info. Return an object with references
def checkDates(people):
	result = {}
	result['errors'] = 0
	result['data'] = []
	result['interpreted_text'] = []

	for person in people:
		for position in person['positions']:
			if 'year' not in position and 'year_range' not in position:
				result['errors'] += 1
				result['data'].append(position['raw_position'])
			if 'year_text' in position:
				result['interpreted_text'].append(position['year_text'])

	return result

# Check for name data
def checkNames(people):
	result = {}
	result['errors'] = 0
	result['data'] = []

	for person in people:
		if 'first_name' not in person and 'last_name' not in person:
			result['errors'] += 1
			result['data'].append(person)

	return result

# Check locations
def checkLocations(people):
	result = {}
	result['errors'] = 0
	result['data'] = []
	result['interpreted_text'] = []

	for person in people:
		for position in person['positions']:
			if 'location' not in position:
				result['errors'] += 1
				result['data'].append(position['raw_position'])
			if 'loc_text' in position:
				result['interpreted_text'].append(position['loc_text'])	

	return result			