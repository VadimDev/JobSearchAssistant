import json
import time
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import tiktoken

# API limits
TPM_LIMIT = 200000  # Token limit per minute
RPM_LIMIT = 500  # Requests per minute limit
MAX_WORKERS = 3  # Number of threads for concurrent processing

# Initialize tiktoken encoder
encoder = tiktoken.encoding_for_model("gpt-4o-mini")

# Function to load job listings from file and count tokens in descriptions
def extract_listings_with_tokens(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    listings_with_tokens = []
    for item in data:
        title = item['title']
        description = item['description']
        url = item['url']
        token_count = len(encoder.encode(description))
        listings_with_tokens.append((title, description, url, token_count))
    return listings_with_tokens

# Function to analyze job listings considering API limits
def analyze_listing(client, title, description, url, token_count, tokens_used, request_count, lock, thread_id):
    messages = [
        {"role": "system",
         "content": "You help me find vacancies for C++ developer, Go developer, Rust developer, game developer, trainee Cloud positions. Respond with 'yes' if the job is suitable, otherwise respond with 'no'. Answer is limited to 3 characters."},
        {"role": "user",
         "content": f"Is this job opening suitable for C++ developer, Go developer, Rust developer, game developer, trainee Cloud?\n\n{description}"}
    ]

    while True:
        with lock:
            total_tokens_needed = tokens_used[0] + token_count + 1  # Include 1 token for the completion
            print(f"[Thread {thread_id}] Total tokens needed: {total_tokens_needed}, Tokens used: {tokens_used[0]}")

            if total_tokens_needed > TPM_LIMIT:
                time_to_wait = 60 - (time.time() % 60)
                print(f"[Thread {thread_id}] Reached token limit. Waiting for {time_to_wait:.2f} seconds to reset token counter.")
                time.sleep(time_to_wait)
                tokens_used[0] = 0  # Reset the token counter after waiting

            if request_count[0] >= RPM_LIMIT:
                time_to_wait = 60 - (time.time() % 60)
                print(f"[Thread {thread_id}] Reached request limit. Waiting for {time_to_wait:.2f} seconds to reset request counter.")
                time.sleep(time_to_wait)
                request_count[0] = 0  # Reset the request counter after waiting

            tokens_used[0] += token_count + 1  # Update token usage
            request_count[0] += 1  # Update request count

        print(f"[Thread {thread_id}] Sending request for job: {title}")
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1
        )
        response = completion.choices[0].message.content.strip().lower()
        print(f"[Thread {thread_id}] Received response for job: {title}, response: {response}")

        if response == 'yes':
            return f"{title} - {url}\n"
        return None

# Function to process a chunk of job listings
def process_chunk(chunk, tokens_used, request_count, lock, thread_id):
    client = OpenAI()  # Create a new client instance for each thread
    results = []
    for title, description, url, token_count in chunk:
        print(f"[Thread {thread_id}] Processing job: {title}")
        result = analyze_listing(client, title, description, url, token_count, tokens_used, request_count, lock, thread_id)
        if result:
            results.append(result)
    return results

# Main execution
json_file = 'job_listings.json'  # Use the path to the uploaded file
listings = extract_listings_with_tokens(json_file)

tokens_used = [0]  # Variable to track used tokens in the current minute
request_count = [0]  # Variable to track the number of requests in the current minute
lock = Lock()

# Split listings into chunks for each thread
chunks = [listings[i::MAX_WORKERS] for i in range(MAX_WORKERS)]

start_time = time.time()

results = []

# Use ThreadPoolExecutor to manage worker threads
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(process_chunk, chunk, tokens_used, request_count, lock, i) for i, chunk in enumerate(chunks)]

    for future in as_completed(futures):
        chunk_results = future.result()
        results.extend(chunk_results)

with open('results.txt', 'w', encoding='utf-8') as file:
    for result in results:
        file.write(result)

end_time = time.time()
execution_time = end_time - start_time

minutes = int(execution_time // 60)
seconds = execution_time % 60

print(f"AI analysis was performed in {minutes} minutes and {seconds:.2f} seconds")
print(f"Total jobs processed: {len(listings)}")
