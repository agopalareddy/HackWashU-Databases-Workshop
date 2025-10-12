# Copilot instructions for this repo

Purpose: small workshop repo with two independent parts:

- `database_generator.py`: builds a local SQLite music library and CSV exports by calling the iTunes Search API.
- `index.html`: a standalone Supabase-powered Todo demo (client-side only).

## Big picture and data flow

- Python script flow (see `main()`): requirements check → create `exports/` → delete old DB → connect SQLite → create tables → fetch iTunes data → insert artists/albums/songs → commit → export every table to CSV.
- Tables and relationships (foreign keys enabled):
  - `artists(id, name UNIQUE)`
  - `albums(id, title, artist_id -> artists.id, genre, release_year)`
  - `songs(id, title, album_id -> albums.id, created_at DEFAULT CURRENT_TIMESTAMP)`
- Deduping strategy: in-memory caches while processing (`artist_cache`, `album_cache`) prevent duplicate inserts; songs are bulk-inserted with `executemany` for speed.

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

- Requires Python 3.x and the `requests` package.

```pwsh
# from repo root
python -m pip install --upgrade pip
python -m pip install requests
python .\database_generator.py
```

Outputs appear in `exports/`:

- `music_library.sqlite` plus `artists.csv`, `albums.csv`, `songs.csv` exported via `SELECT *` (new columns auto-export).

## iTunes API usage

- Endpoint shape in `fetch_songs_from_itunes`: `https://itunes.apple.com/search?term=<artist>&entity=song&limit=50` with 10s timeout.
- Keys read: `artistName`, `collectionName` (album), `trackName` (song), `releaseDate`, `primaryGenreName`.
- Release year parsed from `releaseDate`; failures are ignored gracefully.

## Project-specific conventions

- All artifacts live under `exports/`; the DB file path is `exports/music_library.sqlite`.
- Fresh runs delete the old DB (`clean_old_database`) to ensure deterministic workshops.
- Foreign keys are explicitly enabled (`PRAGMA foreign_keys = ON;`). Keep this if you modify schema.
- Artist list to fetch is centralized in `ARTISTS_TO_FETCH`.

## Common modifications with examples

- Add/limit artists: edit `ARTISTS_TO_FETCH = [ ... ]` in `database_generator.py`.
- Change fetch size: tweak the `limit` query param in `fetch_songs_from_itunes` URL.
- Add new album/song fields: update `CREATE TABLE ...` DDL and the insert in `process_api_data`; CSV export does not need changes.

## Debugging tips

- Network issues: the script logs and skips on `requests` errors per-artist; re-run safely.
- Validate schema/data quickly: open `exports/music_library.sqlite` with a SQLite viewer or run a quick query using your preferred tool.
- If `exports/` is missing or empty, confirm the script created it and that `requests` is installed.

## Supabase demo (`index.html`)

- Pure client-side demo using `@supabase/supabase-js@2` via CDN. It expects a Supabase project with a `todos` table and RLS configured to user_id.
- Update `SUPABASE_URL`/`SUPABASE_ANON_KEY` as needed for your project; the anon key is expected to be embedded on the client.
- Open `index.html` directly or via a simple static server; no build step is required.

## Guardrails for agents

- Do not add server secrets to the repo. The Python script has no secrets; the Supabase anon key is public by design.
- Keep the workshop deterministic: avoid writing outside `exports/` and avoid mutating global state beyond `ARTISTS_TO_FETCH` and schema changes you intend.

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
| Empty CSVs or DB                                  | API returned no results or run failed early | Use the Quick SQLite checks above; confirm artists in `ARTISTS_TO_FETCH` and ensure the script completed (look for "Done!" log).                      |
| SQLite FK constraint errors                       | Foreign keys disabled in other tooling      | The script sets `PRAGMA foreign_keys = ON;`. If writing to the DB externally, enable FKs in your session too.                                         |
| `database is locked` on Windows                   | DB open in another app                      | Close viewers (VS Code SQL extensions, DB browsers) while the script writes, then retry.                                                              |
| Supabase: login works but no todos load           | RLS blocks SELECT                           | Add a SELECT policy on `todos`: `using (user_id = auth.uid())`. Then refresh to pull the user’s rows.                                                 |
| Supabase: insert fails with RLS error             | RLS blocks INSERT                           | Add an INSERT policy with a WITH CHECK: `with check (user_id = auth.uid())`. App inserts `user_id` from the session already.                          |
| Supabase: todos insert but show for all users     | Missing RLS                                 | Ensure RLS is enabled and at least the SELECT policy above exists.                                                                                    |
| Supabase: 401/invalid key                         | Wrong `SUPABASE_URL`/`SUPABASE_ANON_KEY`    | Replace constants in `index.html` with your project’s values from Supabase settings.                                                                  |
| Supabase: user_id null on insert                  | Missing session                             | Ensure the user is logged in (app uses `onAuthStateChange`); if testing manually, call `auth.getUser()` before insert and include `user_id: user.id`. |

## Maintenance

- Keep this file up to date as the project evolves. If schema, workflow order, API usage, or conventions change, update the relevant sections so future agents remain productive.
