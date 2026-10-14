# Putting the workshop app on the internet

Written 14 October 2026. **Hosted on 14 October 2026** at `https://yap-workshop.onrender.com` (Render free plan, Singapore) with a Supabase database in Sydney. These are the steps, and what was and was not tested. How the parts fit together: [system design](WORKSHOP_SYSTEM_DESIGN.md).

The app has two parts: the **program** (this repository, packaged by the `Dockerfile`) and the **database** (PostgreSQL). Supabase can hold the database. Supabase does not run the program, so the program needs a second service that runs a Docker container, such as Render, Fly.io or Railway. Both must be set up by the account owner; they cannot be created from this repository.

## What the app now does for itself

- **Updates its own database.** Each time the container starts it brings the tables up to date before serving. Nobody runs a database command by hand.
- **Keeps every file in the database.** The blank job-sheet picture, job-sheet photos and per-job download files are stored in the database, so a host with no disk loses nothing on restart. Photos saved by older versions are still read from the `WORKSHOP_STORAGE_DIR` folder.
- **Closes the tables to Supabase's public data API.** Supabase publishes tables in the `public` schema through a web address unless row level security is on. The app's update switches it on for every table, with no policies, so only the app's own database login can read or write. Checked by a PostgreSQL test; not checked on a real Supabase project.
- **Per-staff logins**, added by the owner in *Workshop details*.
- **Sign-in page.** People sign in on `/workshop/login` and stay signed in for 12 hours; **Sign out** is in the top bar.
- **Locks out guessing.** Ten wrong passwords in five minutes, from one address or for one login name, makes further tries wait. Counting by name matters because Render passes on the visitor's address in a header the visitor can fake. Only two password checks run at once, so a burst of guesses queues instead of running the 512 MB server out of memory. The counters live in memory and reset when the program restarts.
- **Stays awake.** `.github/workflows/keep-awake.yml` asks `/health` every 10 minutes from 07:00 to 22:00 Singapore time (about 465 of the free 750 hours a month). `/health` also asks the database a trivial question, which keeps a free Supabase project from pausing. GitHub may run these late and switches them off after 60 days without commits; switch it back on under the repository's *Actions* tab.
- **Backups without PostgreSQL tools.** *Workshop details → Download backup* (owner only) saves everything, photos included, as one zip. `scripts/restore_workshop.py` loads it into an empty database.
- **Works behind the host's HTTPS.** The container trusts the forwarding headers the host adds. Only use it behind such a host, never open to the internet directly.

## Steps

1. **Supabase:** create a project in the Singapore region. Open *Connect* and copy the **Session pooler** connection string (port 5432). Do not use the Transaction pooler (port 6543): the app holds row locks inside a transaction and was not tested through it.
2. **Owner password:** on your own computer run `python scripts/workshop_password.py`, type a password of 16 or more characters twice, and copy the line it prints (it starts with `scrypt$`). The password itself is never stored.
3. **Host (Render, free plan):** push this repository to GitHub, then in Render choose *New → Blueprint* and pick it. `render.yaml` creates one free web service in Singapore and asks for the first four settings below; the rest are filled in. You only learn the address after the first deploy, so put a guess in `WORKSHOP_ORIGIN`, then correct it to the address Render shows and redeploy.

   The free plan sleeps after 15 minutes without visitors and takes up to about a minute to wake; it has 512 MB of memory, 750 hours a month and no disk, so attached photos do not survive a restart. These figures are from third-party write-ups in 2026: check Render's own free-plan page.

   Settings:

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

- **Database size.** Supabase's free database holds 500 MB. Photos are kept as uploaded (up to 8 MB each); phone photos of a sheet are usually 1–3 MB, so roughly 150–400 photos fit next to the books. Watch *Database size* in Supabase; past that, a paid plan or moving photos to Supabase Storage is needed.
- **Paper guide pictures** are read from a folder (`WORKSHOP_GUIDE_DIR`) and are not in the database. Without that folder the pop-up says none are set up.
- **Backups are a person's job.** Supabase's free plan, according to third-party write-ups, keeps no backups. The owner should click *Download backup* at least weekly and keep the file off the shop computer. `scripts/backup_workshop.sh` (pg_dump) also works, but needs PostgreSQL client tools at least as new as Supabase's server; this laptop's pg_dump 14 is too old.
- **Shared counter computer.** Staff must click **Sign out** before the next person, or everything is recorded under one name. Sign-out removes the cookie from that browser only; a copied cookie would keep working until it expires (12 hours) or that login's password changes.
- **The other pages of this program** (the parts and vehicle assistant at `/`) are not behind the workshop login. Set `WORKSHOP_ONLY=true` (the Render blueprint does) and they answer “not found”; `/` goes to `/workshop`.
- **Customer data on the internet.** Names, vehicle numbers and phone numbers will sit with Supabase and the host. The workshop should agree to that before real customers are entered.

## Moving the database to Singapore

The first Supabase project was made in Sydney while the app runs in Singapore, so every database question crosses that distance. To move it:

1. Sign in as the owner and click *Workshop details → Download backup*.
2. In Supabase create a new project in **Southeast Asia (Singapore)**, with a password of letters and digits only.
3. In Render, change `DATABASE_URL` to the new project's **Session pooler** string and save. The app starts and creates its empty tables.
4. On the laptop: `DATABASE_URL='<new session pooler string>' /Volumes/T9/Coco-Car-Damage-Dataset/.venv/bin/python scripts/restore_workshop.py <the backup zip>`. It refuses if the new database already has workshop records or is at a different version.
5. Sign in and check Books and a few jobs, then delete the Sydney project.

## Running it on one computer instead

`scripts/run_workshop.sh "<settings file>" [port]` updates the database and serves until Ctrl-C. Set `PYTHON` to the project's Python if it is not on the path.
