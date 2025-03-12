# homecloud/app/utils.py
import psycopg2
from dotenv import load_dotenv
import os
from PIL import Image
import io

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
THUMBNAIL_SIZE = (256, 256) # You can move this to config if needed.
def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def generate_thumbnail(file_path: str):
    """Generates a thumbnail from an image file and returns it as bytes."""
    try:
        with Image.open(file_path) as img:
            img.thumbnail(THUMBNAIL_SIZE)
            # Save the thumbnail to an in-memory byte stream
            with io.BytesIO() as output:
                img.save(output, format="JPEG")  # Or "PNG" if you prefer
                return output.getvalue()
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None