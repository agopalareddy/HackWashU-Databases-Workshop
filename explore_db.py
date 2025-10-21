"""
Database Explorer for Music Library
====================================
This script analyzes and displays statistics from the music library database.
It provides insights into artists, albums, songs, and their relationships.
"""

import sqlite3
import os

# Database configuration
EXPORTS_FOLDER = "exports"
DATABASE_FILE = os.path.join(EXPORTS_FOLDER, "music_library.db")


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def get_basic_statistics(cursor):
    """Display basic record counts for all tables."""
    print_section("DATABASE OVERVIEW")

    tables = ["artists", "albums", "songs"]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table.capitalize():.<20} {count:>5} records")


def get_top_artists(cursor, limit=10):
    """Display artists ranked by number of albums."""
    print_section("TOP ARTISTS BY ALBUM COUNT")

    cursor.execute(
        """
        SELECT 
            a.name,
            COUNT(DISTINCT al.id) as album_count,
            COUNT(s.id) as song_count
        FROM artists a
        JOIN albums al ON al.artist_id = a.id
        JOIN songs s ON s.album_id = al.id
        GROUP BY a.id, a.name
        ORDER BY album_count DESC, song_count DESC
        LIMIT ?
    """,
        (limit,),
    )

    print(f"\n  {'Artist':<30} {'Albums':<10} {'Songs':<10}")
    print("  " + "-" * 50)

    for row in cursor.fetchall():
        artist, albums, songs = row
        print(f"  {artist:<30} {albums:<10} {songs:<10}")


def get_genre_distribution(cursor):
    """Display distribution of albums by genre."""
    print_section("GENRE DISTRIBUTION")

    cursor.execute(
        """
        SELECT 
            COALESCE(genre, 'Unknown') as genre,
            COUNT(DISTINCT id) as album_count,
            COUNT(DISTINCT artist_id) as artist_count
        FROM albums
        GROUP BY genre
        ORDER BY album_count DESC
        LIMIT 15
    """
    )

    print(f"\n  {'Genre':<25} {'Albums':<10} {'Artists':<10}")
    print("  " + "-" * 45)

    for row in cursor.fetchall():
        genre, albums, artists = row
        print(f"  {genre:<25} {albums:<10} {artists:<10}")


def get_year_distribution(cursor):
    """Display albums by release year."""
    print_section("ALBUMS BY RELEASE YEAR")

    cursor.execute(
        """
        SELECT 
            year,
            COUNT(*) as album_count
        FROM albums
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY year DESC
        LIMIT 20
    """
    )

    print(f"\n  {'Year':<10} {'Albums':<10} {'Bar Chart'}")
    print("  " + "-" * 50)

    for row in cursor.fetchall():
        year, count = row
        bar = "#" * (count // 2) if count > 0 else ""
        print(f"  {year:<10} {count:<10} {bar}")


def get_prolific_albums(cursor, limit=10):
    """Display albums with the most songs."""
    print_section("ALBUMS WITH MOST SONGS")

    cursor.execute(
        """
        SELECT 
            al.title,
            a.name as artist,
            al.year,
            COUNT(s.id) as song_count
        FROM albums al
        JOIN artists a ON al.artist_id = a.id
        JOIN songs s ON s.album_id = al.id
        GROUP BY al.id, al.title, a.name, al.year
        ORDER BY song_count DESC
        LIMIT ?
    """,
        (limit,),
    )

    print(f"\n  {'Album':<35} {'Artist':<25} {'Year':<8} {'Songs'}")
    print("  " + "-" * 75)

    for row in cursor.fetchall():
        album, artist, year, songs = row
        year_str = str(year) if year else "N/A"
        print(f"  {album[:34]:<35} {artist[:24]:<25} {year_str:<8} {songs}")


def get_recent_albums(cursor, limit=10):
    """Display most recent albums."""
    print_section("MOST RECENT ALBUMS")

    cursor.execute(
        """
        SELECT 
            al.title,
            a.name as artist,
            al.year,
            al.genre,
            COUNT(s.id) as song_count
        FROM albums al
        JOIN artists a ON al.artist_id = a.id
        JOIN songs s ON s.album_id = al.id
        WHERE al.year IS NOT NULL
        GROUP BY al.id, al.title, a.name, al.year, al.genre
        ORDER BY al.year DESC
        LIMIT ?
    """,
        (limit,),
    )

    print(f"\n  {'Album':<30} {'Artist':<20} {'Year':<8} {'Genre':<15}")
    print("  " + "-" * 73)

    for row in cursor.fetchall():
        album, artist, year, genre, songs = row
        genre_str = genre[:14] if genre else "N/A"
        print(f"  {album[:29]:<30} {artist[:19]:<20} {year:<8} {genre_str:<15}")


def get_artist_diversity(cursor):
    """Show artists with most diverse genres."""
    print_section("GENRE DIVERSITY BY ARTIST")

    cursor.execute(
        """
        SELECT 
            a.name,
            COUNT(DISTINCT al.genre) as genre_count,
            GROUP_CONCAT(DISTINCT al.genre) as genres
        FROM artists a
        JOIN albums al ON al.artist_id = a.id
        WHERE al.genre IS NOT NULL
        GROUP BY a.id, a.name
        HAVING genre_count > 1
        ORDER BY genre_count DESC
        LIMIT 10
    """
    )

    results = cursor.fetchall()
    if results:
        print(f"\n  {'Artist':<30} {'Genres':<10} {'Genre List'}")
        print("  " + "-" * 70)

        for row in results:
            artist, count, genres = row
            genre_list = genres[:35] if genres else ""
            print(f"  {artist:<30} {count:<10} {genre_list}")
    else:
        print("\n  No artists with multiple genres found.")


def get_sample_songs(cursor, limit=15):
    """Display a sample of songs with their details."""
    print_section("SAMPLE SONGS")

    cursor.execute(
        """
        SELECT 
            s.title,
            a.name as artist,
            al.title as album,
            al.year
        FROM songs s
        JOIN albums al ON s.album_id = al.id
        JOIN artists a ON al.artist_id = a.id
        ORDER BY RANDOM()
        LIMIT ?
    """,
        (limit,),
    )

    print(f"\n  {'Song':<35} {'Artist':<20} {'Album':<30}")
    print("  " + "-" * 85)

    for row in cursor.fetchall():
        song, artist, album, year = row
        print(f"  {song[:34]:<35} {artist[:19]:<20} {album[:29]:<30}")


def get_database_insights(cursor):
    """Display interesting insights about the database."""
    print_section("DATABASE INSIGHTS")

    # Average songs per album
    cursor.execute(
        """
        SELECT AVG(song_count) as avg_songs
        FROM (
            SELECT COUNT(s.id) as song_count
            FROM albums al
            JOIN songs s ON s.album_id = al.id
            GROUP BY al.id
        )
    """
    )
    avg_songs = cursor.fetchone()[0]
    print(f"\n  Average songs per album: {avg_songs:.2f}")

    # Average albums per artist
    cursor.execute(
        """
        SELECT AVG(album_count) as avg_albums
        FROM (
            SELECT COUNT(al.id) as album_count
            FROM artists a
            JOIN albums al ON al.artist_id = a.id
            GROUP BY a.id
        )
    """
    )
    avg_albums = cursor.fetchone()[0]
    print(f"  Average albums per artist: {avg_albums:.2f}")

    # Most common year
    cursor.execute(
        """
        SELECT year, COUNT(*) as count
        FROM albums
        WHERE year IS NOT NULL
        GROUP BY year
        ORDER BY count DESC
        LIMIT 1
    """
    )
    result = cursor.fetchone()
    if result:
        year, count = result
        print(f"  Most common release year: {year} ({count} albums)")

    # Most common genre
    cursor.execute(
        """
        SELECT genre, COUNT(*) as count
        FROM albums
        WHERE genre IS NOT NULL
        GROUP BY genre
        ORDER BY count DESC
        LIMIT 1
    """
    )
    result = cursor.fetchone()
    if result:
        genre, count = result
        print(f"  Most common genre: {genre} ({count} albums)")


def search_artist(cursor, artist_name):
    """Search for a specific artist and show their details."""
    print_section(f"SEARCH RESULTS FOR: {artist_name}")

    cursor.execute(
        """
        SELECT 
            a.name,
            COUNT(DISTINCT al.id) as album_count,
            COUNT(s.id) as song_count,
            MIN(al.year) as first_year,
            MAX(al.year) as last_year
        FROM artists a
        JOIN albums al ON al.artist_id = a.id
        JOIN songs s ON s.album_id = al.id
        WHERE a.name LIKE ?
        GROUP BY a.id, a.name
    """,
        (f"%{artist_name}%",),
    )

    results = cursor.fetchall()
    if results:
        for row in results:
            artist, albums, songs, first_year, last_year = row
            print(f"\n  Artist: {artist}")
            print(f"  Albums: {albums}")
            print(f"  Songs: {songs}")
            if first_year and last_year:
                print(f"  Active years: {first_year} - {last_year}")

        # Show albums
        print(f"\n  {'Album':<40} {'Year':<8} {'Genre':<20} {'Songs'}")
        print("  " + "-" * 75)

        cursor.execute(
            """
            SELECT 
                al.title,
                al.year,
                al.genre,
                COUNT(s.id) as song_count
            FROM artists a
            JOIN albums al ON al.artist_id = a.id
            JOIN songs s ON s.album_id = al.id
            WHERE a.name LIKE ?
            GROUP BY al.id, al.title, al.year, al.genre
            ORDER BY al.year DESC
        """,
            (f"%{artist_name}%",),
        )

        for row in cursor.fetchall():
            album, year, genre, songs = row
            year_str = str(year) if year else "N/A"
            genre_str = genre[:19] if genre else "N/A"
            print(f"  {album[:39]:<40} {year_str:<8} {genre_str:<20} {songs}")
    else:
        print(f"\n  No results found for '{artist_name}'")


def main():
    """Main function to run all analyses."""

    # Check if database exists
    if not os.path.exists(DATABASE_FILE):
        print("=" * 60)
        print("  ERROR: Database not found!")
        print("=" * 60)
        print(f"\n  Expected location: {DATABASE_FILE}")
        print(
            "\n  Please run 'python database_generator.py' first to create the database."
        )
        return

    # Connect to database
    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    print("\n" + "=" * 60)
    print("  MUSIC LIBRARY DATABASE EXPLORER")
    print("=" * 60)
    print(f"  Database: {DATABASE_FILE}")

    # Run all analyses
    get_basic_statistics(cursor)
    get_database_insights(cursor)
    get_top_artists(cursor, limit=10)
    get_genre_distribution(cursor)
    get_year_distribution(cursor)
    get_prolific_albums(cursor, limit=10)
    get_recent_albums(cursor, limit=10)
    get_artist_diversity(cursor)
    get_sample_songs(cursor, limit=15)

    # Optional: Search for specific artist
    # Uncomment the line below and replace with an artist name to search
    # search_artist(cursor, "Taylor Swift")

    print("\n" + "=" * 60)
    print("  ANALYSIS COMPLETE")
    print("=" * 60)
    print("\n  Tip: Edit this script to search for specific artists!")
    print("  Uncomment the search_artist() line and add your artist name.\n")

    # Close connection
    connection.close()


if __name__ == "__main__":
    main()
