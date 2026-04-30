"""MongoDB initialization and connection module."""
import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure

# Get MongoDB URI from environment or use default
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/notesdb")
DB_NAME = "notesdb"
COLLECTION_NAME = "notes"


def get_client():
    return MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)


def get_database():
    client = get_client()
    return client[DB_NAME]


def init_db():
    try:
        client = get_client()
        db = client[DB_NAME]
        
        # Verify connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully")
        
        # Create collection if it doesn't exist
        if COLLECTION_NAME not in db.list_collection_names():
            db.create_collection(COLLECTION_NAME)
            print(f"Created collection '{COLLECTION_NAME}'")
            
            # Create indexes for better query performance
            db[COLLECTION_NAME].create_index([("created_at", 1)])
            db[COLLECTION_NAME].create_index([("done", 1)])
            print("Created indexes on 'created_at' and 'done'")
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists")
        
        print("MongoDB initialization complete")
        return True
        
    except ServerSelectionTimeoutError:
        print("Could not connect to MongoDB. Make sure it's running on the configured URI.")
        return False
    except OperationFailure as e:
        print(f"MongoDB operation failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error during MongoDB initialization: {e}")
        return False


if __name__ == "__main__":
    init_db()
