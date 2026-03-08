from dotenv import load_dotenv
import os

load_dotenv()

GITHUB_CLIENT_ID     = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GOOGLE_CLIENT_ID     = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
SECRET_KEY           = os.getenv('SECRET_KEY')
FERNET_KEY           = os.getenv('FERNET_KEY')


CONTRACT_ADDRESS    = os.getenv('CONTRACT_ADDRESS')
WALLET_ADDRESS      = os.getenv('WALLET_ADDRESS')
WALLET_PRIVATE_KEY  = os.getenv('WALLET_PRIVATE_KEY')
AMOY_RPC_URL        = os.getenv('AMOY_RPC_URL', 'https://rpc-amoy.polygon.technology')


# Render provides DATABASE_URL — use it if available, otherwise fall back to local config
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Render uses postgres:// but psycopg2 needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    DB_CONFIG = None  # signal to database.py to use URL instead
else:
    DB_CONFIG = {
        'dbname':   'identity_verifier',
        'user':     'postgres',
        'password': os.getenv('DB_PASSWORD', 'password'),
        'host':     'localhost',
        'port':     '5432'
    }

API_HOST = '0.0.0.0'
API_PORT = int(os.getenv('PORT', 5000))
DEBUG    = os.getenv('DEBUG', 'False') == 'True'