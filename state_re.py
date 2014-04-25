import re
import json

'''
	Compile individual tests for the potential different parts
	of the text
'''


# These are the basic RegEx compilations for relevant data
full_position_parser = re.compile(r"([^0-9,(]*)")
name_parser = re.compile(r"(?P<last_name>[^,]*),\s(?P<first_name>[^0-9,]*)")

# Testng new patterns from scratch
location_parser = re.compile(r'((?:^|,|\s)+?(?P<open_location>\w+)(?:$|\n|\s|\t)(?:\(|\)|$|\d))|(\((?P<enclosed_location>\w+)\))')
year_parser = re.compile(r'\([^()]*?(?P<year_from>\d{4})[^()-]*?-[^()-]*?(?P<year_to>\d{4})[^()]*?\)|\([^()]*?(?P<complex_year>\d{4})[^()]*?\)|\((?P<simple_year>\d{4})\)')

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
		clean_pos['raw_position'] = position # For error checking
		text = position[:] # Copy the original so we can cut it down

		# Check to see if the string can be split by comma
		# If so, update 'text' variable to hold only the rest
		split_str = text.split(',')
		if(split_str[0] != text):
			clean_pos['title'] = split_str[0]
			text = split_str[1]
		else:
			full_title = full_position_parser.match(text) # We use 'match' her because it's always at the start of the string
			if(full_title):
				clean_pos['title'] = full_title.groups()[0]

		# Check for the year, and if it's there remove it and
		# update the 'text' variable
		year = year_parser.search(text)
		if(year):
			if(year.group('year_from') and year.group('year_to')):
				year_range = year.group('year_from') + '-' + year.group('year_to')
				clean_pos['year_range'] = year_range
				text = re.sub(year_range, '', text)
			elif(year.group('simple_year')):
				clean_pos['year'] = year.group('simple_year')
				text = re.sub(year.group('simple_year'), '', text)
			elif(year.group('complex_year')):
				clean_pos['year'] = year.group('complex_year')
				text = re.sub(year.group('complex_year'), '', text)	
			else:
				clean_pos['year_text'] = text
		else:
			clean_pos['year_text'] = text	

		# Check for the location, and if it's there isolate it in
		# whatever format it currently is in
		location = location_parser.search(text)
		if(location):
			if(location.group('enclosed_location')):
				clean_pos['location'] = location.group('enclosed_location')
			elif(location.group('open_location')):
				clean_pos['location'] = location.group('open_location')
			else:
				clean_pos['loc_text'] = text
		else:
			clean_pos['loc_text'] = text	

		# Add only if there was ANY information for that position:
		if(len(clean_pos) > 0):
			cleaned_positions.append(clean_pos)
		else:
			print 'No positions were cleaned for a person.'	

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
