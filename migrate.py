'''
	Run this program in order to migrate a cleaned output file (by default
	called [output_clean.json]) to an already-structured database. To see 
	the appropriate database model for this program, open the DB_REDAME.txt file
'''
import json
import MySQLdb as sql

def main():
	
	# Attempt to load the settings using the loadConfig() function below.
	# Exit the program if this doesn't work and print an error message.
	settings = loadConfig()
	if settings is 0:
		print 'There is an error or missing configuration file. Please make sure you have [db_config.json] properly configured.'
		return 1 

	# Try to open a db connection. Defaults to localhost.
	try:
		db = sql.connect(passwd=settings['password'], user=settings['user'], 
			db=settings['db_name'], host=settings['db_host'], charset='utf8', use_unicode=True)
	except IOError:
		print 'Unable to connect to database!'
		return 1

	# Database configuration
	db.autocommit = True

	# Next, try to open the correct output file
	try:
		fp = open('output_clean.json')
	except IOError:
		print 'There was an error opening the JSON file!'
		return 1

	# Attempt to isolate the <people> from the JSON file
	data = fp.read()
	people = json.loads(data)['people']

	# Loop through each <person> in <people> and add the relevant parts to the db		
	cursor = db.cursor()
	records_added = 0
	total_records = len(people)
	percent = .10

	for person in people:
		try:
			records_added += addPerson(person, cursor)
		except IOError:
			print 'There was an error adding ' + person['name']
			pass

		# Update console every time 10% of the total records have been added
		if records_added >= total_records * percent:
			print str(records_added) + ' records added out of ' + str(total_records)
			percent += .10

	cursor.close()
	db.commit()
	db.close()

	print '=========='
	print ' Added ' + str(records_added) + ' entries.'
	print '=========='

'''
	Takes a person dict and adds that person to the database pointed
	to by the cursor (<curs>) obejct.
'''
def addPerson(person, curs):

	# Insert the person's name into the 'people' table.
	last_name = person['last_name']
	first_name = person['first_name']
	try:
		curs.execute("""INSERT INTO consular_people (first_name, last_name) VALUES (%s, %s)""", (first_name, last_name))
	except sql.Error, e:
		print '--= ERROR for [' + last_name + ', ' + first_name + '] =--'
		print e
		pass

	# Isolate the added person_id, then add each position to the 'positions' table.
	# person_id is the foreign key in the 'positions' table
	next_id = curs.lastrowid
	for position in person['positions']:
		# The first check is to see if there is location data
		if 'location' in position:
			if 'year_from' in position and 'year_to' in position:
				try:
					curs.execute("""INSERT INTO consular_positions (location, title, date_from, date_to, person_id) VALUES(%s, %s, %s, %s, %s)""", (position['location'], 
						position['title'], formatYear(position['year_from']), formatYear(position['year_to']), next_id))
				except sql.Error, e:
					print '--= ERROR =--'
					print e
					pass	
			elif 'year_single' in position:
				try:
					curs.execute("""INSERT INTO consular_positions (location, title, date_single, person_id) VALUES(%s, %s, %s, %s)""", (position['location'], 
						position['title'], formatYear(position['year_single']), next_id))
				except sql.Error, e:
					print '--= ERROR =--'
					print e
					pass	
		else:
			if 'year_from' in position and 'year_to' in position:
				try:
					curs.execute("""INSERT INTO consular_positions (title, date_from, date_to, person_id) VALUES(%s, %s, %s, %s)""", (position['title'], 
						formatYear(position['year_from']), formatYear(position['year_to']), next_id))
				except sql.Error, e:
					print '--= ERROR =--'
					print e
					pass	
			elif 'year_single' in position:
				try:
					curs.execute("""INSERT INTO consular_positions (title, date_single, person_id) VALUES(%s, %s, %s)""", (position['title'], 
						formatYear(position['year_single']), next_id))
				except sql.Error, e:
					print '--= ERROR =--'
					print e
					pass	

	return 1

'''
	Takes a YYYY year as a string and returns a format compatible with sql
'''
def formatYear(year):
	return year + '-01-01'

'''
	Loads a json configuration file with all of the database
	settings information and the proper table names. Returns a dict
	of these settings if checks are successful. Otherwise returns 0.
'''
def loadConfig():
	has_errors = False;
	
	# Try to open the settings file.
	try:
		fp = open('db_config.json')
	except IOError:
		print 'Could not open the configuration file.'
		return 0

	# Load the file data into a dict
	data = fp.read()
	fp.close()
	settings = json.loads(data)

	# Make sure the required values are present
	if not configErrorCheck(settings, 'db_name'):
		errorStatement('db_name')
		has_errors = True
	if not configErrorCheck(settings, 'user'):
		errorStatement('user')
		has_errors = True
	if not configErrorCheck(settings, 'password'):
		errorStatement('password')
		has_errors = True

	# Setup default values
	if not configErrorCheck(settings, 'db_port'):
		settings['db_port'] = 3306
	if not configErrorCheck(settings, 'db_host'):
		settings['db_host'] = 'localhost'

	# If there are errors, return 0. Else, return the settings dict.
	if has_errors:
		return 0
	else:
		return settings


'''
	Helper for error checking the config
'''
def configErrorCheck(settings, key):
	if key not in settings:
		return False
	elif settings[key] is not "":
		return True	
	else:
		return False

'''
	Returns a string with the error statement
	when a required item is not configured properly
'''
def errorStatement(item):
	return "You do not have a %s configured. This is required. Please edit the [db_config.json] file." % (item)			

if __name__ == '__main__':
	main()