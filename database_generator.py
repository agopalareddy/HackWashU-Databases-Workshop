"""
Music Library Database Generator
=================================
A beginner-friendly script that:
1. Fetches music data from iTunes API
2. Saves it to a SQLite database
3. Exports tables to CSV files

Created for HackWashU Databases Workshop
"""

import csv
import os
import sqlite3
import requests

# ============================================
# CONFIGURATION - Change these if you want!
# ============================================

# List of artists to search for
ARTISTS = [
    "Sabrina Carpenter",
    "Gracie Abrams",
    "Chappel Roan",
    "Halsey",
    "Tate McRae",
    "Conan Gray",
    "Twenty One Pilots",
    "Taylor Swift",
    "Michael Jackson",
    "The Beatles",
    "Daft Punk",
]

# How many songs to fetch per artist
SONGS_PER_ARTIST = 50

# Where to save files
EXPORTS_FOLDER = "exports"
DATABASE_FILE = os.path.join(EXPORTS_FOLDER, "music_library.db")


# ============================================
# STEP 1: CREATE DATABASE TABLES
# ============================================


def create_tables(cursor):
    """
    Create three tables for our music library:
    - artists: stores artist names
    - albums: stores album info (linked to artists)
    - songs: stores song names (linked to albums)
    """
    print("\n📋 Creating database tables...")

    # Enable foreign keys (this makes table relationships work)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table 1: Artists
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
    """
    )

    # Table 2: Albums (connected to artists)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS albums (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            artist_id INTEGER NOT NULL,
            genre TEXT,
            year INTEGER,
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        )
    """
    )

    # Table 3: Songs (connected to albums)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            album_id INTEGER NOT NULL,
            FOREIGN KEY (album_id) REFERENCES albums(id)
        )
    """
    )

    print("✅ Tables created!")


# ============================================
# STEP 2: FETCH DATA FROM ITUNES API
# ============================================


def fetch_songs_from_itunes(artist_name):
    """
    Fetch songs from the iTunes API for a given artist.
    Returns a list of song data (or empty list if error).
    """
    print(f"\n🔍 Searching iTunes for '{artist_name}'...")

    # Build the API URL (replace spaces with + signs)
    search_term = artist_name.replace(" ", "+")
    url = f"https://itunes.apple.com/search?term={search_term}&entity=song&limit={SONGS_PER_ARTIST}"

    try:
        # Make the request to iTunes
        response = requests.get(url, timeout=10)
        data = response.json()
        results = data.get("results", [])

        print(f"   Found {len(results)} songs!")
        return results

    except Exception as error:
        print(f"   ⚠️ Error: {error}")
        return []


# ============================================
# STEP 3: SAVE DATA TO DATABASE
# ============================================


def save_to_database(cursor, all_songs):
    """
    Save all the song data to our database tables.
    We use dictionaries to avoid duplicate entries.
    """
    print("\n💾 Saving to database...")

    # Dictionaries to track what we've already saved
    saved_artists = {}  # artist_name -> artist_id
    saved_albums = {}  # (album_title, artist_id) -> album_id

    song_count = 0

    # Go through each song from the API
    for song in all_songs:
        # Get the data we need from the API response
        artist_name = song.get("artistName")
        album_title = song.get("collectionName")
        song_title = song.get("trackName")
        genre = song.get("primaryGenreName")
        release_date = song.get("releaseDate", "")

        # Skip if missing important data
        if not artist_name or not album_title or not song_title:
            continue

        # Get year from date (e.g., "2024-10-15T07:00:00Z" -> 2024)
        year = None
        if release_date:
            year = release_date.split("-")[0]  # Get first part before "-"
            try:
                year = int(year)
            except:
                year = None

        # STEP 1: Save artist (if we haven't already)
        if artist_name not in saved_artists:
            cursor.execute(
                "INSERT OR IGNORE INTO artists (name) VALUES (?)", (artist_name,)
            )
            cursor.execute("SELECT id FROM artists WHERE name = ?", (artist_name,))
            saved_artists[artist_name] = cursor.fetchone()[0]

        artist_id = saved_artists[
            artist_name
        ]  # STEP 2: Save album (if we haven't already)
        album_key = (album_title, artist_id)
        if album_key not in saved_albums:
            cursor.execute(
                "INSERT INTO albums (title, artist_id, genre, year) VALUES (?, ?, ?, ?)",
                (album_title, artist_id, genre, year),
            )
            saved_albums[album_key] = cursor.lastrowid

        album_id = saved_albums[album_key]

        # STEP 3: Save song
        cursor.execute(
            "INSERT INTO songs (title, album_id) VALUES (?, ?)", (song_title, album_id)
        )
        song_count += 1

    print(
        f"✅ Saved {len(saved_artists)} artists, {len(saved_albums)} albums, {song_count} songs!"
    )


# ============================================
# STEP 4: EXPORT TO CSV FILES
# ============================================


def export_to_csv(cursor, table_name):
    """
    Export a database table to a CSV file.
    CSV = Comma Separated Values (opens in Excel!)
    Uses Python's built-in csv module for proper formatting.
    """
    # Get all data from the table
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if not rows:
        print(f"   ⚠️ Table '{table_name}' is empty")
        return

    # Get column names (like "id", "name", etc.)
    columns = [description[0] for description in cursor.description]

    # Write to CSV file using csv module
    filename = os.path.join(EXPORTS_FOLDER, f"{table_name}.csv")
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # Write header row
        writer.writerow(columns)

        # Write all data rows
        writer.writerows(rows)

    print(f"   ✅ Exported {len(rows)} rows to {filename}")


# ============================================
# MAIN PROGRAM
# ============================================


def main():
    """
    Main function that runs the whole program!
    """
    print("=" * 50)
    print("🎵 MUSIC LIBRARY DATABASE GENERATOR")
    print("=" * 50)

    # Create exports folder if it doesn't exist
    if not os.path.exists(EXPORTS_FOLDER):
        os.makedirs(EXPORTS_FOLDER)
        print(f"✅ Created '{EXPORTS_FOLDER}' folder")

    # Connect to database (creates file if it doesn't exist)
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()
    print(f"✅ Connected to database: {DATABASE_FILE}")

    # Create our three tables
    create_tables(cursor)

    # Fetch songs from iTunes for each artist
    all_songs = []
    for artist in ARTISTS:
        songs = fetch_songs_from_itunes(artist)
        all_songs.extend(songs)  # Add to our master list

    print(f"\n📊 Total songs collected: {len(all_songs)}")

    # Save everything to the database
    if all_songs:
        save_to_database(cursor, all_songs)
        connection.commit()  # Save changes permanently

    # Export to CSV files
    print("\n📄 Exporting to CSV files...")
    export_to_csv(cursor, "artists")
    export_to_csv(cursor, "albums")
    export_to_csv(cursor, "songs")

    # Close the database connection
    connection.close()

    print("\n" + "=" * 50)
    print("🎉 ALL DONE!")
    print("=" * 50)
    print(f"Check the '{EXPORTS_FOLDER}' folder for these files:")
    print(f"  • music_library.db (SQLite database)")
    print(f"  • artists.csv")
    print(f"  • albums.csv")
    print(f"  • songs.csv")
    print("\nOpen the .db file in a SQLite viewer to explore!")


# This runs the program when you execute the file
if __name__ == "__main__":
    main()
