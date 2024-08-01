import json
import time
from openai import OpenAI

def extract_listings(json_file):
  with open(json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

  listings = [(item['title'], item['description'], item['url']) for item in data]
  return listings

client = OpenAI()
json_file = 'job_listings.json'
listings = extract_listings(json_file)

start_time = time.time()

with open('results.txt', 'w', encoding='utf-8') as file:
  for title, description, url in listings:
    completion = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system",
         "content": "You help me find vacancies for android developer. Respond with 'yes' if the job is suitable, otherwise respond with 'no'. Answer is limited to 3 characters"},
        {"role": "user", "content": f"Is this job opening suitable for an android developer?\n\n{description}"}
      ],
      max_tokens=3
    )

    response = completion.choices[0].message.content.strip().lower()
    # We write the result to the file only if the answer is "yes"
    if response == 'yes':
      file.write(f"{title} - {url}\n")

end_time = time.time()
execution_time = end_time - start_time

minutes = int(execution_time // 60)
seconds = execution_time % 60

print(f"AI analysis was performed in {minutes} minutes and {seconds:.2f} seconds")