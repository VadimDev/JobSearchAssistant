from openai import OpenAI

client = OpenAI()

completion = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You should return something funny but short that will represents `200 OK response`."},
    {"role": "user", "content": "Everything is okay?"}
  ]
)

print(completion.choices[0].message)
