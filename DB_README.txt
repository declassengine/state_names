*************************************
*                                   *
*      Instructions for Migration   *
*                                   *
*************************************

Before the migration can be executed, there are som key prerequisites:

1) Two database tables must be set up ahead of time. They should be structured like this:

	a) 'consular_people' (tablename)
		--> 'person_id' INT, PRIMARY_KEY, AUTO_INCREMENT, NOT NULL
		--> 'first_name' VARCHAR(255), NOT NULL
		--> 'last_name' VARCHAR(255), NOT NULL
	b) 'consular_positions'
		--> 'position_id' INT, PRIMARY_KEY, AUTO_INCREMENT, NOT NULL
		--> 'title' TEXT
		--> 'location' VARCHAR(255)
		--> 'date_from' DATE // If there is a date range instead of a single year
		--> 'date_to' DATE // If there is a date range instead of a single year
		--> 'date_single' DATE // For single year positions
		--> 'person_ID' FOREIGN_KEY from consular_people person_id

	**NOTE** The character set for the fields on these tables MUST be utf8	

2) You must have a copy of the *clean* scraper output. The file should be named
'output_clean.json'. If there is not an up to date version of this, you must
open the python interpreter, import 'tests', and then run 'tests.getCleanData()'
	
	**NOTE** the getCleanData() function itself requires the raw scrape data, which
	is contained in a file called 'output.json'. If this also not present, you must
	run 'python state_names.py' from the command line BEFORE executing the interpreter
	instructions mentioned above.

3) Be sure that the 'db_config.json' file is filled out correctly. You'll need a database name,
 a username, and a password at minimum. Defaults to the standard MySQL port and the hostname defaults
 to localhost

4) Run migration.py from the command line, and you should be all set!