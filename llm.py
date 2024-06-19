import requests
import json
import os
from dotenv import load_dotenv


load_dotenv()
URL = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={os.getenv("GEMINI_API_KEY")}'


async def get_ai_response(prompt):
    headers = {'Content-Type': 'application/json'}
    data = {"contents":[{"parts":[{"text":str(prompt)}]}]}
    response = requests.post(URL, headers=headers, data=json.dumps(data))
    
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


if __name__ == '__main__':
    import asyncio
    res = asyncio.run(get_ai_response("Hello, how are you doing?"))
    print(res)