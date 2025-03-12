from telegram import Bot
from flask import request
from telegram.error import TelegramError
from dotenv import load_dotenv
import os
import asyncio
import json

load_dotenv()

# --- Configuration ---
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Initialize the bot
bot = Bot(token=BOT_TOKEN)

async def start_tdlib():
    """Starts the bot and checks authorization."""
    try:
        me = await bot.get_me()
        print(f"Logged in as @{me.username} (ID: {me.id})")
    except TelegramError as e:
        print(f"Login failed: {e}")

async def stop_tdlib():
    """Stops the bot."""
    # No explicit stop method is needed for python-telegram-bot
    print("Bot stopped")

async def upload_photo(file_path: str):
    """Uploads a photo to Telegram and stores metadata in the database."""
    from .utils import get_db_connection, generate_thumbnail
    
    try:
        conn = get_db_connection()
        if conn is None:
            print("Failed to get database connection.")  # Log
            return None
        cur = conn.cursor()

        # Check if the file exists
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return None

        # Extract the file name with extension
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        file_name_with_extension = os.path.basename(file_path)

        # Initialize the bot (ensure it's created in the same event loop)
        bot = Bot(token=os.getenv("BOT_TOKEN"))

        # Upload the photo
        with open(file_path, 'rb') as photo_file:
            message = await bot.send_photo(
                chat_id=os.getenv("CHAT_ID"),  # Replace with your chat ID
                photo=photo_file,
                caption=file_name_with_extension  # Use the full file name with extension
            )

        file_id = message.photo[-1].file_id  # Get the highest resolution photo's file ID
        file_unique_id = message.photo[-1].file_unique_id

        # Generate and upload thumbnail
        thumbnail_bytes = generate_thumbnail(file_path)
        if thumbnail_bytes:
            thumb_message = await bot.send_photo(
                chat_id=os.getenv("CHAT_ID"),  # Replace with your chat ID
                photo=thumbnail_bytes,
                caption=f"Thumbnail for {file_name_with_extension}"
            )
            thumb_file_id = thumb_message.photo[-1].file_id
            thumb_file_unique_id = thumb_message.photo[-1].file_unique_id
        else:
            print("Thumbnail generation failed. Skipping thumbnail upload.")
            thumb_file_id = None
            thumb_file_unique_id = None

        # Serialize the metadata dictionary to JSON
        metadata = {
            'thumbnail_file_id': thumb_file_id,
            'thumbnail_file_unique_id': thumb_file_unique_id
        }
        metadata_json = json.dumps(metadata)  # Convert dictionary to JSON string

        # Insert metadata into the database
        cur.execute(
            """
            INSERT INTO photos (telegram_message_id, telegram_chat_id, file_unique_id, file_id,
                               file_name, file_extension, file_size, upload_date, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """,
            (
                message.message_id,
                message.chat.id,
                file_unique_id,
                file_id,
                file_name,  # Store the file name without extension
                file_extension,  # Store the file extension
                os.path.getsize(file_path),
                message.date,
                metadata_json  # Insert the JSON string
            )
        )
        photo_id = cur.fetchone()[0]
        conn.commit()
        print(f"Photo uploaded and metadata stored. Photo ID: {photo_id}")
        return photo_id

    except TelegramError as e:
        print(f"Telegram upload error: {e}")  # Log
        if conn:
            conn.rollback()
        return None
    except Exception as e:
        print(f"Error uploading photo: {e}")  # Log
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            cur.close()
            conn.close()

async def download_photo(file_unique_id: str, output_path: str):
    """Downloads a photo from Telegram."""
    from .utils import get_db_connection

    try:
        conn = get_db_connection()
        if conn is None:
            return False
        cur = conn.cursor()
        cur.execute("SELECT file_id FROM photos WHERE file_unique_id = %s", (file_unique_id,))
        result = cur.fetchone()
        if not result:
            print(f"Error: Photo not found for unique ID: {file_unique_id}")
            return False
        file_id = result[0]

        # Download file
        file = await bot.get_file(file_id)
        await file.download_to_drive(output_path)
        print(f'Downloaded to {output_path}')
        return True

    except TelegramError as e:
        print(f"Telegram download error: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"Error downloading photo: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            cur.close()
            conn.close()

def message_handler(update):
    """Handles incoming messages synchronously."""
    from .utils import get_db_connection  # Import locally
    import re
    
    if update['@type'] != 'message':
        return
        
    message = update
    # Get my user ID to compare
    me = tg.get_me()
    me.wait()
    my_id = me.update['id']
    
    # Ensure that the message is from your bot
    if message.get('sender_user_id') != my_id:
        return

    if message['content']['@type'] == 'messageText':
        text = message['content']['text']['text']
        chat_id = message['chat_id']

        if text.startswith('/list'):
            asyncio.create_task(list_photos_command(chat_id, text))
        elif text.startswith('/search'):
            asyncio.create_task(search_photos_command(chat_id, text))
        elif text.startswith('/help'):
            asyncio.create_task(help_command(chat_id))
        elif text.startswith('/delete'):
            asyncio.create_task(delete_photo_command(chat_id, text))
        else:
            tg.send_message(
                chat_id=chat_id,
                input_message_content={
                    '@type': 'inputMessageText',
                    'text': {'@type': 'formattedText', 'text': "Unknown command. Type /help for available commands."}
                }
            )

# Update the remaining command functions similarly...
async def list_photos_command(chat_id: int, text: str):
    """Fetches and sends a list of photos."""
    from .utils import get_db_connection  # Import locally
    import re

    try:
        conn = get_db_connection()
        if conn is None:
            return
        cur = conn.cursor()

        # Parse limit (optional)
        match = re.match(r'/list\s*(\d+)?', text)
        limit = int(match.group(1)) if match and match.group(1) else 10  # Default to 10

        cur.execute("SELECT id, file_name, file_unique_id FROM photos ORDER BY upload_date DESC LIMIT %s", (limit,))
        photos = cur.fetchall()

        if photos:
            response_text = "Photos (most recent):\n"
            for photo_id, file_name, file_unique_id in photos:
                response_text += f"- ID: {photo_id}, Name: {file_name}, Unique ID: {file_unique_id}\n"
        else:
            response_text = "No photos found."

        tg.send_message(
            chat_id=chat_id,
            input_message_content={
                '@type': 'inputMessageText',
                'text': {'@type': 'formattedText', 'text': response_text}
            }
        )

    except Exception as e:
        print(f"Error in list_photos_command: {e}")
        tg.send_message(
            chat_id=chat_id,
            input_message_content={
                '@type': 'inputMessageText',
                'text': {'@type': 'formattedText', 'text': f"Error: {e}"}
            }
        )
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()

