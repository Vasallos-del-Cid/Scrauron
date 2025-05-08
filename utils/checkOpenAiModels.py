from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) # TODO INTRODUCE AQUI TU TOKEN DE GPT 

models = client.models.list()

for m in models.data:
    print(m.id)