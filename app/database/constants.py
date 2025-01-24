import os

from dotenv import load_dotenv

load_dotenv('/Users/omniadmin/Desktop/invoice_remittance_project/app/database/.env')
# load_dotenv('app/database/.env')


DATABASE_HOST = os.getenv('database_host','')
DATABASE_USERNAME = os.getenv('database_username','')
DATABASE_PASSWORD = os.getenv('database_password','')
DATABASE_NAME = os.getenv('database_name','')

OPENAI_API_KEY = os.getenv('openai_api_key','')

if not DATABASE_HOST:
    raise Exception('Database Host IP not found')
elif not DATABASE_USERNAME:
    raise Exception('Database Username not found')
elif not DATABASE_PASSWORD:
    raise Exception('Database Password not found')
elif not DATABASE_NAME:
    raise Exception('Database Name not found')
elif not OPENAI_API_KEY:
    raise Exception('OpenAI API Key not found')