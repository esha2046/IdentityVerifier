from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_CLIENT_ID     = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GOOGLE_CLIENT_ID     = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SECRET_KEY           = os.getenv('SECRET_KEY')

DB_CONFIG = {
    'dbname': 'identity_verifier',
    'user': 'postgres',
    'password': 'password',  #if nothing is working please check if youve changed this to ur password
    'host': 'localhost',
    'port': '5432'
}


API_HOST = '0.0.0.0'
API_PORT = 5000
DEBUG = True