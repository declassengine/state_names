''' Quick and dirty program for pulling Diplomat name and position
	information from the State Dept website. Makes use of the BeautifulSoup
	HTML parser module and the 'state_re.py' module included in this
	directory. Output is a file called 'output.json', containing
	specific but unparsed text from the scrape.
'''


from BeautifulSoup import BeautifulSoup as bs
import urllib2
import names2json

def main():

	# Set up a dict to store the results and a count
	names_dict = {}
	names_dict['count'] = 0
	names_dict['raw_people'] = []
	prefix = 'http://history.state.gov' ## This is just a prefix for use by urllib (absolute path)

	# Get the first page, then loop through each subsequent page
	current_url = '/departmenthistory/people/by-name/a'

	while(current_url):
		next_page = getPage(prefix + current_url, names_dict)

		if(next_page):
			current_url = next_page.a.get("href") # If there is a link to a subsequent page, follow it
		else:
			current_url = None	

	print "+++++++++++++++++++++++++++++++++++++++"
	print "=======================================\n"
	print " Dictionary Compiled " + str(names_dict['count']) + " Names Successfully\n"
	print "++++++++++++++++++++++++++++++++++++++++"
	print "========================================\n\n"

	names2json.save(names_dict) # try to write the result to json

'''
	Adds the name information for a given page. A "page" is all of the last
	names for a letter in the alphabet, so A-Z. In other words, this function should
	run 26 times. Its caller function should know how to cycle based on the soup 
	object it does or does not return.

	At the end, this function looks for a "next letter" link in the html and returns
	that object. If the object is empty, then the caller function knows to terminate
	its while loop.
'''
def getPage(url, names_dict):

	# Get the page content for the provided url
	wb = urllib2.urlopen(url)
	html = wb.read()
	wb.close()

	# Soupify the scraped html
	soup = bs(html)

	# Find the div with class "content"
	main_content = soup.find("div", "content")

	# Get the first <ul> in that div, which corresponds to the list of name info
	name_list = main_content.find("ul")

	# Grab the first <li> and store it. Sibling functions will iterate from here on out
	current_name = name_list.find("li")
	
	# Iterate over the names and add them to the dict
	while(current_name):
		names_dict['count'] += 1
		addName(current_name, names_dict)
		current_name = current_name.findNextSibling("li")

	print "Successfully added " + str(names_dict['count']) + " names from " + url

	# Return the next link, if there is one
	next_nav = soup.find("div", { "id": "contentnav"} ).ul.find("li", "right")
	return next_nav

''' Adds a name to the names dict for storage in the proper structure '''
def addName(souped_name, names_dict):
	individual = {}
	
	# A list for the different positions
	individual['positions'] = []

	# The link to the bio on the site
	individual['bio_link'] = souped_name.a.get("href")

	# The actual name
	individual['name'] = souped_name.a.text

	# The dates
	individual['dates'] = souped_name.text

	# Process the positions
	getIndividualPositions(souped_name, individual)

	# Add individual to names_dict with count as key
	names_dict['raw_people'].append(individual)

	# Report !!
	print "Successfully added " + individual['name'] + ' to the dict.'


'''
	Processes the nested <ul> that contains the different positions one had
	until there is nothing left. Returns all positions as a list attached to
	the provided @individual parameter
'''
def getIndividualPositions(souped_name, individual):

	position_ul = souped_name.ul
	current_pos = position_ul.find("li")

	# Run a while loop as long as there are more positions
	while(current_pos):
		
		# Append the first position to the list,
		# then update the current position in that list
		individual['positions'].append(current_pos.text)
		current_pos = current_pos.findNextSibling("li")


if __name__ == '__main__':
	main()