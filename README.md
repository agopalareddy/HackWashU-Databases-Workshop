# HackWashU Databases Workshop

Welcome to the HackWashU Databases Workshop! This project is designed to introduce participants to practical database concepts, API integration, and modern web app development using Python, SQLite, Supabase, and client-side JavaScript.

---

## Workshop Overview

- **Audience:** Beginners to intermediate developers interested in databases, APIs, and full-stack web apps.
- **Format:** Hands-on, code-along workshop with live demos and Q&A.
- **Materials:**
  - This repo (clone/download)
  - [HackWashU-Databases.pdf](./HackWashU-Databases.pdf) (slides/handout)

---

## Project Structure

```
├── database_generator.py      # Python script: builds a music library DB from iTunes API
├── index.html                # Standalone Supabase-powered Todo app (client-only)
├── app.js                    # JavaScript for the Todo app
├── styles.css                # CSS for the Todo app
├── .env                      # (not committed) Secrets for Supabase
├── .env.sample               # Sample env file for sharing
├── exports/                  # Generated SQLite DB and CSVs
│   ├── music_library.sqlite
│   ├── artists.csv
│   ├── albums.csv
│   └── songs.csv
└── HackWashU-Databases.pdf   # Workshop slides/handout
```

---

## Part 1: Python Music Library Generator

- **Goal:** Learn how to fetch data from a public API, store it in a relational database, and export to CSV.
- **Key Concepts:**
  - SQLite schema design (artists, albums, songs)
  - Foreign keys and relationships
  - API requests (iTunes Search API)
  - Data deduplication and bulk inserts
  - Exporting tables to CSV
- **How to run:**
  ```pwsh
  python -m pip install requests
  python database_generator.py
  ```
- **Outputs:**
  - `exports/music_library.sqlite` (open in DB viewer)
  - CSVs for each table

---

## Part 2: Supabase Todo Web App

- **Goal:** Experience a modern, serverless, full CRUD web app using Supabase (Postgres + Auth) and pure HTML/JS/CSS.
- **Key Concepts:**
  - Supabase client setup and environment variables
  - Row Level Security (RLS) for user data isolation
  - Full CRUD: create, read, update, delete todos
  - UI/UX best practices (collapsible completed tasks, inline editing, etc.)
- **How to run locally:**
  1. Copy `.env.sample` to `.env` and fill in your Supabase project values.
  2. Start a local server:
     ```pwsh
     python -m http.server
     ```
  3. Open [http://localhost:8000/index.html](http://localhost:8000/index.html)

---

## Supabase Setup Notes

- Create a `todos` table with columns: `id`, `task`, `user_id`, `is_complete`, `created_at`.
- Enable RLS and add policies for SELECT, INSERT, UPDATE, DELETE:
  - Example: `user_id = auth.uid()`
- Use your project's URL and anon key in `.env`.

---

## Troubleshooting

- If the web app doesn't load secrets, make sure you are running a local server (not opening HTML directly).
- If you see RLS errors, check your Supabase policies.
- For Python errors, ensure `requests` is installed and you have internet access.

---

## Workshop Tips

- Encourage questions and experimentation!
- Use the provided PDF for reference and live walkthroughs.
- Show how to inspect the SQLite DB and Supabase tables.
- Discuss real-world use cases for APIs, databases, and serverless apps.

---

## License

This project is licensed under the [MIT License](./LICENSE).
