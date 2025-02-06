from pymongo import MongoClient
import recommendation.config as config

class Database:
    _client = None
    _db = None

    @classmethod
    def get_connection(cls):
        """Initialize and return the database connection."""
        if cls._client is None:
            cls._client = MongoClient(config.MONGO_URI)
            cls._db = cls._client[config.DATABASE_NAME]
            print("✅ MongoDB Connection Established")
        return cls._db

    @classmethod
    def get_collection(cls, collection_name):
        """Get a specific collection from the database."""
        if cls._db is None:
            cls.get_connection()
        return cls._db[collection_name]
