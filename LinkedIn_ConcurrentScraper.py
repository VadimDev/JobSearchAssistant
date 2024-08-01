import json
import time
from linkedin_api import Linkedin
import threading

# LinkedIn Login
api = Linkedin('mail', 'pass')

# Job Search Options
keywords = "C++"  # Software Engineer
location_geo_id = "105072130"  # you can take it from the search page in linkedin, look to "geoId" in URL
limit = 100  # -1 max 1000

# Start time for job search (last 24 hours)
listed_at = 604800
# 604800 week
# 24 * 60 * 60 24 h

lock = threading.Lock()
job_numbers = []
job_counter = 0
all_jobs = []

def search_and_collect_jobs():
    global job_numbers, job_counter, all_jobs

    result = api.search_jobs(
        keywords=keywords,
        location_geo_id=location_geo_id,
        limit=limit,
        listed_at=listed_at
    )

    print(f"Received {len(result)} jobs in this request")

    with lock:
        for job in result:
            tracking_urn = job['trackingUrn']
            tracking_number = tracking_urn.split(':')[-1]
            job_numbers.append(tracking_number)


def get_job_details():
    global job_numbers, job_counter, all_jobs

    while True:
        with lock:
            if not job_numbers:
                break
            tracking_number = job_numbers.pop(0)

        job_details = api.get_job(tracking_number)
        formatted_location = job_details['formattedLocation']
        if formatted_location == "European Union" or formatted_location == "EMEA":
            continue

        job_description = job_details['description']['text']
        job_title = job_details['title']
        job_posting_id = job_details['entityUrn'].split(':')[-1]
        job_url = f"https://www.linkedin.com/jobs/view/{job_posting_id}"

        job_info = {
            'title': job_title,
            'description': job_description,
            'url': job_url
        }

        with lock:
            all_jobs.append(job_info)
            job_counter += 1
            print(f"Vacancy {job_counter} added: {job_title}")


search_and_collect_jobs()

start_time = time.time()

# You can manage the number of threads here
threads = []
for _ in range(2):
    thread = threading.Thread(target=get_job_details)
    thread.start()
    threads.append(thread)

# Waiting for all threads to complete
for thread in threads:
    thread.join()

end_time = time.time()
execution_time = end_time - start_time

minutes = int(execution_time // 60)
seconds = execution_time % 60

print(f"The collection of vacancies was carried out for {minutes} minutes and {seconds:.2f} seconds")

listings = [(item['title'], item['description'], item['url']) for item in all_jobs]

with open('job_listings.json', 'w', encoding='utf-8') as file:
    json.dump(all_jobs, file, ensure_ascii=False, indent=4)

print("Information about vacancies is written to the file: job_listings.json")