from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

client = MongoClient("mongodb+srv://<anto>:<ynHHkfVPz9AcSjR8>@nycbikes.2usntce.mongodb.net/?appName=NYCBikes", server_api=ServerApi('1'))

print(client)