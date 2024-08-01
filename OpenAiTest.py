from openai import OpenAI
from dotenv import load_dotenv
import os

# load dotenv variables
load_dotenv()

client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY"),
)

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You should return something funny but short that will represents `200 OK response`."},
    {"role": "user", "content": "Everything is okay?"}
  ]
)

print(completion.choices[0].message)