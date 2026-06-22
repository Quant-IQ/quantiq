import os
from dotenv import load_dotenv
from dhanhq import dhanhq


load_dotenv()
client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")


dhan = dhanhq(client_id, access_token)

print("Successfully connected to Dhan API!")