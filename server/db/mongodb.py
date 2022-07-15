from pymongo.collection import Collection
from pymongo.database import Database
from pymongo import MongoClient

# In memory mongo client
from pymongo_inmemory import MongoClient as MemClient

client = MongoClient("mongodb://127.0.0.1:27017/?compressors=disabled&gssapiServiceName=mongodb")

def get_jobs_collection() -> Collection:
    return get_general_database().get_collection("jobs")

def get_distributions_collection() -> Collection:
    return get_general_database().get_collection("distributions")

def get_metadata_collection() -> Collection:
    return get_general_database().get_collection("metadata")

def get_tokens_collection(collectionName: str) -> Collection:
    return get_collection_database(collectionName).get_collection("tokens")

def get_collection_database(collectionName: str) -> Database:
    return client.get_database(collectionName)

def get_general_database() -> Database:
    return client.get_database("general")



