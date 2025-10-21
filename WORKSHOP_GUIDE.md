# HackWashU Databases Workshop - Step-by-Step Guide

**Welcome!** This guide will walk you through building two complete database projects from scratch. Work through each section at your own pace, and don't hesitate to ask questions!

---

## Table of Contents

- [Workshop Setup](#workshop-setup)
- [Part 1: Python Music Library Database](#part-1-python-music-library-database)
- [Part 2: Supabase Todo Web App](#part-2-supabase-todo-web-app)
- [Challenge Exercises](#challenge-exercises)
- [Troubleshooting](#troubleshooting)
- [Discussion Questions & Answers](#discussion-questions--answers)

---

## Workshop Setup

### Prerequisites Check

Before we begin, let's make sure you have everything installed:

**Step 1:** Check Python Installation

```pwsh
python --version
```

You should see Python 3.x. If not, download from [python.org](https://python.org).

**Step 2:** Clone or download this repository

```pwsh
git clone https://github.com/agopalareddy/HackWashU-Databases-Workshop.git
cd HackWashU-Databases-Workshop
```

**Step 3:** Install the required package

```pwsh
python -m pip install requests
```

**Checkpoint:** If all commands ran successfully, you're ready to go!

> **Note:** This script uses the `requests` package for API calls, plus built-in Python modules (`csv`, `os`, `sqlite3`).

---

## Part 1: Python Music Library Database

### Learning Goals

- Understand relational database design (tables, foreign keys, relationships)
- Learn to fetch data from public APIs
- Practice data deduplication and bulk inserts
- Export database tables to CSV files
- Use Python's built-in modules for file and data handling

### Architecture Overview

We'll build a music library with three related tables:

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  ARTISTS    │       │   ALBUMS    │       │    SONGS    │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │◄──┐   │ id (PK)     │◄──┐   │ id (PK)     │
│ name        │   │   │ title       │   │   │ title       │
└─────────────┘   │   │ artist_id   │   │   │ album_id    │
                  └───│ genre       │   └───│ created_at  │
                      │ release_year│       └─────────────┘
                      └─────────────┘
```

### Step 1: Explore the Database Generator Code

**Action:** Open `database_generator.py` in your editor.

The script is organized into clear sections with lots of comments! Here's what to look for:

**Configuration Section (Top of file)**
- `ARTISTS` - List of artists to search for
- `SONGS_PER_ARTIST` - How many songs per artist (default: 50)
- `EXPORTS_FOLDER` - Folder for all output files
- `DATABASE_FILE` - Path to the database file

**Step 1: `create_tables()` function**
- Creates three tables: artists, albums, songs
- Uses `FOREIGN KEY` to link tables together
- `PRAGMA foreign_keys = ON;` enables referential integrity

**Step 2: `fetch_songs_from_itunes()` function**
- Builds a URL to search iTunes API
- Returns a list of song data
- Handles errors gracefully with try/except

**Step 3: `save_to_database()` function**
- Uses dictionaries (`saved_artists`, `saved_albums`) to avoid duplicates
- Parses the year from date strings
- Uses `INSERT OR IGNORE` to handle duplicates
- Inserts data into all three tables

**Step 4: `export_to_csv()` function**
- Reads data from database tables
- Uses Python's `csv` module for proper formatting
- Exports to CSV files in the exports folder

**Main Program: `main()` function**
- Creates exports folder if needed
- Connects to database
- Runs all steps in sequence
- Provides progress feedback

💡 **Discussion Question:** Why do we use dictionaries to track saved artists and albums? [See answer →](#q1-why-dictionaries-for-deduplication)

### Step 2: Customize Your Music Library

**Action:** Modify the artist list in `database_generator.py`.

Find this section at the top of the file:

```python
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
```

**Your turn:**

1. Add or replace artists with your favorites
2. Adjust `SONGS_PER_ARTIST` if you want more or fewer songs (1-200)
3. Save the file

**Pro tip:** Start with 3-5 artists and 20-30 songs for faster testing!

### Step 3: Run the Database Generator

**Action:** Execute the script and watch the magic happen!

```pwsh
python database_generator.py
```

**What you should see:**

```
==================================================
MUSIC LIBRARY DATABASE GENERATOR
==================================================
Created 'exports' folder
Connected to database: exports\music_library.db

Creating database tables...
Tables created!

Searching iTunes for 'Sabrina Carpenter'...
   Found 50 songs!

Searching iTunes for 'Gracie Abrams'...
   Found 50 songs!

... (continues for each artist)

Total songs collected: 546

Saving to database...
Saved 48 artists, 208 albums, 546 songs!

Exporting to CSV files...
   Exported 48 rows to exports\artists.csv
   Exported 208 rows to exports\albums.csv
   Exported 546 rows to exports\songs.csv

==================================================
ALL DONE!
==================================================
Check the 'exports' folder for these files:
  • music_library.db (SQLite database)
  • artists.csv
  • albums.csv
  • songs.csv
```

**Checkpoint:** Verify you have an `exports/` folder with these files:

- `music_library.db` (the database)
- `artists.csv`
- `albums.csv`
- `songs.csv`

### Step 4: Explore Your Database

**Option A: Using Python (Quick Stats)**

Create a new file called `explore_db.py`:

```python
import sqlite3

# Connect to the database
connection = sqlite3.connect('exports/music_library.db')
cursor = connection.cursor()

print("=" * 50)
print("DATABASE STATISTICS")
print("=" * 50)

# Count records in each table
for table in ['artists', 'albums', 'songs']:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f"{table.upper()}: {count} records")

print("\n" + "=" * 50)
print("TOP ARTISTS (by album count)")
print("=" * 50)

cursor.execute('''
    SELECT a.name, COUNT(al.id) as album_count
    FROM artists a
    JOIN albums al ON al.artist_id = a.id
    GROUP BY a.id
    ORDER BY album_count DESC
''')

for row in cursor.fetchall():
    print(f"{row[0]}: {row[1]} albums")

connection.close()
```

Run it:

```pwsh
python explore_db.py
```

**Option B: Using SQLite Browser (Visual Tool)**

- Download [DB Browser for SQLite](https://sqlitebrowser.org/)
- Open `exports/music_library.db`
- Click "Browse Data" to see your tables
- Click "Execute SQL" to run custom queries

**Option C: Using VS Code Extension**

- Install "SQLite Viewer" extension in VS Code
- Click on `exports/music_library.db` file to open it
- Explore tables visually

### Step 5: Practice SQL Queries

Try these queries in your SQL tool:

**Query 1:** Find all songs by a specific artist
```sql
SELECT s.title, al.title as album, a.name as artist
FROM songs s
JOIN albums al ON s.album_id = al.id
JOIN artists a ON al.artist_id = a.id
WHERE a.name = 'Queen'
ORDER BY al.release_year;
```

**Query 2:** Find albums from a specific year
```sql
SELECT al.title, a.name, al.genre
FROM albums al
JOIN artists a ON al.artist_id = a.id
WHERE al.year = 2024;
```

**Query 3:** Count songs per genre
```sql
SELECT al.genre, COUNT(s.id) as song_count
FROM songs s
JOIN albums al ON s.album_id = al.id
GROUP BY al.genre
ORDER BY song_count DESC;
```

💡 **Discussion Questions:**
- How would you add a `duration` column to store song length? [See answer →](#q2-adding-duration-column)
- What if you wanted to track which songs are your favorites? [See answer →](#q3-tracking-favorite-songs)
- How could you add song lyrics to the database? [See answer →](#q4-adding-song-lyrics)

### Step 6: Open and Examine CSV Exports

**Action:** Open the CSV files in Excel, Google Sheets, or a text editor.

**Questions to explore:**
- How is the data structured in each CSV?
- Can you identify the foreign key relationships?
- What happens if you open `songs.csv` - do you see artist names directly?

**Why CSVs matter:**
- Easy to import into spreadsheets for analysis
- Can be used with data visualization tools (Tableau, Power BI)
- Simple backup format
- Can be imported into other databases

---

## Part 2: Supabase Todo Web App

### Learning Goals

- Set up a cloud database (Supabase)
- Implement user authentication
- Understand Row Level Security (RLS)
- Build a full CRUD application (Create, Read, Update, Delete)
- Deploy a client-side web app

### What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- PostgreSQL database (more powerful than SQLite)
- Built-in authentication (email/password, OAuth, etc.)
- Row Level Security (RLS) for data privacy
- Instant APIs
- Real-time subscriptions

### Step 1: Create a Supabase Account and Project

**Action:** Set up your free Supabase project

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project" → Sign up (use GitHub or email)
3. Click "New Project"
   - **Organization:** Create or select one
   - **Name:** `hackwashu-todo-app`
   - **Database Password:** Generate a strong password (save it!)
   - **Region:** Choose closest to you
   - **Pricing Plan:** Free
4. Click "Create new project" (takes ~2 minutes)

**Checkpoint:** Your project dashboard should load with a green "Active" status.

### Step 2: Create the Todos Table

**Action:** Set up your database schema

1. In your Supabase project, click **"Table Editor"** in the left sidebar
2. Click **"Create a new table"**
3. Configure the table:
   - **Name:** `todos`
   - **Description:** "User todo items"
   - Click **"Add Column"** for each field:

| Column Name | Type          | Default Value         | Primary | Nullable | Unique |
|-------------|---------------|-----------------------|---------|----------|--------|
| id          | int8          | auto-increment        | Yes     | No       | Yes    |
| created_at  | timestamptz   | now()                 | No      | No       | No     |
| task        | text          | (none)                | No      | No       | No     |
| is_complete | bool          | false                 | No      | No       | No     |
| user_id     | uuid          | (none)                | No      | No       | No     |

4. Click **"Save"**

**Checkpoint:** You should see your `todos` table in the Table Editor.

### Step 3: Enable Row Level Security (RLS)

**Why RLS?** Without RLS, any user could see everyone else's todos. RLS ensures users can only access their own data.

**Action:** Set up security policies

1. In Table Editor, click on your `todos` table
2. Click the **"RLS"** badge or go to **Authentication → Policies**
3. Find your `todos` table and click **"Enable RLS"**
4. Click **"New Policy"**

**Policy 1: SELECT (Read own todos)**
```sql
Name: Users can view their own todos
Allowed operation: SELECT
Target roles: authenticated
WITH CHECK expression: (user_id = auth.uid())
```

**Policy 2: INSERT (Create todos)**
```sql
Name: Users can create todos
Allowed operation: INSERT
Target roles: authenticated
WITH CHECK expression: (user_id = auth.uid())
```

**Policy 3: UPDATE (Edit own todos)**
```sql
Name: Users can update their own todos
Allowed operation: UPDATE
Target roles: authenticated
USING expression: (user_id = auth.uid())
WITH CHECK expression: (user_id = auth.uid())
```

**Policy 4: DELETE (Remove own todos)**
```sql
Name: Users can delete their own todos
Allowed operation: DELETE
Target roles: authenticated
USING expression: (user_id = auth.uid())
```

5. Click **"Review"** then **"Save policy"** for each

💡 **Discussion Question:** What happens if you try to query todos without being logged in? [See answer →](#q5-rls-without-authentication)

### Step 4: Get Your Supabase Credentials

**Action:** Find your project's API keys

1. Click **"Settings"** (gear icon) in the left sidebar
2. Click **"API"** under Project Settings
3. Find these two values:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **anon public** key (under "Project API keys")

**Important:** Keep these handy for the next step!

### Step 5: Configure the Web App

**Action:** Add your credentials to the app

**Option A: Using a .env file (recommended)**

Create a `.env` file in the project root:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

Replace the values with your actual Supabase credentials:
```
SUPABASE_URL=https://abcdefghij.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Why .env?**
- Keeps credentials separate from code
- Easy to change without editing JavaScript
- Better security practice
- Won't accidentally commit keys to Git

**Option B: Hardcode in app.js (fallback for troubleshooting)**

If the .env file doesn't work:

1. Open `app.js` and find the `loadConfig()` function (around line 18)
2. Replace the entire function with:

```javascript
async function loadConfig() {
  return {
    SUPABASE_URL: 'https://your-project.supabase.co', // Replace this!
    SUPABASE_ANON_KEY: 'your-anon-key-here' // Replace this!
  };
}
```

3. Replace with your actual values and save

### Step 6: Run the Web App Locally

**Action:** Start a local web server

```pwsh
python -m http.server 8000
```

You should see:
```
Serving HTTP on :: port 8000 (http://[::]:8000/) ...
```

**Open your browser:** Go to [http://localhost:8000/index.html](http://localhost:8000/index.html)

**Checkpoint:** You should see the "Supabase Secure Todo App" with a sign-up form.

### Step 7: Test User Authentication

**Action:** Create your first user account

1. Enter an email (can be fake for testing: `test@example.com`)
2. Enter a password (minimum 6 characters)
3. Click **"Sign Up"**

**What happens:**
- Supabase creates a new user account
- You're automatically logged in
- The app shows your email in the welcome bar
- The todo input form appears

**Try logging out and back in:**
1. Click **"Log Out"**
2. Enter the same email/password
3. Click **"Log In"**

💡 **Discussion Question:** Where is your password stored? [See answer →](#q6-password-storage)

### Step 8: Test CRUD Operations

**Action:** Put the app through its paces!

**Create:**
1. Type "Buy groceries" in the input field
2. Click **"➕ Add Task"**
3. Your todo appears in the Active Tasks section

**Read:**
- Refresh the page - your todos should still be there (data persists!)
- Open the app in an incognito window and log in with a *different* email
- Verify you can't see the first user's todos (RLS works!)

**Update:**
1. Click the checkbox next to a todo to mark it complete
2. It moves to the "Completed Tasks" section
3. Click again to mark it incomplete

**Delete:**
1. Hover over a todo
2. Click the **"🗑️"** button
3. Confirm deletion

### Step 9: Explore the Code

**Action:** Open `app.js` and understand how it's organized

**Code Structure** (6 clear steps):

**Step 1: Load Configuration** (~line 18)
- `loadConfig()` - Reads credentials from `.env` file
- Parses key=value pairs

**Step 2: Initialize Supabase** (~line 39)
- Loads config and creates Supabase client
- This client handles all database and auth operations

**Step 3: Get HTML Elements** (~line 49)
- Gets references to page elements (forms, lists, buttons)
- Avoids repeated `document.getElementById()` calls

**Step 4: Helper Functions** (~line 59)
- `createTodoElement()` - Builds HTML for each todo item
- Handles checkbox, text, edit/delete buttons
- Reduces code duplication

**Step 5: TODO CRUD Operations** (~line 109)
- `fetchTodos()` - Reads all todos and displays them
- `toggleTodoComplete()` - Marks todos complete/incomplete
- `editTodo()` - Updates todo text
- `deleteTodo()` - Removes a single todo

**Step 6: Event Listeners** (~line 187)
- Sign up, login, logout button handlers
- Add todo button
- Delete all tasks button
- All event handlers are grouped together for easy reference

**Step 7: Session Management** (~line 292)
- `onAuthStateChange()` - Detects login/logout
- Shows/hides appropriate UI sections
- Loads todos when user logs in

**Key Database Operations:**

```javascript
// Create a new todo
await supabaseClient.from('todos').insert({
  task: task,
  user_id: user.id,
  is_complete: false
});

// Read todos (RLS filters by user automatically)
await supabaseClient.from('todos').select('*');

// Update a todo
await supabaseClient.from('todos')
  .update({ is_complete: !isComplete })
  .eq('id', todoId);

// Delete a todo
await supabaseClient.from('todos')
  .delete()
  .eq('id', todoId);
```

💡 **Discussion Questions:** 
- Why do we include `user_id` in the insert? What would happen if we didn't? [See answer →](#q7-why-user_id-in-inserts)
- Why is `createTodoElement()` defined before `fetchTodos()` uses it? [See answer →](#q8-function-definition-order)
- Why are all event listeners grouped together in Step 6? [See answer →](#q9-event-listener-organization)

### Step 10: Verify Data in Supabase Dashboard

**Action:** See your todos in the cloud!

1. Go back to your Supabase project dashboard
2. Click **"Table Editor"**
3. Select the `todos` table
4. You should see all the todos you created!

**Try this:**
- Note the `user_id` column - it's a unique identifier for each user
- Create a todo in the app, then refresh the Table Editor to see it appear
- Try manually editing a todo in the dashboard

---

## Challenge Exercises

### Music Database Challenges

**Challenge 1: Add a new field**
Add a `duration` column to the songs table (in seconds).
- Modify `create_database_tables()` function
- Re-run the script
- Bonus: Parse duration from iTunes API response

**Challenge 2: Advanced queries**
Write SQL queries to find:
- The artist with the most songs
- All albums from the 2000s
- Songs that appear in multiple albums (if any)

**Challenge 3: Add another table**
Create a `playlists` table that links to songs (many-to-many relationship).
- Think about the schema design
- You'll need a junction table!

### Todo App Challenges

**Challenge 4: Add priority levels**
- Add a `priority` column to the todos table (low/medium/high)
- Update the UI to show priority with colors
- Sort todos by priority

**Challenge 5: Add due dates**
- Add a `due_date` column (type: date)
- Show overdue tasks in red
- Sort by due date

**Challenge 6: Add categories/tags**
- Think about the schema: should tags be a column or separate table?
- Implement tag filtering in the UI
- Consider many-to-many relationships

**Challenge 7: Real-time updates**
Use Supabase's real-time features so changes appear instantly across devices:
```javascript
supabase
    .channel('todos')
    .on('postgres_changes', { event: '*', schema: 'public', table: 'todos' }, 
        payload => { loadTodos(); })
    .subscribe();
```

---

## Troubleshooting

### Python Script Issues

**Problem:** `ModuleNotFoundError: No module named 'requests'`

**Solution:**

```pwsh
python -m pip install requests
```

**Problem:** `⚠️ Error: ...` when fetching songs

**Possible causes:**
- No internet connection
- iTunes API is down or rate limiting
- Artist name not found

**Solutions:**
- Check your internet connection
- Reduce number of artists in the `ARTISTS` list
- Try different artist names
- Change `SONGS_PER_ARTIST` to a lower number (like 10)

**Problem:** Empty CSVs or very few songs

**Solution:**

```pwsh
# Check if data was saved:
python -c "import sqlite3; c=sqlite3.connect('exports/music_library.db').cursor(); print('Songs:', c.execute('select count(*) from songs').fetchone()[0])"
```

If you see 0 songs, the API fetch failed - check your artist names and internet connection.

**Problem:** `database is locked`

**Solution:** Close any programs that have the database open (SQLite Browser, VS Code extensions, etc.) and run the script again.

**Problem:** `exports` folder not created

**Solution:** The script should create it automatically. If not, create it manually:

```pwsh
mkdir exports
```

### Supabase Todo App Issues

**Problem:** App shows "Failed to fetch" or doesn't load

**Solutions to check:**
1. Is your `.env` file in the project root (same folder as `index.html`)?
2. Are your `SUPABASE_URL` and `SUPABASE_ANON_KEY` correct in `.env`?
3. Are you running a local server? (can't open HTML file directly - must use `python -m http.server`)
4. Check browser console (F12 → Console) for specific error messages
5. Try the hardcoded fallback option (see Step 5, Option B)

**Common .env mistakes:**
- Extra quotes around values (should be: `SUPABASE_URL=https://...` not `"https://..."`)
- Spaces around the `=` sign (wrong: `KEY = value`, correct: `KEY=value`)
- File named `.env.txt` instead of just `.env`
- .env file in wrong folder (must be in project root)

**Problem:** Sign up works but can't see todos / RLS error
```sql
-- Solution: Verify RLS policies in Supabase dashboard
-- Go to Authentication → Policies → todos table
-- Make sure you have SELECT, INSERT, UPDATE, DELETE policies
-- All should use: user_id = auth.uid()
```

**Problem:** Todos visible to all users (no privacy)
```sql
-- Solution: RLS is not enabled!
-- Go to Table Editor → todos table → Enable RLS
-- Then add the policies from Step 3
```

**Problem:** Can create todos but they have null user_id
```javascript
// Solution: Check your insert code includes user_id:
const { data, error } = await supabase
    .from('todos')
    .insert([{ task: todoText, user_id: user.id }]) // ← Make sure user_id is here
    .select();
```

**Problem:** Todos don't persist after refresh
```javascript
// Solution: Check if loadTodos() is called on page load
// Look for: onAuthStateChange callback in app.js
```

### General Debugging Tips

1. **Check browser console** (F12 → Console tab) for JavaScript errors
2. **Check Supabase logs** (Dashboard → Logs) for API errors
3. **Test in incognito mode** to rule out cache issues
4. **Use console.log()** liberally to debug JavaScript
5. **Verify your data** in Supabase Table Editor

---

## Discussion Questions & Answers

Here are detailed answers to all the discussion questions throughout the workshop:

### Part 1: Python Music Library

#### Q1: Why dictionaries for deduplication?

**Question:** Why do we use dictionaries to track saved artists and albums?

**Answer:** 
Dictionaries (`saved_artists` and `saved_albums`) serve as in-memory caches to prevent duplicate database inserts. Here's why this approach is efficient:

1. **Fast Lookups:** Dictionary lookups are O(1) - checking if an artist already exists is instant
2. **ID Mapping:** We store `{artist_name: artist_id}` so we can quickly get the ID when creating albums
3. **Reduces Database Queries:** Without caching, we'd need to query the database every time to check if an artist exists
4. **Works with API Data:** The iTunes API can return the same artist/album multiple times across different songs

**Example:**
```python
saved_artists = {}  # Will store {"Queen": 1, "The Beatles": 2, ...}

if artist_name not in saved_artists:
    # Insert new artist
    cursor.execute('INSERT INTO artists (name) VALUES (?)', (artist_name,))
    saved_artists[artist_name] = cursor.lastrowid

# Now we can use: artist_id = saved_artists[artist_name]
```

#### Q2: Adding duration column

**Question:** How would you add a `duration` column to store song length?

**Answer:**

**Step 1:** Modify the table creation in `create_tables()`:
```python
cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        album_id INTEGER NOT NULL,
        duration INTEGER,  -- Duration in seconds
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (album_id) REFERENCES albums(id)
    )
''')
```

**Step 2:** Parse duration from iTunes API response:
```python
def save_to_database(cursor, songs_data):
    # Inside the song loop:
    duration_ms = song.get('trackTimeMillis', 0)  # iTunes returns milliseconds
    duration_seconds = duration_ms // 1000  # Convert to seconds
    
    cursor.execute('''
        INSERT INTO songs (title, album_id, duration) 
        VALUES (?, ?, ?)
    ''', (song_title, album_id, duration_seconds))
```

**Step 3:** Query songs by duration:
```sql
-- Find songs longer than 5 minutes
SELECT title, duration/60.0 as minutes 
FROM songs 
WHERE duration > 300 
ORDER BY duration DESC;
```

#### Q3: Tracking favorite songs

**Question:** What if you wanted to track which songs are your favorites?

**Answer:**

There are two approaches depending on complexity needs:

**Approach 1: Simple Boolean Column**
```python
# Add to songs table:
CREATE TABLE songs (
    -- existing columns...
    is_favorite BOOLEAN DEFAULT 0
);

# Query favorites:
SELECT * FROM songs WHERE is_favorite = 1;
```

**Approach 2: Separate Favorites Table (Better for multi-user)**
```python
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,  -- If you have users
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    UNIQUE(song_id, user_id)  -- Prevent duplicate favorites
);

# Query a user's favorites:
SELECT s.title, a.name as artist
FROM favorites f
JOIN songs s ON f.song_id = s.id
JOIN albums al ON s.album_id = al.id
JOIN artists a ON al.artist_id = a.id
WHERE f.user_id = 1;
```

Approach 2 is better because:
- Supports multiple users
- Tracks when favorites were added
- Easier to implement "unfavorite" (just delete row)
- Can add ratings, play counts, etc. later

#### Q4: Adding song lyrics

**Question:** How could you add song lyrics to the database?

**Answer:**

**Option 1: Simple TEXT Column**
```python
CREATE TABLE songs (
    -- existing columns...
    lyrics TEXT  -- Can store large text
);
```

**Option 2: Separate Lyrics Table (Recommended)**
```python
CREATE TABLE lyrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER UNIQUE NOT NULL,  -- One-to-one relationship
    lyrics_text TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    is_explicit BOOLEAN DEFAULT 0,
    source TEXT,  -- Where lyrics came from
    FOREIGN KEY (song_id) REFERENCES songs(id)
);
```

**Why separate table?**
- Lyrics can be very large (100KB+)
- Not all songs need lyrics
- Faster queries when you don't need lyrics
- Can support multiple language versions:

```python
CREATE TABLE lyrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id INTEGER NOT NULL,  -- Changed from UNIQUE
    language TEXT NOT NULL,
    lyrics_text TEXT NOT NULL,
    FOREIGN KEY (song_id) REFERENCES songs(id),
    UNIQUE(song_id, language)  -- One lyrics per language
);
```

**Getting lyrics from APIs:**
- Genius API: `https://genius.com/api-clients`
- Musixmatch API: `https://developer.musixmatch.com/`
- LyricsOVH: `https://lyricsovh.docs.apiary.io/`

### Part 2: Supabase Todo App

#### Q5: RLS without authentication

**Question:** What happens if you try to query todos without being logged in?

**Answer:**

With Row Level Security (RLS) enabled and policies requiring `auth.uid()`:

1. **The query returns an empty array** `[]` - even if todos exist
2. **No error is thrown** - this is by design for security
3. **The user can't tell if todos exist** - prevents information leakage

**Example:**
```javascript
// User not logged in
const { data, error } = await supabase.from('todos').select('*');
// data = []  (empty array)
// error = null

// If RLS wasn't enabled:
// data = [all todos from all users]  (security breach!)
```

**Why this matters:**
- **Security:** Prevents unauthorized access to private data
- **Privacy:** Users can't probe for existence of others' data
- **Automatic filtering:** Your code doesn't need to filter by user - RLS does it

**Testing RLS:**
```sql
-- In Supabase SQL Editor, test without auth:
SET request.jwt.claims TO '{}';
SELECT * FROM todos;  -- Returns nothing

-- Test with fake user:
SET request.jwt.claims TO '{"sub": "fake-user-id"}';
SELECT * FROM todos;  -- Returns only that user's todos
```

#### Q6: Password storage

**Question:** Where is your password stored?

**Answer:**

Your password is **never stored in plain text**. Here's the security flow:

1. **Client Side (Browser):**
   - You type: `myPassword123`
   - Sent over HTTPS (encrypted in transit)
   - Never stored in localStorage or cookies

2. **Supabase Server:**
   - Receives password
   - Hashes using **bcrypt** algorithm with salt
   - Stores only the hash: `$2a$10$N9qo8uLOickgx2ZMRZoMye...`
   - Original password discarded

3. **Login Verification:**
   - You enter password again
   - Server hashes it the same way
   - Compares hashes (not passwords)
   - If match → generates JWT token

**Important concepts:**

- **Hash:** One-way function, can't reverse to get password
- **Salt:** Random data added to prevent rainbow table attacks
- **JWT Token:** What's stored in your browser for authentication
  ```javascript
  // After login, this is stored:
  localStorage.getItem('supabase.auth.token')
  // Contains: {access_token: 'eyJ...', refresh_token: 'xyz...'}
  ```

**Even Supabase staff can't see your password!** They only see:
```sql
SELECT email, encrypted_password FROM auth.users;
-- encrypted_password: $2a$10$abcd1234...
```

#### Q7: Why user_id in inserts?

**Question:** Why do we include `user_id` in the insert? What would happen if we didn't?

**Answer:**

**Including `user_id` is critical** for RLS policies to work. Here's what happens:

**With `user_id`:**
```javascript
// Correct ✓
await supabase.from('todos').insert({
  task: 'Buy milk',
  user_id: user.id,  // Links todo to current user
  is_complete: false
});
// RLS policy: WITH CHECK (user_id = auth.uid()) → PASSES ✓
```

**Without `user_id`:**
```javascript
// Incorrect ✗
await supabase.from('todos').insert({
  task: 'Buy milk',
  // user_id missing!
  is_complete: false
});
// RLS policy: WITH CHECK (user_id = auth.uid())
// Compares: null = 'real-user-id' → FAILS ✗
// Error: "new row violates row-level security policy"
```

**What happens:**
1. **INSERT fails** with RLS error
2. **Todo not created** in database
3. **Error message:** `"new row violates row-level security policy for table 'todos'"`

**Why we need it:**
- Links todos to owners
- RLS uses it to filter queries
- Prevents orphaned todos
- Enables multi-user application

**Pro tip:** You could make `user_id` auto-fill with a trigger:
```sql
CREATE TRIGGER set_user_id
BEFORE INSERT ON todos
FOR EACH ROW
EXECUTE FUNCTION set_current_user_id();

-- Function:
CREATE FUNCTION set_current_user_id()
RETURNS TRIGGER AS $$
BEGIN
  NEW.user_id := auth.uid();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

#### Q8: Function definition order

**Question:** Why is `createTodoElement()` defined before `fetchTodos()` uses it?

**Answer:**

This relates to **JavaScript hoisting** and code organization best practices:

**The Issue:**
```javascript
// This WORKS (function declaration):
fetchTodos();  // Can call before definition

function fetchTodos() {
  createTodoElement(todo, false);
}

function createTodoElement(todo, isCompleted) {
  // ...
}
```

```javascript
// This FAILS (const arrow function):
fetchTodos();  // ReferenceError: Cannot access before initialization

const fetchTodos = () => {
  createTodoElement(todo, false);  // ReferenceError!
};

const createTodoElement = (todo, isCompleted) => {
  // ...
};
```

**Why our code works:**
```javascript
// Step 4: Define helper first
const createTodoElement = (todo, isCompleted) => {
  // ...
};

// Step 5: Use helper (defined above)
const fetchTodos = async () => {
  const todoElement = createTodoElement(todo, false);  // ✓ Works!
};
```

**Best practices:**
1. **Define helpers before use** - clear dependency flow
2. **Group by purpose** - helpers, CRUD, events
3. **Top-to-bottom reading** - easier for beginners
4. **Avoid circular dependencies** - A calls B, B calls C (not back to A)

**Alternative with function declarations:**
```javascript
// These can be in any order (hoisted):
function fetchTodos() {
  createTodoElement(todo, false);
}

function createTodoElement(todo, isCompleted) {
  // ...
}
```

We use arrow functions for consistency and because they're more common in modern JavaScript tutorials.

#### Q9: Event listener organization

**Question:** Why are all event listeners grouped together in Step 6?

**Answer:**

**Grouping event listeners** is an organizational pattern that helps with:

**1. Mental Model Clarity**
```javascript
// Clear structure:
// Step 4: Helper functions (pure logic)
// Step 5: CRUD operations (database logic)
// Step 6: Event listeners (user interaction)
// Step 7: Session management (auth logic)
```

**2. Easy to Find & Modify**
- Need to change button behavior? → Go to Step 6
- Need to fix database query? → Go to Step 5
- Need to tweak HTML generation? → Go to Step 4

**3. Separation of Concerns**
```javascript
// Business logic (Step 5):
const deleteTodo = async (todoId) => {
  await supabase.from('todos').delete().eq('id', todoId);
  fetchTodos();
};

// UI wiring (Step 6):
document.getElementById('delete-all-btn')
  .addEventListener('click', async () => {
    if (confirm('Delete all?')) {
      await deleteTodo(todoId);
    }
  });
```

**4. Avoid Duplication**
```javascript
// Bad: Event handler has business logic
deleteBtn.addEventListener('click', async () => {
  if (!confirm('Delete?')) return;
  const { error } = await supabase.from('todos').delete().eq('id', todoId);
  if (error) alert(error.message);
  fetchTodos();
});

// Good: Reusable function
deleteBtn.addEventListener('click', () => deleteTodo(todoId));
```

**5. Testability**
```javascript
// Can test CRUD functions without simulating clicks:
test('deleteTodo removes todo from database', async () => {
  await deleteTodo(123);
  // Assert todo is gone
});
```

**Alternative patterns:**
- **Component-based:** Group all delete-related code together
- **Module-based:** Separate files for auth, todos, UI
- **Class-based:** TodoApp class with methods

For beginners, the step-by-step approach with grouped listeners is easiest to understand!

---

## Congratulations!

You've built two complete database applications:

**Python Music Library**
- Fetched data from a public API
- Created a relational SQLite database
- Learned about foreign keys and relationships
- Exported data to CSV files
- Used built-in Python modules (csv, os, sqlite3)

**Supabase Todo App**
- Set up a cloud PostgreSQL database
- Implemented user authentication
- Secured data with Row Level Security
- Built a full CRUD web application

### Next Steps

**Continue Learning:**
- Explore [Supabase Docs](https://supabase.com/docs) for more features
- Try the Challenge Exercises above
- Build your own project!

**Project Ideas:**
- Expense tracker with categories
- Recipe organizer with ingredients
- Study timer with session history
- Bookmark manager with tags
- Workout tracker with progress charts

### Additional Resources

- [SQLite Tutorial](https://www.sqlitetutorial.net/)
- [Supabase YouTube Channel](https://www.youtube.com/@Supabase)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [REST API Design Best Practices](https://restfulapi.net/)

### Share Your Work

Built something cool? Share it with the HackWashU community!

---

**Questions?** Don't hesitate to ask the workshop facilitators or post in the Discord/Slack!

Happy coding!
