# About project

This small program helps to extract job postings from LinkedIn by keyword and filter them using AI.

# Preparing:

1. Get an API key from OpenAI and top up the balance with the minimum amount ($5).

	Set the environment variable with key as described here (Step 2: Set up your API key):
	https://platform.openai.com/docs/quickstart
	
	And check that everything works by running OpenAiTest.py.
	
2. Set your LinkedIn username and password in LinkedIn_ConcurrentScraper.py

	api = Linkedin('mail', 'pass')
	
Install the necessary dependencies:

pip install git+https://github.com/tomquirk/linkedin-api.git
pip install --upgrade openai

If you use LinkedIn Premium, you have significantly higher limits on scraping and speeds, but having Premium is not mandatory. However, you need to reduce the speed by adjusting the number of threads and the size of the scrape to avoid looking like suspicious activity:

	for _ in range(2):
	
	If there are problems, then reduce the scraper limit:
	
	limit = 100
	
# Patch the LinkedIn API Library to Add Search by Location Ability (geoId):

1. Open the LinkedIn_ConcurrentScraper and locate the line with the text 'result = api.search_jobs()'
2. Press and hold the 'CTRL' key and click on 'search_jobs'. Navigate with file manager to the library 'linkedin.py' and replace the file with the updated file from this project.	
	
Run LinkedIn_ConcurrentScraper, and if you receive the CHALLENGE error on startup, you need to log out, clear the site's cookies, restart the computer (!), and log in to LinkedIn again. Check the Troubleshooting section here https://github.com/tomquirk/linkedin-api

After execution, you will get a 'job_listings.json' file with the results.

3. Run OpenAI_JobScreener, after execution you will get a 'results.txt' file with the results. If it is empty, the AI could not select any jobs based on your request. Modify the context requests if necessary.

# Tuning:

To find jobs, you need to configure your location, search key, and the number of vacancies (limit) you want to retrieve (maximum 1000 (-1)), as well as set GPT commands.

1. Find the location: Open the LinkedIn search page and perform a search, e.g., `React` `Poland`.
2. Set the location you found: Extract the `geoId` number from the URL and set it in `LinkedIn_ConcurrentScraper.py` in the `location_geo_id` field.
3. Set your search key, e.g., `React`, in `LinkedIn_ConcurrentScraper.py` in the `keywords` field.
4. Set your vacancies limit for searching, e.g., 5 (maximum 1000 (-1)).
5. Configure GPT commands in the file `OpenAI_JobScreener.py`:

   5.1. System Role command context: Define the context that the system should know before your request. For example: `"Your role is a vacancy analyzer. Respond with 'yes' if the job is fully suitable for a React Developer; otherwise, respond with 'no'."`

   5.2. Request context: This will be sent with each vacancy in the User Role Content. For example: `f"Is this vacancy suitable for a React Software Developer? Yes or no?\n\n{description}"`