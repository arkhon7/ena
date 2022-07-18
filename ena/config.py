import dotenv
import os

dotenv.load_dotenv()


TOKEN = os.getenv("TEST_TOKEN")
DB_STRING = os.getenv("TEST_DB_STRING")
SYNC_DB_STRING = os.getenv("TEST_SYNC_DB_STRING")
