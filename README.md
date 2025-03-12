# HomeCloud

HomeCloud is a Flask-based web application that allows users to upload, list, and download photos. It also integrates with Telegram to upload photos and generate thumbnails.

## Features

- Upload photos via a web interface or Telegram bot
- Generate and store thumbnails for uploaded photos
- List uploaded photos with metadata
- Download photos and thumbnails
- Integration with PostgreSQL for storing photo metadata
- Docker support for easy deployment

## Setup

### Prerequisites

- Python 3.11
- Docker and Docker Compose
- PostgreSQL

### Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/homecloud.git
    cd homecloud
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file and set the following environment variables:

    ```env
    DATABASE_URL=your_database_url
    BOT_TOKEN=your_telegram_bot_token
    CHAT_ID=your_telegram_chat_id
    POSTGRES_USER=your_postgres_user
    POSTGRES_PASSWORD=your_postgres_password
    POSTGRES_DB=your_postgres_db
    PGADMIN_DEFAULT_EMAIL=your_pgadmin_email
    PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
    ```

5. Start the Docker containers:

    ```sh
    docker-compose up -d
    ```

6. Initialize the database (if needed):

    ```sh
    flask db upgrade
    ```

### Running the Application

1. Run the Flask application:

    ```sh
    python run.py
    ```

2. Access the application at `http://localhost:8888`.

### Running the Telegram Bot

The Telegram bot will start automatically when the Flask application is run. Ensure that the `BOT_TOKEN` and `CHAT_ID` environment variables are set correctly.

## Usage

### Uploading Photos

- Via Web Interface: Use the `/upload` endpoint to upload photos.
- Via Telegram: Send photos to the bot.

### Listing Photos

- Use the `/list` endpoint to list all uploaded photos.

### Downloading Photos

- Use the `/download/<file_unique_id>` endpoint to download a specific photo.

### Getting Thumbnails

- Use the `/thumbnail/<file_unique_id>` endpoint to get the thumbnail of a specific photo.


