# Putting the workshop app on the internet

Written 14 October 2026. **Nothing has been hosted yet.** These are the steps, and what was and was not tested.

The app has two parts: the **program** (this repository, packaged by the `Dockerfile`) and the **database** (PostgreSQL). Supabase can hold the database. Supabase does not run the program, so the program needs a second service that runs a Docker container, such as Render, Fly.io or Railway. Both must be set up by the account owner; they cannot be created from this repository.

## What the app now does for itself

- **Updates its own database.** Each time the container starts it brings the tables up to date before serving. Nobody runs a database command by hand.
- **Keeps the blank job-sheet picture in the database.** Upload it once in *Workshop details*; printing then needs no files on the server.
- **Closes the tables to Supabase's public data API.** Supabase publishes tables in the `public` schema through a web address unless row level security is on. The app's update switches it on for every table, with no policies, so only the app's own database login can read or write. Checked by a PostgreSQL test; not checked on a real Supabase project.
- **Per-staff logins**, added by the owner in *Workshop details*.
- **Locks out guessing.** Ten wrong passwords from one address in five minutes makes that address wait. This counter lives in memory and resets when the program restarts.
- **Works behind the host's HTTPS.** The container trusts the forwarding headers the host adds. Only use it behind such a host, never open to the internet directly.

## Steps

1. **Supabase:** create a project in the Singapore region. Open *Connect* and copy the **Session pooler** connection string (port 5432). Do not use the Transaction pooler (port 6543): the app holds row locks inside a transaction and was not tested through it.
2. **Owner password:** on your own computer run `python scripts/workshop_password.py`, type a password of 16 or more characters twice, and copy the line it prints (it starts with `scrypt$`). The password itself is never stored.
3. **Host:** create a web service from this repository using the `Dockerfile`. Set these settings as secrets:

   | Setting | Value |
   |---|---|
   | `DATABASE_URL` | the Supabase session pooler string, with the database password filled in |
   | `WORKSHOP_ENABLED` | `true` |
   | `WORKSHOP_AUTH_USERNAME` | the owner's login name, for example `victor` |
   | `WORKSHOP_AUTH_PASSWORD_HASH` | the `scrypt$…` line from step 2 |
   | `WORKSHOP_ORIGIN` | the exact address the host gives, for example `https://yap-workshop.onrender.com` (must be `https`) |
   | `WORKSHOP_AI_ENABLED` | `false` |

4. **First visit:** open `https://…/workshop`, sign in as the owner, and follow *Workshop details*: workshop details, blank job-sheet picture, staff logins.

## What hosting does not solve, and what to do

- **Job-sheet photos need a disk.** Attached photos and per-job download files are written to a folder (`WORKSHOP_STORAGE_DIR`). Most hosts wipe the container's folder on every restart. Either add the host's persistent disk and point `WORKSHOP_STORAGE_DIR` at it, or do not attach photos. Everything else (jobs, invoices, payments, expenses, the form picture) is in the database.
- **Paper guide pictures** are read from a folder (`WORKSHOP_GUIDE_DIR`) and are not in the database. Without that folder the pop-up says none are set up.
- **Backups.** Supabase's free plan pauses a project after about a week of low activity and, according to third-party write-ups, keeps no backups; the paid plan keeps daily ones. Check Supabase's current pricing page before relying on either. Independently of the plan, `scripts/backup_workshop.sh` saves a dated copy of the whole database to a folder of your choice; run it daily from a computer you control.
- **Sign-in is the browser's own username/password box.** There is no sign-out button; close the browser to switch person. On a shared counter computer staff must do that or everything is recorded under one name.
- **The other pages of this program** (the parts and vehicle assistant at `/`) are served from the same container and are not behind the workshop login.
- **Customer data on the internet.** Names, vehicle numbers and phone numbers will sit with Supabase and the host. The workshop should agree to that before real customers are entered.

## Running it on one computer instead

`scripts/run_workshop.sh "<settings file>" [port]` updates the database and serves until Ctrl-C. Set `PYTHON` to the project's Python if it is not on the path.
