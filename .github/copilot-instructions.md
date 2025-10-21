# Copilot instructions for this repo

Purpose: HackWashU Databases Workshop - beginner-friendly educational workshop with two independent projects:

1. **`database_generator.py`**: Python script that builds a SQLite music library and CSV exports by calling the iTunes Search API
2. **Todo App** (`index.html`, `app.js`, `styles.css`): Standalone Supabase-powered Todo app with authentication and RLS
3. **`explore_db.py`**: Database analysis tool with statistics and visualizations
4. **`WORKSHOP_GUIDE.md`**: Comprehensive step-by-step tutorial for workshop participants

## Project philosophy

- **Beginner-friendly**: Code is organized in clear sections with extensive comments
- **Educational**: Designed for learning database concepts, APIs, and web development
- **Self-contained**: Minimal dependencies (requests, csv, os, sqlite3 for Python; Supabase JS SDK via CDN)
- **Deterministic**: Workshops should produce consistent results

## Big picture and data flow

### Python Music Library (`database_generator.py`)

- Script flow (see `main()`): create `exports/` folder → connect SQLite → create tables → fetch iTunes data for each artist → deduplicate and insert artists/albums/songs → commit → export all tables to CSV
- Tables and relationships (foreign keys enabled):
  - `artists(id, name UNIQUE)`
  - `albums(id, title, artist_id -> artists.id, genre, release_year)`
  - `songs(id, title, album_id -> albums.id, created_at DEFAULT CURRENT_TIMESTAMP)`
- Deduplication strategy: in-memory dictionaries (`saved_artists`, `saved_albums`) map names to IDs, preventing duplicate inserts
- Uses Python's built-in `csv` module with proper formatting (no manual string concatenation)

## ER diagram (ASCII)

```
artists                               albums                               songs
-------                               ------                               -----
id   PK                               id   PK                              id   PK
name UNIQUE                           title                                 title
                                       artist_id FK -> artists.id            album_id FK -> albums.id
                                       genre                                 created_at DEFAULT CURRENT_TIMESTAMP
                                       release_year

artists 1 ────────────< albums 1 ────────────< songs
```

## How to run (Windows PowerShell)

### Part 1: Python Music Library

Requires Python 3.x and the `requests` package.

```pwsh
# From repo root
python -m pip install requests
python database_generator.py

# Explore the database
python explore_db.py
```

Outputs appear in `exports/`:

- `music_library.db` (SQLite database)
- `artists.csv`, `albums.csv`, `songs.csv` (exported via Python's csv module)

### Part 2: Supabase Todo App

Requires a Supabase account and project setup.

```pwsh
# Create .env file with your Supabase credentials (see WORKSHOP_GUIDE.md)
# Then start local server:
python -m http.server 8000
# Open http://localhost:8000/index.html
```

## iTunes API usage

- Endpoint shape in `fetch_songs_from_itunes`: `https://itunes.apple.com/search?term=<artist>&entity=song&limit=50` with 10s timeout.
- Keys read: `artistName`, `collectionName` (album), `trackName` (song), `releaseDate`, `primaryGenreName`.
- Release year parsed from `releaseDate`; failures are ignored gracefully.

## Project-specific conventions

- **All artifacts live under `exports/`**: DB file is `exports/music_library.db`, CSVs are `exports/*.csv`
- **Fresh runs preserve data**: The script does NOT delete old DB anymore - it connects to existing or creates new
- **Foreign keys explicitly enabled**: `PRAGMA foreign_keys = ON;` must remain for referential integrity
- **Artist list**: Centralized in `ARTISTS` constant at top of `database_generator.py`
- **Songs per artist**: Controlled by `SONGS_PER_ARTIST` constant (default: 50)
- **Folder auto-creation**: Script uses `os.makedirs(EXPORTS_FOLDER, exist_ok=True)`
- **CSV exports**: Use Python's `csv.writer()` with `newline=''` parameter for proper formatting

## Common modifications with examples

- Add/limit artists: edit `ARTISTS = [ ... ]` in `database_generator.py`.
- Change fetch size: tweak the `limit` query param in `fetch_songs_from_itunes` URL.
- Add new album/song fields: update `CREATE TABLE ...` DDL and the insert in `save_to_database`; CSV export does not need changes.

## Debugging tips

- Network issues: the script logs and skips on `requests` errors per-artist; re-run safely.
- Validate schema/data quickly: open `exports/music_library.db` with a SQLite viewer or run a quick query using your preferred tool.
- If `exports/` is missing or empty, confirm the script created it and that `requests` is installed.

## Supabase Todo App (`index.html`, `app.js`, `styles.css`)

- **Architecture**: Pure client-side app using `@supabase/supabase-js@2` via CDN
- **Configuration**: Uses `.env` file (recommended) or hardcoded values in `loadConfig()` function
- **Database**: Expects Supabase project with `todos` table:
  - Columns: `id`, `created_at`, `task`, `is_complete`, `user_id`
  - RLS enabled with policies for SELECT, INSERT, UPDATE, DELETE (all using `user_id = auth.uid()`)
- **Code organization** (`app.js` - 7 steps for beginners):
  1. Load Configuration (reads .env file)
  2. Initialize Supabase (creates client)
  3. Get HTML Elements (references to DOM)
  4. Helper Functions (`createTodoElement()` for UI)
  5. CRUD Operations (`fetchTodos`, `toggleTodoComplete`, `editTodo`, `deleteTodo`)
  6. Event Listeners (all grouped: auth buttons, add todo, delete all)
  7. Session Management (`onAuthStateChange` callback)
- **Security**: Anon key is public by design; RLS provides data isolation
- **Local server required**: Must use `python -m http.server` (can't open HTML file directly due to .env fetch)

## Guardrails for agents

- Do not add server secrets to the repo. The Python script has no secrets; the Supabase anon key is public by design.
- Keep the workshop deterministic: avoid writing outside `exports/` and avoid mutating global state beyond `ARTISTS` list and schema changes you intend.

## Quick SQLite sanity checks

- Using Python (works on Windows by default):

```pwsh
# Row counts per table
python -c "import sqlite3; c=sqlite3.connect('exports/music_library.sqlite').cursor();\
print('artists:', c.execute('select count(*) from artists').fetchone()[0]);\
print('albums:', c.execute('select count(*) from albums').fetchone()[0]);\
print('songs:', c.execute('select count(*) from songs').fetchone()[0])"

# Peek a few albums and songs
python -c "import sqlite3; c=sqlite3.connect('exports/music_library.sqlite').cursor();\
print('albums sample:', c.execute(\"select title, release_year from albums order by id desc limit 5\").fetchall());\
print('songs sample:', c.execute(\"select title from songs order by id desc limit 5\").fetchall())"
```

- If you have the SQLite CLI installed:

```pwsh
sqlite3 .\exports\music_library.sqlite "SELECT name FROM sqlite_master WHERE type='table';"
sqlite3 .\exports\music_library.sqlite "SELECT a.name, count(al.id) FROM artists a JOIN albums al ON al.artist_id=a.id GROUP BY a.id ORDER BY 2 DESC LIMIT 5;"
```

## Troubleshooting

| Symptom                                           | Likely cause                                | Fix                                                                                                                                                   |
| ------------------------------------------------- | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: No module named 'requests'` | Dependency missing                          | Install via `python -m pip install requests`, then rerun the script.                                                                                  |
| `⚠ Error fetching data for <artist>` and 0 songs  | Network hiccup or API rate limiting         | Re-run; optionally reduce the artist list or `limit` in `fetch_songs_from_itunes`. Network errors are per-artist and safe to retry.                   |
| Empty CSVs or DB                                  | API returned no results or run failed early | Use the Quick SQLite checks above; confirm artists in `ARTISTS` and ensure the script completed (look for "Done!" log).                               |
| SQLite FK constraint errors                       | Foreign keys disabled in other tooling      | The script sets `PRAGMA foreign_keys = ON;`. If writing to the DB externally, enable FKs in your session too.                                         |
| `database is locked` on Windows                   | DB open in another app                      | Close viewers (VS Code SQL extensions, DB browsers) while the script writes, then retry.                                                              |
| Supabase: login works but no todos load           | RLS blocks SELECT                           | Add a SELECT policy on `todos`: `using (user_id = auth.uid())`. Then refresh to pull the user’s rows.                                                 |
| Supabase: insert fails with RLS error             | RLS blocks INSERT                           | Add an INSERT policy with a WITH CHECK: `with check (user_id = auth.uid())`. App inserts `user_id` from the session already.                          |
| Supabase: todos insert but show for all users     | Missing RLS                                 | Ensure RLS is enabled and at least the SELECT policy above exists.                                                                                    |
| Supabase: 401/invalid key                         | Wrong `SUPABASE_URL`/`SUPABASE_ANON_KEY`    | Check `.env` file values or update `loadConfig()` function in `app.js` with correct values from Supabase settings.                                    |
| `.env` file not loading                           | Not using local server or wrong path        | Must use `python -m http.server 8000` (can't open HTML directly). Ensure `.env` is in project root, same folder as `index.html`.                      |
| `.env` file format errors                         | Extra quotes, spaces, or wrong filename     | Format should be `KEY=value` (no spaces, no quotes). File must be named `.env` not `.env.txt`.                                                        |
| Supabase: user_id null on insert                  | Missing session                             | Ensure the user is logged in (app uses `onAuthStateChange`); if testing manually, call `auth.getUser()` before insert and include `user_id: user.id`. |

## Database Explorer (`explore_db.py`)

- Comprehensive analysis tool for the music library database
- Functions:
  - `get_basic_statistics()` - counts for all tables
  - `get_top_artists()` - ranked by album/song count
  - `get_genre_distribution()` - albums per genre
  - `get_year_distribution()` - albums by release year with bar charts
  - `get_prolific_albums()` - albums with most songs
  - `get_recent_albums()` - newest releases
  - `get_artist_diversity()` - genre variety per artist
  - `get_database_insights()` - averages and common values
  - `search_artist()` - detailed artist lookup
- Bar charts use `#` character (Windows-compatible, not █)
- Designed to demonstrate SQL queries for workshop participants

## Workshop Guide (`WORKSHOP_GUIDE.md`)

- **Purpose**: Complete step-by-step tutorial for workshop attendees
- **Structure**:
  - Workshop Setup (prerequisites, installation)
  - Part 1: Python Music Library (6 steps)
  - Part 2: Supabase Todo App (10 steps)
  - Challenge Exercises (7 advanced tasks)
  - Troubleshooting (comprehensive solutions)
  - Discussion Questions & Answers (9 detailed Q&As)
- **Teaching approach**: "Reverse book club" format - participants work through independently
- **Code walkthroughs**: Explains every function, decision, and pattern
- **Links**: All discussion questions link to detailed answers at the end
- **Best practices**: Emphasizes .env files over hardcoding, built-in modules over manual implementations

## File organization

```
├── .github/
│   └── copilot-instructions.md    # This file
├── exports/                       # Generated by database_generator.py
│   ├── music_library.db
│   ├── artists.csv
│   ├── albums.csv
│   └── songs.csv
├── database_generator.py          # Part 1: Music library builder (~300 lines, 7 sections)
├── explore_db.py                  # Database analysis tool (~380 lines)
├── index.html                     # Part 2: Todo app HTML structure
├── app.js                         # Todo app logic (7-step organization, ~366 lines)
├── styles.css                     # Todo app styles
├── .env                           # (not committed) Supabase credentials
├── WORKSHOP_GUIDE.md              # Step-by-step tutorial
├── README.md                      # Project overview with links
└── LICENSE                        # MIT License
```

## Code style for beginners

- **Clear sections**: Each file divided into numbered steps with header comments
- **Extensive documentation**: Every function has docstrings or comment blocks explaining purpose
- **Consistent naming**: `snake_case` for Python, `camelCase` for JavaScript
- **Error handling**: Graceful failures with helpful messages
- **No magic numbers**: Constants defined at top of files
- **DRY principle**: Helper functions to reduce duplication (e.g., `createTodoElement()`)
- **Logical grouping**: Related code together (all event listeners in Step 6)

## Maintenance

- Keep this file up to date as the project evolves. If schema, workflow order, API usage, or conventions change, update the relevant sections so future agents remain productive.
- When updating code, ensure `WORKSHOP_GUIDE.md` stays in sync with actual implementation
- Test both projects after major changes to ensure workshop participants won't encounter errors
