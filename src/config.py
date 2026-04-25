# /src/config.py

from dotenv import load_dotenv
import os

# load dotenv file
load_dotenv()
# get api_key from dotenv file
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL')