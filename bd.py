from time import time
from pymongo import MongoClient

MONGO_DB_PROTOCOL = "mongodb://"
DATABASE_NAME = "ecibot"

class Database:
    def __init__(self, user, password, url):
        self.database = MongoClient(f"{MONGO_DB_PROTOCOL}{user}:{password}@{url}/")
        self.stats_collection = self.database["stats"]


    def get_database(self):
        return self.database
    

    def get_stats_collection(self):
        return self.stats_collection
    

    def register_user_interaction(self, username, command, sound):
        now = time() * 1000
        item = {
            "username": username,
            "commandName": command,
            "soundName": sound,
            "timestamp": now
        }
        self.get_stats_collection().insertOne(item)


if __name__ == "__main__":
    db = Database("admin", "pass", "db")
    db.register_user_interaction("wokis", "p", "a")
