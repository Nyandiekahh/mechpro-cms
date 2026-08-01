# MECHPRO SOLUTIONS LTD — Backend

Django 5 + Django REST Framework backend implementing the Website Requirements
Specification: RFQ lead-generation system with unique references and email
notifications, full CMS via Django admin, product catalogue with search/filters,
services/solutions/projects/blog content API, SEO endpoints, reCAPTCHA and
rate limiting.

## Quick start (development)

```bash
cd ~/projects/mechpro-backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env               # then edit .env
python manage.py migrate
python manage.py seed_initial      # loads all website content
python manage.py createsuperuser   # your admin login
python manage.py runserver 0.0.0.0:8000
```

- Admin (CMS): http://localhost:8000/admin/
- API root examples: /api/site/ · /api/services/ · /api/products/ · /api/blog/
- RFQ endpoint: POST /api/rfq/
- Lead analytics: /admin/leads/quotationrequest/analytics/

## Gmail app password (mechpro.co.ke@gmail.com)

1. Sign in to the dedicated account → myaccount.google.com → **Security**.
2. Turn on **2-Step Verification** (required before app passwords appear).
3. Security → **App passwords** → create one named "MECHPRO Website".
4. Paste the 16-character password into `.env` as `EMAIL_HOST_PASSWORD`
   (no spaces). `EMAIL_HOST_USER` stays `mechpro.co.ke@gmail.com`.
5. In development, emails print to the terminal instead (console backend) —
   no credentials needed until production.

## The RFQ workflow (WRS steps 1–7)

POST /api/rfq/ → validate → store → generate `MECH-RFQ-<year>-<000001>` →
email acknowledgment to the customer → email alert to `RFQ_NOTIFY_EMAILS` →
JSON receipt `{reference, created_at}` for the confirmation screen.
Every send (or failure) is recorded in **Email logs** in admin.

## Connecting the React frontend

Add to the frontend `.env`: `REACT_APP_API_URL=http://localhost:8000`

Swap the RequestQuote submit (the commented Django POST point) for:

```js
const res = await fetch(`${process.env.REACT_APP_API_URL}/api/rfq/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(form),
});
const data = await res.json();   // { reference: "MECH-RFQ-2026-000123", ... }
```

Content pages migrate the same way at your pace: each `src/data/*.js` file has a
matching endpoint returning identical keys (`/api/services/`, `/api/products/`,
`/api/solutions/`, `/api/projects/`, `/api/blog/`, `/api/site/`), so a page can
switch from static import to `fetch` without any rendering changes.

## Production deployment (Ubuntu + gunicorn + nginx)

```bash
# .env for production:
#   DEBUG=False
#   SECRET_KEY=<long random string>
#   ALLOWED_HOSTS=api.mechpro.co.ke
#   FRONTEND_URL=https://mechpro.co.ke
#   CORS_ALLOWED_ORIGINS=https://mechpro.co.ke,https://www.mechpro.co.ke
#   DATABASE_URL=postgres://...   (optional; SQLite works for this scale)
#   EMAIL_HOST_PASSWORD=<app password>
#   RECAPTCHA_SECRET_KEY=<from Google reCAPTCHA console>

export DJANGO_SETTINGS_MODULE=mechpro.settings.production
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn mechpro.wsgi:application --bind 127.0.0.1:8001 --workers 3
```

systemd unit (`/etc/systemd/system/mechpro.service`):

```ini
[Unit]
Description=MECHPRO backend
After=network.target

[Service]
User=nyandieka
WorkingDirectory=/home/nyandieka/projects/mechpro-backend
Environment=DJANGO_SETTINGS_MODULE=mechpro.settings.production
ExecStart=/home/nyandieka/projects/mechpro-backend/venv/bin/gunicorn \
  mechpro.wsgi:application --bind 127.0.0.1:8001 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

nginx site (proxy `/api/`, `/admin/`, `/sitemap.xml`, `/robots.txt`, `/media/`
to gunicorn; serve the React build for everything else):

```nginx
server {
    server_name mechpro.co.ke www.mechpro.co.ke;

    root /var/www/mechpro-frontend/build;
    index index.html;

    location ~ ^/(api|admin|static|media|sitemap\.xml|robots\.txt) {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location / {
        try_files $uri /index.html;   # React Router
    }
}
```

Then `sudo certbot --nginx -d mechpro.co.ke -d www.mechpro.co.ke` for HTTPS.

## Admin cheat-sheet for the client (training day)

- **Site & Company → Site settings**: phone, WhatsApp, emails, hours, socials.
- **Site & Company → Stats / Why-MECHPRO / Brand logos / Testimonials**: homepage blocks.
- **Product Catalogue → Products**: add units, tick badges, upload images with ALT text.
- **Website Content → Services / Industries / Projects / Posts**: all pages;
  posts support drafts and scheduled publishing.
- **Leads & Quotations → Quotation requests**: the sales dashboard — filter,
  assign engineers, update statuses, export CSV, view Analytics.
- **Contact messages / Newsletter subscribers / Email logs**: inbound and audit.
# mechpro-cms
