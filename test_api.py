import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Changed from gemini-1.5-pro to gemini-2.5-flash
response = client.models.generate_content(
    model='gemini-2.5-flash', 
    contents='Say OK'
)

print(response.text)
