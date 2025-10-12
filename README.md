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

- **Live demo (GitHub Pages):**
  - URL: [https://agopalareddy.github.io/HackWashU-Databases-Workshop/](https://agopalareddy.github.io/HackWashU-Databases-Workshop/)

  - For GitHub Pages deployments, **do NOT commit secrets**. The app loads `.env` locally for development, but on Pages, `config.js` is generated automatically at deploy time by GitHub Actions using repository secrets.
  - **To deploy your own instance:**
    1. Fork this repo.
    2. In your GitHub repo, go to Settings → Secrets and variables → Actions → New repository secret.
    3. Add `SUPABASE_URL` and `SUPABASE_ANON_KEY` as secrets (values from your Supabase project).
    4. Push to `main` to trigger deploy. The workflow will generate `config.js` with your secrets for Pages (never committed to git).
    5. Your app will be live at `https://<your-username>.github.io/<repo-name>/`.

    The Supabase anon key is designed to be public, but always rely on RLS policies for security.

---


## Supabase Setup & Deployment Notes

- Create a `todos` table with columns: `id`, `task`, `user_id`, `is_complete`, `created_at`.
- Enable RLS and add policies for SELECT, INSERT, UPDATE, DELETE:
  - Example: `user_id = auth.uid()`
  - Use your project's URL and anon key in `.env` for local dev, and as GitHub repo secrets for Pages deploy.

### GitHub Actions/Pages Deployment

- The workflow in `.github/workflows/pages.yml` builds the site and injects your Supabase config as `config.js` at deploy time.
- **Never commit `config.js` or secrets to git.**
- Add your Supabase credentials as repo secrets (`SUPABASE_URL`, `SUPABASE_ANON_KEY`).
- On push to `main`, the workflow deploys to GitHub Pages with secrets injected securely.

---


## Troubleshooting & Tips

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
