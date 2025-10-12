"""
Music Library Database Generator
===============================
This script creates a music database by fetching data from iTunes API.
It creates three related tables: artists, albums, and songs.
All files are saved in an 'exports' folder.
"""

import sqlite3
import os
import requests
import csv
from datetime import datetime

# Configuration
EXPORTS_FOLDER = "exports"
DB_FILE = os.path.join(EXPORTS_FOLDER, "music_library.sqlite")

# Artists to fetch from iTunes API
ARTISTS_TO_FETCH = [
    "Queen",
    "Led Zeppelin",
    "The Beatles",
    "Daft Punk",
    "Taylor Swift",
    "Kendrick Lamar",
    "Adele",
    "Sabrina Carpenter",
    "Gracie Abrams",
    "Chappel Roan",
]


def check_requirements():
    """Check if required libraries are installed."""
    try:
        import requests

        print("✓ All required libraries are available")
        return True
    except ImportError:
        print("=" * 50)
        print("ERROR: The 'requests' library is not installed.")
        print("Please install it by running this command in your terminal:")
        print("pip install requests")
        print("=" * 50)
        return False


def create_exports_folder():
    """Create the exports folder if it doesn't exist."""
    if not os.path.exists(EXPORTS_FOLDER):
        os.makedirs(EXPORTS_FOLDER)
        print(f"Created '{EXPORTS_FOLDER}' folder")
    else:
        print(f"Using existing '{EXPORTS_FOLDER}' folder")


def clean_old_database():
    """Remove old database file to start fresh."""
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Removed old database file: {DB_FILE}")


def create_database_tables(cursor):
    """Create the three main tables: artists, albums, songs."""
    print("Creating database tables...")

    # Enable foreign key support (important for table relationships)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Artists table - stores each artist once
    cursor.execute(
        """
    CREATE TABLE artists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """
    )

    # Albums table - stores albums and links to artists
    cursor.execute(
        """
    CREATE TABLE albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist_id INTEGER NOT NULL,
        genre TEXT,
        release_year INTEGER,
        FOREIGN KEY (artist_id) REFERENCES artists (id)
    );
    """
    )

    # Songs table - stores songs and links to albums
    cursor.execute(
        """
    CREATE TABLE songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        album_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (album_id) REFERENCES albums (id)
    );
    """
    )

    print("✓ Tables created successfully")


def fetch_songs_from_itunes(artist_name):
    """Fetch songs for an artist from iTunes API."""
    print(f"→ Fetching songs for '{artist_name}'...")

    # Build API URL
    url = f"https://itunes.apple.com/search?term={artist_name.replace(' ', '+')}&entity=song&limit=50"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        print(f"  Found {len(results)} songs")
        return results
    except requests.exceptions.RequestException as e:
        print(f"  ⚠ Error fetching data for {artist_name}: {e}")
        return []


def process_api_data(cursor):
    """Process all API data and insert into database."""
    print("\nProcessing music data...")

    # Keep track of what we've already added to avoid duplicates
    artist_cache = {}  # artist_name -> artist_id
    album_cache = {}  # (album_title, artist_id) -> album_id
    songs_to_add = []  # list of (song_title, album_id) tuples

    # Process each artist
    for artist_name in ARTISTS_TO_FETCH:
        api_results = fetch_songs_from_itunes(artist_name)

        for song_data in api_results:
            # Get the important information from the API
            artist_name_api = song_data.get("artistName")
            album_title = song_data.get("collectionName")
            song_title = song_data.get("trackName")

            # Skip if we're missing essential data
            if not all([artist_name_api, album_title, song_title]):
                continue

            # Handle the artist (add if new)
            if artist_name_api not in artist_cache:
                cursor.execute(
                    "INSERT INTO artists (name) VALUES (?)", (artist_name_api,)
                )
                artist_id = cursor.lastrowid
                artist_cache[artist_name_api] = artist_id
            else:
                artist_id = artist_cache[artist_name_api]

            # Handle the album (add if new)
            album_key = (album_title, artist_id)
            if album_key not in album_cache:
                # Try to get the release year
                release_year = None
                if "releaseDate" in song_data:
                    try:
                        release_year = datetime.strptime(
                            song_data["releaseDate"], "%Y-%m-%dT%H:%M:%SZ"
                        ).year
                    except ValueError:
                        pass  # If date format is weird, just skip it

                cursor.execute(
                    "INSERT INTO albums (title, artist_id, genre, release_year) VALUES (?, ?, ?, ?)",
                    (
                        album_title,
                        artist_id,
                        song_data.get("primaryGenreName"),
                        release_year,
                    ),
                )
                album_id = cursor.lastrowid
                album_cache[album_key] = album_id
            else:
                album_id = album_cache[album_key]

            # Add song to our list (we'll insert all songs at once later)
            songs_to_add.append((song_title, album_id))

    # Insert all songs at once (this is faster than one by one)
    if songs_to_add:
        print(f"Adding {len(songs_to_add)} songs to database...")
        cursor.executemany(
            "INSERT INTO songs (title, album_id) VALUES (?, ?)", songs_to_add
        )
        print(f"✓ Added {len(songs_to_add)} songs")
        print(
            f"✓ Database now has {len(artist_cache)} artists and {len(album_cache)} albums"
        )
    else:
        print("⚠ No songs were processed")


def export_table_to_csv(cursor, table_name):
    """Export a database table to a CSV file."""
    csv_file = os.path.join(EXPORTS_FOLDER, f"{table_name}.csv")

    # Get all data from the table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print(f"⚠ Table '{table_name}' is empty, skipping CSV export")
        return

    # Get column names
    column_names = [description[0] for description in cursor.description]

    # Write to CSV file
    with open(csv_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(column_names)  # Write headers
        writer.writerows(rows)  # Write data

    print(f"✓ Exported {len(rows)} rows from '{table_name}' to {csv_file}")


def export_all_tables_to_csv(cursor):
    """Export all tables to CSV files."""
    print("\nExporting tables to CSV files...")
    tables = ["artists", "albums", "songs"]

    for table in tables:
        export_table_to_csv(cursor, table)


def main():
    """Main function that runs everything step by step."""
    print("Music Library Database Generator")
    print("=" * 40)

    # Step 1: Check if we have everything we need
    if not check_requirements():
        return

    # Step 2: Create the exports folder
    create_exports_folder()

    # Step 3: Clean up old database
    clean_old_database()

    conn = None  # Initialize conn to None
    # Step 4: Create and populate the database
    try:
        # Connect to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print(f"✓ Connected to database: {DB_FILE}")

        # Create tables
        create_database_tables(cursor)

        # Get data from iTunes and add to database
        process_api_data(cursor)

        # Save changes
        conn.commit()
        print("✓ All changes saved to database")

        # Export to CSV files
        export_all_tables_to_csv(cursor)

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:  # Always close the database connection
        if conn:
            conn.close()  # Close the connection if it was successfully opened
            print("✓ Database connection closed")

    print(f"\n🎉 Done! Check the '{EXPORTS_FOLDER}' folder for your files:")
    print(f"   - music_library.sqlite (database)")
    print(f"   - artists.csv (artists table)")
    print(f"   - albums.csv (albums table)")
    print(f"   - songs.csv (songs table)")


# Run the program when this file is executed
if __name__ == "__main__":
    main()
