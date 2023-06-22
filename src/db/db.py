from pymongo import MongoClient

# Provide the mongodb atlas url to connect python to mongodb using pymongo
# CONNECTION_STRING = "mongodb://192.168.138.129"
CONNECTION_STRING = "mongodb://hydro:HsyHcNGtKJmE4EUvXxMZNaAI9xiDZv03@127.0.0.1:27017/hydro"


def get_database():
    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['hydro']
