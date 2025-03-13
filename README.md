# HomeCloud

HomeCloud is a Flask-based web application that allows users to upload, list, and download photos. It also integrates with Telegram to upload photos and generate thumbnails.

## Features

- Upload photos via a web interface or Telegram bot.
- Generate and store thumbnails for uploaded photos.
- List uploaded photos with metadata.
- Download photos and thumbnails.
- Integration with PostgreSQL for storing photo metadata.
- Docker support for easy deployment.
- Hot-reloading in development for faster iteration.

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

2. (For Local Development) Create a virtual environment and activate it:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```sh
    pip install .
    ```

4. Create a `.env` root file and set the following environment variables:
    ```env
    API_ID=<Telegram API_ID>
    API_HASH=<Telegram API_HASH>
    PHONE_NUMBER=<Telegram PHONE_NUMBER>
    BOT_TOKEN=<Telegram PHONE_NUMBER>
    CHAT_ID=<Telegram CHAT_ID>
    DATABASE_URL=DATABASE_URL=postgresql://your_postgres_user:your_postgres_password@localhost:5432/your_postgres_db
    DATABASE_ENCRYPTION_KEY=<Secure Encryption Key>
    TDLIB_FILES_DIRECTORY=<tdlib_data Directory Path>
    APP_PORT=<Default 5000>
    
    # for pgadmin
    POSTGRES_USER=your_postgres_user
    POSTGRES_PASSWORD=your_postgres_password
    POSTGRES_DB=your_postgres_db
    PGADMIN_DEFAULT_EMAIL=your_pgadmin_email
    PGADMIN_DEFAULT_PASSWORD=your_pgadmin_password
    ```

### Running the Application

1.  Run with Docker (Recommended)

    ```sh
    docker-compose up -d --build
    ```

    Check Logs:
    ```sh
    docker-compose logs -f web
    ```

(2) Run Locally (Without Docker)

    Initialize the database (if needed):
    ```sh
    flask db upgrade
    ```

    Start the Flask app:
    ```sh
    python run.py
    ```

2. Access the application at `http://localhost:5000`. Use same port as defined by APP_PORT in .env

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


