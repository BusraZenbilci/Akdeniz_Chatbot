from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

my_key = os.getenv("openai_apikey")

client = OpenAI(api_key=my_key)

AI_Response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125",
    temperature=0,
    max_tokens=256,
    messages=[
        {"role": "system", "content":"Sen yardımsever bir asistansın."},
        {"role": "user", "content": "Mevsimler neden oluşur? Dünya kendi etrafında döndüğü için mi?"}
    ]
)

print(AI_Response.choices[0].message.content)