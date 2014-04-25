import json
import state_re

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