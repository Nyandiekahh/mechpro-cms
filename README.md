# MECHPRO SOLUTIONS LTD — Backend Documentation

Complete technical and operational documentation for the Django backend
powering mechpro.co.ke. Written so that a competent developer who has
never seen this project could take it over using only this document.

---

## 1. Technology Stack

| Layer | Technology | Version (approx) |
|---|---|---|
| Language | Python | 3.11+ |
| Framework | Django | 5.2 |
| API layer | Django REST Framework | 3.17 |
| Database | SQLite (file-based) | built into Python |
| Web server (app) | Gunicorn | 26 |
| Reverse proxy | Nginx | 1.22 |
| TLS certificates | Let's Encrypt (via Certbot) | — |
| Process manager | systemd (`mechpro.service`) | OS-level |
| Image processing | Pillow | latest |
| Spreadsheet export | openpyxl | latest |
| CORS handling | django-cors-headers | 4.9 |
| Filtering | django-filter | 26 |
| Static file serving | WhiteNoise | 6.12 |
| OS | Debian 12 (Bookworm) | — |

**Why SQLite in production:** at MECHPRO's current traffic scale, a
single-file database is simpler to operate, back up, and restore than a
separate database server, and avoids an entire class of connection/auth
configuration. If traffic grows substantially, migrating to PostgreSQL is
a supported path (`DATABASE_URL` in `.env` already expects a Postgres URL
format when the time comes) — not an emergency, just a future option.

## 2. Project Structure

```
mechpro-backend/
├── manage.py
├── requirements.txt
├── .env                      # NEVER committed to git — real secrets live here
├── .env.example               # template, safe to commit
├── db.sqlite3                 # the actual database — BACK THIS UP REGULARLY
├── media/                     # uploaded images/files — BACK THIS UP TOO
├── staticfiles/                # collected static assets (admin CSS/JS etc.)
├── mechpro/
│   ├── settings/
│   │   ├── base.py            # shared settings
│   │   ├── development.py     # used locally (DEBUG=True, console email)
│   │   └── production.py      # used on the live server (DEBUG=False, HTTPS enforced)
│   ├── urls.py                 # top-level URL routing
│   ├── wsgi.py                 # entry point gunicorn uses
│   └── sitemaps.py             # XML sitemap generation
├── core/                       # site-wide settings, leads-adjacent utilities
│   ├── models.py               # SiteSettings, Stat, WhyUsItem, Testimonial,
│   │                            #   BrandLogo, ContactMessage, NewsletterSubscriber,
│   │                            #   EmailLog, LegalPage, ClickEvent
│   ├── admin.py
│   ├── views.py                 # site bundle, contact form, newsletter,
│   │                            #   maintenance status, legal pages, click tracking
│   ├── serializers.py
│   ├── emails.py                 # templated email sending engine
│   ├── security.py               # reCAPTCHA verification, client IP helper
│   └── management/commands/      # see section 9
├── catalogue/                   # products, brands, categories
├── content/                      # services, industries/solutions, projects, blog
├── leads/                        # the RFQ lead-generation system
└── templates/
    ├── emails/                   # HTML + plain-text email templates
    ├── robots.txt
    └── admin/                    # custom admin template overrides
```

## 3. Running Locally

```bash
git clone <repo-url> mechpro-backend
cd mechpro-backend
python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # then edit .env — see section 4
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000/admin/` to log in. In development, emails
print to your terminal instead of sending (see `SEND_REAL_EMAILS` below).

## 4. Environment Variables (`.env`)

**Never commit `.env` to git.** It is gitignored on purpose — every
machine (your laptop, the server) needs its own copy with its own
values, and a leaked `SECRET_KEY` or email password is a real security
incident, not a formality.

| Variable | Purpose | Example (production) |
|---|---|---|
| `SECRET_KEY` | Django's cryptographic signing key | long random string |
| `DEBUG` | Verbose error pages when `True` | `False` in production, always |
| `ALLOWED_HOSTS` | Which domains Django will respond to | `api.mechpro.co.ke,<server-ip>` |
| `FRONTEND_URL` | Used to build sitemap URLs and CORS | `https://www.mechpro.co.ke` |
| `CORS_ALLOWED_ORIGINS` | Which frontend origins may call this API | `https://www.mechpro.co.ke,https://mechpro.co.ke` |
| `DATABASE_URL` | Leave blank for SQLite; Postgres URL if migrated | (blank) |
| `EMAIL_HOST` | SMTP server | `smtp.zoho.com` (see section 5) |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS | `True` |
| `EMAIL_HOST_USER` | The mailbox that authenticates | `info@mechpro.co.ke` |
| `EMAIL_HOST_PASSWORD` | App-specific password for that mailbox | (secret) |
| `DEFAULT_FROM_EMAIL` | The From header customers see | `MECHPRO SOLUTIONS LTD <info@mechpro.co.ke>` |
| `SEND_REAL_EMAILS` | `False` prints emails to console instead of sending | `True` in production |
| `RFQ_NOTIFY_EMAILS` | Comma-separated inboxes that get new-lead alerts | `info@mechpro.co.ke` |
| `RECAPTCHA_SECRET_KEY` | Google reCAPTCHA secret; blank disables verification | (from Google reCAPTCHA console) |

## 5. Email Configuration (info@mechpro.co.ke via Zoho)

The system sends two kinds of email: the customer's automatic
acknowledgment when they submit an RFQ or contact form, and the
sales-team alert notifying MECHPRO of a new lead. Both are sent through
`info@mechpro.co.ke`, hosted on Zoho Mail, **not** through a Gmail
account — this matters for deliverability (customers see your real
domain in the From address, not a Gmail address impersonating it).

**Getting Zoho SMTP credentials:**
1. Log into Zoho Mail as `info@mechpro.co.ke`.
2. Go to Zoho Account → Security → App Passwords.
3. Generate an app-specific password (do not use the mailbox's normal
   login password for SMTP — Zoho, like Gmail, requires a separate
   app password when 2FA is on).
4. Confirm the SMTP host in your Zoho plan's mail settings — typically
   `smtp.zoho.com`, port `587`, TLS enabled.

**Verifying it works:**
```bash
python manage.py test_email your-personal-email@example.com
```
Check the received email's From header shows `info@mechpro.co.ke`.

**Why the sender and the notification recipient can be configured
separately:** `EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD` control who
*sends* (authenticates with Zoho); `RFQ_NOTIFY_EMAILS` controls who
*receives* the sales alert (can be multiple addresses, comma-separated,
useful during a transition between inboxes or if several staff should
see new leads).

## 6. Deploying to Production

Full step-by-step deployment (server setup, gunicorn, nginx, HTTPS) is
covered in the project's deployment history — the short version, once a
server already exists and is configured (see section 7 for what "already
configured" means):

```bash
cd /var/www/mechpro-backend
git pull
source venv/bin/activate
pip install -r requirements.txt        # only if requirements.txt changed
python manage.py migrate                # ALWAYS review what it's about to apply first — see section 8
python manage.py collectstatic --noinput --clear
systemctl restart mechpro
```

**Always check `systemctl status mechpro` after restarting** — a failed
restart leaves the *previous* process running silently in some setups;
confirm the new one is actually up before considering a deploy finished.

## 7. Hosting / Server Details

| Item | Value |
|---|---|
| Provider | HostAfrica (Cloud Server — Kenya) |
| Plan | C1 — 1 vCore, 1GB RAM, 20GB storage |
| OS | Debian 12 (Bookworm) |
| Server IP | *(recorded in the credential register — see handover checklist)* |
| SSH access | `ssh root@<server-ip>` (key-based; see section 17 on security) |
| Web server | Nginx, config at `/etc/nginx/sites-available/mechpro` |
| App process | Gunicorn, managed by systemd unit `/etc/systemd/system/mechpro.service` |
| App directory | `/var/www/mechpro-backend` |
| Domain (API) | `api.mechpro.co.ke` |
| Swap file | 1GB swap configured at `/swapfile` (safety margin on the 1GB RAM plan) |

**Restarting the app after any code or `.env` change:**
```bash
systemctl restart mechpro
```
**Viewing live logs (essential for debugging any 500 error):**
```bash
journalctl -u mechpro -n 50 --no-pager
```
**Checking nginx config validity before reloading:**
```bash
nginx -t && systemctl reload nginx
```

## 8. Database Details & Restoration

The entire database is one file: `/var/www/mechpro-backend/db.sqlite3`.

**⚠️ Critical: this file currently has NO automated backup configured.**
Set one up before relying on this system for real business data long
term — see section 10.

**Manual backup (do this before any risky operation):**
```bash
cp db.sqlite3 db.sqlite3.backup-$(date +%Y%m%d-%H%M%S)
```

**Restoring from a backup:**
```bash
systemctl stop mechpro
cp db.sqlite3.backup-YYYYMMDD-HHMMSS db.sqlite3
systemctl start mechpro
```

**Applying new migrations safely (never blind):**
```bash
python manage.py migrate --plan     # shows what WOULD run, without running it
python manage.py migrate            # then actually run it
```
A migration that only says "Add field" or "Create model" is additive and
safe — it never deletes or overwrites existing rows. A migration that
says "Alter field" or "Remove field" deserves a manual backup first and
a moment of real attention to what's changing.

## 9. Management Commands Reference

| Command | Purpose | Safe to re-run? |
|---|---|---|
| `seed_initial` | Loads base site content (services, industries, etc.) | Yes — uses `get_or_create`, skips existing rows |
| `import_product_catalogue` | Loads the 147-product supplier catalogue | Yes — matches on brand+model, updates rather than duplicates |
| `delete_demo_products` | Permanently removes the 8 placeholder demo products | Only meaningful once; harmless if run again (nothing left to delete) |
| `sync_brand_logos` | Matches the "Brands We Work With" list to actually-stocked brands | Yes — safe, additive/deactivating only |
| `generate_product_descriptions` | Writes starter descriptions for products with none | Yes by default (skips products that already have one). `--overwrite` replaces existing text — use with care if the admin has hand-edited descriptions |
| `seed_placeholder_images` | Generates on-brand placeholder graphics for products with no photo | Yes — skips products that already have an image unless `--overwrite` |
| `fix_product_slugs` | One-off cleanup of a slug-generation bug (duplicated brand name in URL) | Already run; safe to re-run, will simply report "0 fixed" if nothing needs fixing |
| `seed_legal_pages` | Creates Privacy/Terms/Copyright pages if they don't exist | Yes — never overwrites admin-edited legal text |
| `test_email` | Sends a real test email to verify SMTP config | Yes, always safe |

## 10. Backup Procedure (recommended setup — not yet automated)

**What needs backing up:** `db.sqlite3` (all data) and `media/` (all
uploaded images/files).

**Recommended minimal cron setup** (add via `crontab -e` on the server):
```bash
0 2 * * * cd /var/www/mechpro-backend && tar -czf /root/backups/mechpro-backup-$(date +\%Y\%m\%d).tar.gz db.sqlite3 media/ && find /root/backups -mtime +14 -delete
```
This creates a nightly compressed backup at 2am, keeping 14 days of
history, and deletes anything older automatically. **Important:** this
alone only protects against database corruption, not full server loss —
periodically copy `/root/backups/` off the server entirely (e.g. to your
own machine or a cloud storage bucket) so a backup doesn't live only on
the same disk it's protecting.

## 11. Third-Party Services Inventory

| Service | Purpose | Login/Owner | Renewal | Cost |
|---|---|---|---|---|
| HostAfrica | VPS hosting (server + database) | *(record actual account owner)* | 12-month plan | ~KSh 10,368/year (C1 plan, 10% annual discount) |
| Domain registrar (mechpro.co.ke) | Domain registration + DNS | *(confirm with Peter — predates this build)* | *(confirm)* | *(confirm)* |
| Vercel | Frontend hosting (React build) | *(currently under developer's personal account — see handover checklist item #1/#2 on ownership)* | Free tier (as configured) | KSh 0 (unless upgraded) |
| Zoho Mail | info@mechpro.co.ke mailbox | *(Peter/MECHPRO)* | Per Zoho's plan | *(per Zoho pricing)* |
| Let's Encrypt (via Certbot) | Free SSL certificate for api.mechpro.co.ke | Automatic, no login | Auto-renews every ~60 days | Free |
| Google Search Console | Search indexing monitoring | *(MECHPRO's Google account)* | Free | Free |
| Google Analytics 4 | Traffic analytics | *(not yet fully configured — measurement ID pending)* | Free | Free |
| GitHub | Source code repositories (`mechpro`, `mechpro-cms`) | *(currently under developer's personal GitHub — see ownership note in handover checklist)* | Free tier | Free |

**Ownership note:** several items above are marked as currently under
the developer's personal accounts. This is flagged explicitly in the
project's handover checklist (section 1, 2, 4, 19, 25) as something that
needs a documented transfer plan before final sign-off — see that
document for the full independence checklist.

## 12. CMS / Admin User Manual

Login: `https://api.mechpro.co.ke/admin/`

| Task | Where in admin |
|---|---|
| Edit company phone/WhatsApp/email/hours | Site & Company → Site settings |
| Turn maintenance mode on/off, edit maintenance message | Site & Company → Site settings → Maintenance mode section |
| Edit Contact page heading/intro text | Site & Company → Site settings → Contact page section |
| Add/edit products | Product Catalogue → Products |
| Upload product images, choose "Cover" or "Contain" fit | Product Catalogue → Products → (open a product) → Product images inline |
| Mark a product Featured (shows on homepage) | Product Catalogue → Products → tick "Is featured" |
| Add/edit services, solutions, projects, blog posts | Website Content |
| Edit a project's full write-up (shown on its own page) | Website Content → Projects → open a project → "Full description" field |
| Edit Privacy Policy / Terms / Copyright | Site & Company → Legal pages |
| View and manage RFQ leads | Leads & Quotations → Quotation requests |
| Assign an engineer to a lead, change status | Open the lead → set "Assigned to" and "Status" |
| Export leads to CSV or Excel | Quotation requests list → select rows → Actions dropdown → choose export |
| Export products to Excel | Products list → select rows → Actions dropdown |
| View click-tracking totals (phone/WhatsApp/email clicks) | Site & Company → Click events (totals shown at the top of the list) |
| View contact form submissions | Site & Company → Contact messages |
| View newsletter subscribers | Site & Company → Newsletter subscribers |
| View the email send audit trail | Site & Company → Email logs |

## 13. SEO / Search Console

- Sitemap: `https://www.mechpro.co.ke/sitemap.xml` (auto-generated by
  Django, proxied through the frontend domain via `vercel.json` — see
  frontend README section on this).
- Robots.txt: `https://www.mechpro.co.ke/robots.txt`
- Search Console property: verified for `www.mechpro.co.ke` (domain
  property). Sitemap submitted and confirmed "Success" with 175
  discovered pages as of the last check.
- To check indexing status of any specific page: Search Console → URL
  Inspection → paste the full URL.
- New pages are not indexed instantly — expect days to weeks for full
  indexing of a new site, this is normal Google behavior, not a bug.

## 14. Technical Documentation — API Reference

Base URL (production): `https://api.mechpro.co.ke`

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/site/` | GET | Company config, stats, why-us, brands, testimonials |
| `/api/services/` | GET | List all services |
| `/api/services/<slug>/` | GET | One service, full detail |
| `/api/solutions/` | GET | List all industry solutions |
| `/api/solutions/<slug>/` | GET | One solution, full detail |
| `/api/products/` | GET | Product list, paginated, filterable (`?category=`, `?brand=`, `?featured=`, `?energyRating=`, `?capacity=`, `?installationType=`, `?search=`) |
| `/api/products/<slug>/` | GET | One product, full detail |
| `/api/projects/` | GET | Project list (`?sector=` filter) |
| `/api/projects/<slug>/` | GET | One project, full detail (NEW) |
| `/api/blog/` | GET | Published blog posts |
| `/api/blog/<slug>/` | GET | One article, full detail |
| `/api/legal/<slug>/` | GET | Legal page (`privacy`, `terms`, `copyright`) (NEW) |
| `/api/maintenance/` | GET | Maintenance mode status (NEW) |
| `/api/rfq/` | POST | Submit a quotation request |
| `/api/contact/` | POST | Submit the general contact form |
| `/api/newsletter/` | POST | Subscribe to the newsletter |
| `/api/track-click/` | POST | Log a phone/WhatsApp/email click (NEW) |
| `/api/faqs/` | GET | Flattened FAQ list (used by the chatbot) |
| `/api/leads/analytics/` | GET | Staff-only lead analytics |
| `/sitemap.xml` | GET | XML sitemap |
| `/robots.txt` | GET | Robots file |
| `/admin/` | — | Django admin / CMS |

All list endpoints are paginated (DRF's `PageNumberPagination`, 24 items
per page) unless noted otherwise.

## 15. Security Notes

- HTTPS is enforced (`SECURE_SSL_REDIRECT = True`); HTTP requests
  redirect to HTTPS automatically.
- HSTS is enabled with a 30-day max-age, `includeSubDomains`, and
  `preload` — browsers that have seen this site once will refuse to
  connect over plain HTTP even if a link somehow pointed there.
- Rate limiting is active on RFQ (`5/hour`), contact (`5/hour`), and
  newsletter (`10/hour`) submissions to deter spam/abuse.
- `X-Frame-Options: DENY` prevents the site being embedded in a
  clickjacking iframe.
- Passwords, API keys, and the Django `SECRET_KEY` live only in `.env`,
  which is gitignored — never in source code, never in this repository.
- **Recommendation:** rotate `SECRET_KEY` and any credential that has
  ever been pasted into a chat, email, or shared document, since those
  channels should be treated as potentially exposed.

---

*Last updated as part of the ownership handover and feature expansion
covering: maintenance mode, legal pages, project detail pages, click
tracking, Excel export, and extended product filtering.*
