# homecloud/app/views.py
from flask import Blueprint, request, jsonify, send_file
from .utils import get_db_connection, generate_thumbnail
from .telegram_bot import upload_photo, download_photo  # Import from telegram_bot.py
import os
import io

main_bp = Blueprint('main', __name__)

@main_bp.route('/upload', methods=['POST'])
async def upload():
    try:
        if 'photo' not in request.files:
            return jsonify({'error': 'No photo provided'}), 400

        photo = request.files['photo']
        temp_filename = f"temp_{photo.filename}"
        photo.save(temp_filename)
        photo_id = await upload_photo(temp_filename)  # Call the function from telegram_bot
        os.remove(temp_filename)

        if photo_id:
            return jsonify({'message': 'Photo uploaded', 'photo_id': photo_id}), 201
        else:
            return jsonify({'error': 'Failed to upload photo'}), 500
    except Exception as e:
        print(f"Error in upload route: {e}")  # Log the error
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


@main_bp.route('/list', methods=['GET'])
def list_photos():
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Failed to connect to database'}), 500
        cur = conn.cursor()
        cur.execute("SELECT id, file_name, file_size, upload_date, metadata FROM photos")
        photos = []
        for row in cur.fetchall():
            photo_id, file_name, file_size, upload_date, metadata = row
            photos.append({
                'id': photo_id,
                'file_name': file_name,
                'file_size': file_size,
                'upload_date': upload_date.isoformat(),
                'metadata': metadata
            })
        return jsonify(photos), 200
    except Exception as e:
        print(f'Exception while listing {e}')
        return jsonify({'error': 'Failed to list photos', 'details': str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@main_bp.route('/download/<file_unique_id>', methods=['GET'])
async def download(file_unique_id):
    try:
        temp_download_path = f"/tmp/downloaded_{file_unique_id}.jpg"
        success = await download_photo(file_unique_id, temp_download_path)
        if success:
            return_data = io.BytesIO()
            with open(temp_download_path, 'rb') as fo:
                return_data.write(fo.read())
            return_data.seek(0)
            os.remove(temp_download_path)
            return send_file(return_data, mimetype='image/jpeg', as_attachment=True, download_name=f'{file_unique_id}.jpg')
        else:
            return jsonify({'error': 'Failed to download photo'}), 404
    except Exception as e:
        print(f'Exception while downloading: {e}')
        return jsonify({'error': str(e)}), 500

@main_bp.route('/thumbnail/<file_unique_id>', methods=['GET'])
async def get_thumbnail(file_unique_id):
     try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'error': 'Failed to connect to database'}), 500
        cur = conn.cursor()
        # 1.  Fetch the thumbnail data from the database
        cur.execute("SELECT metadata FROM photos WHERE file_unique_id = %s", (file_unique_id,))
        result = cur.fetchone()
        if not result:
            return jsonify({'error': 'Photo not found'}), 404
        metadata = result[0]

        if 'thumbnail_file_id' not in metadata:
            return jsonify({'error': 'Thumbnail not found'}), 404

        thumb_file_id = metadata['thumbnail_file_id']

        # 2. Download from telegram.
        temp_thumb_path = f"/tmp/thumb_{file_unique_id}.jpg"
        thumb_result = await tg.download_file(file_id=thumb_file_id, destination=temp_thumb_path) # tg is available globally.
        thumb_result.wait()

        if thumb_result.error:
            return jsonify({'error': f'Thumbnail download error: {thumb_result.error}'}), 500
        # 3. Send the thumbnail data as response
        return_data = io.BytesIO()
        with open(temp_thumb_path, 'rb') as fo:
            return_data.write(fo.read())
        return_data.seek(0)
        os.remove(temp_thumb_path) # Clean up
        return send_file(return_data, mimetype='image/jpeg')

     except Exception as e:
        print(f"Error retrieving thumbnail: {e}")
        return jsonify({'error': 'Failed to retrieve thumbnail', 'details': str(e)}), 500 # Added details
     finally:
        if conn:
            cur.close()
            conn.close()