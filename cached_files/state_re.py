import re
import json

'''
	Compile individual tests for the potential different parts
	of the text
'''


# These are the basic RegEx compilations for relevant data
full_position_parser = re.compile(r"([^0-9,(]*)")
single_location_parser = re.compile(r"^.*?\(([^0-9)]*)\).*$")
isolate_location_parser = re.compile(r"[^,()]*,([^0-9,()]*)")

# The complex_location addresses problematic complex strings that came about from testing. It complicates population control flow as well, dammit
complex_location_parser = re.compile(r"^[^()](\((?P<location>[^0-9])\)\s((\([^0-9]*(?P<year_from>\d{4})-[^0-9]*(?P<year_to>\d{4})\)))|(\([^0-9()]*(?P<year_single>\d{4})\)))")
year_single_parser = re.compile(r"^.*?\([^0-9()]*(\d{4})\).*$")
year_range_parser = re.compile(r"^.*?\([^0-9]*(?P<year_from>\d{4})-[^0-9]*(?P<year_to>\d{4})\).*$") # Added exclusions because some dates are "(jan 1954 - feb 1966)"
name_parser = re.compile(r"(?P<last_name>[^,]*),\s(?P<first_name>[^0-9,]*)")

'''
	Takes the whole raw data dict and returns a cleaned version. Writes to a file suffixed
	with '_clean.json'

	regex example: r'\(\w{,4}\d{4}-\w{,4}\d{4}\)(?:$|\s|\w)|\(\d{4}\)(?:$|\s|\w)'
'''
def cleanConsularData(data):
	clean_data = {}
	clean_data['count'] = 0
	clean_data['people'] = []
	clean_data['errors'] = []

	# For each person in the original array, increase count and add a clean person
	for person in data['raw_people']:
		
		# Add a cleaned person to the clean dataset. If it doesn't work,
		# add to the error array on the new set.
		clean_person = cleanPerson(person)
		if(clean_person['first_name'] and clean_person['last_name']):
			clean_data['people'].append(clean_person)
			clean_data['count'] += 1
		else:
			clean_data['errors'].append(person)
	print 'Successfully added ' + str(clean_data['count']) + ' entries.'
	if(clean_data['count'] != data['count']):
		print 'There were ' + str(data['count'] - clean_data['count']) + ' discrepancies!!'
	writeCleanData(clean_data)
	print '==========\n\n'



'''
	Gets clean field information for a given person object 
	and returns a cleaned person object.
'''
def cleanPerson(person):
	clean_person = {}
	
	# First, clean the names then add them
	clean_names = cleanName(person['name'])
	if(len(clean_names) > 0):
		clean_person['first_name'] = clean_names['first_name']
		clean_person['last_name'] = clean_names['last_name']

	# Now add the positions array, even if it's empty
	clean_person['positions'] = cleanPositions(person['positions'])

	# Return the cleaned person
	return clean_person	


'''
	Takes a person['name'] from the people array
	and returns an object with first_name and last_name
'''	
def cleanName(name):
	match = name_parser.match(name)
	name_data = {}

	if not match:
		print 'ERROR: Name parser error for ' + name
		return name_data
	else:
		name_data['first_name'] = match.group('first_name')
		name_data['last_name'] = match.group('last_name')
		return name_data

'''
	Clean the position fields for a given entry in the
	people array. Isolate Location takes precedent over Single Location.
	Year ranges and single years will BOTH be entries in the resulting set
'''
def cleanPositions(positions_list):
	cleaned_positions = []

	for position in positions_list:
		clean_pos = {}

		# Check for RE matches for the attributes
		full_position = full_position_parser.match(position)
		single_location = single_location_parser.match(position)
		isolate_location = isolate_location_parser.match(position)
		complex_location = complex_location_parser.match(position)
		year_single = year_single_parser.match(position)
		year_range = year_range_parser.match(position)

		# Control flow and assignment based on results

		# Position name (called 'title')
		if(full_position):
			clean_pos['title'] = full_position.groups()[0]

		# Optional (you can erase): add original position string
		clean_pos['raw_position'] = position	

		# Location information
		if(isolate_location):
			clean_pos['location'] = isolate_location.groups()[0]
		elif(single_location):
			clean_pos['location'] = single_location.groups()[0]
		elif(complex_location):
			if(complex_location.group('location')):
				clean_pos['location'] = complex_location.group('location')

		# Date information
		if(year_single):
			clean_pos['year'] = year_single.groups()[0]
		elif(year_range):
			year_from = year_range.group('year_from')
			year_to = year_range.group('year_to')
			clean_pos['year_range'] = year_from + '-' + year_to
		elif(complex_location):
			if(complex_location.group('year_from') and complex_location.group('year_to')):
				clean_pos['year_range'] = complex_location.group('year_from') + '-' + complex_location.group('year_to')
			if(complex_location.group('year_single')):
				clean_pos['year'] = complex_location.group('year_single')		

		# Add only if there was ANY information for that position:
		if(len(clean_pos) > 0):
			cleaned_positions.append(clean_pos)

	return cleaned_positions

'''
	Converts clean data dict to JSON and then writes to the output file
'''
def writeCleanData(clean_data):
	data_json = json.dumps(clean_data, sort_keys=True, indent=4, separators=(',', ': '))

	try:
		wf = open('output_clean.json', 'w')
	except IOError:
		print 'There was an error writing the output file!'
		return 0
	wf.write(data_json)
	wf.close()
	print 'Successfully wrote [output_clean.json]!'
