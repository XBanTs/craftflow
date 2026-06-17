<div align="center">

# 🛠️ CraftFlow

### Premium Freelance Marketplace, Built for Craftsmanship

*Where quality‑focused clients meet skilled freelancers for work that matters.*

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen?style=for-the-badge)](https://craftflow-tyl3.onrender.com)
[![Django](https://img.shields.io/badge/Django-5.1-0C4B33?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)

[**Live Demo**](https://craftflow-tyl3.onrender.com) · [**Report a Bug**](https://github.com/XBanTs/craftflow/issues) · [**Request a Feature**](https://github.com/XBanTs/craftflow/issues)

</div>

---

## ✨ Overview

**CraftFlow** is a full‑stack freelance marketplace platform that goes beyond a typical CRUD job board. It's a production‑grade system handling real‑time‑feeling messaging, notifications, multi‑facet reviews, verified freelancer trust signals, and a REST API layer — all wrapped in a responsive, animated UI with dark/light gradient theming.

It was built to answer a simple question: *what does a freelance marketplace look like when it's engineered with the same rigor as the products freelancers are hired to build?*

<table>
<tr>
<td width="50%">

**For Clients**
- Post jobs with rich filtering for category, budget, and timeline
- Review bids and freelancer portfolios side by side
- Message freelancers directly, with live notification pings
- Rate freelancers on communication, quality, and timeliness

</td>
<td width="50%">

**For Freelancers**
- Build a public portfolio gallery to showcase past work
- Save proposal drafts before committing to a bid
- Bookmark jobs worth revisiting
- Earn a verified badge that signals trust to clients

</td>
</tr>
</table>

---

## 🚀 Live Demo

> **[craftflow-tyl3.onrender.com](https://craftflow-tyl3.onrender.com)**

The app is deployed on Render with a managed PostgreSQL instance on Supabase. Cold starts on the free tier may take a few seconds on first load — that's Render spinning the dyno back up, not the app.

---

## 🧩 Feature Breakdown

| Category | Capabilities |
|---|---|
| **Auth & Identity** | Email‑verified registration (SendGrid), admin‑toggled verified freelancer badges |
| **Core Marketplace** | Full CRUD for jobs, bids, services, and portfolios |
| **Communication** | Real‑time‑style messaging and notifications via AJAX polling |
| **Proposals** | Draft‑save‑before‑submit workflow so freelancers never lose a half‑written pitch |
| **Trust & Reputation** | Multi‑facet reviews (communication, quality, timeliness) + verified badges |
| **Discovery** | Advanced search and filtering by category, budget, status, and date |
| **Engagement** | Bookmarking/saving jobs for later |
| **Dashboards** | Role‑aware stats for both clients and freelancers |
| **API** | 8‑endpoint REST API built on DRF, with a ready‑to‑import Postman collection |
| **Design** | Fully responsive UI with animations and dark/light gradient themes |
| **Infra** | PostgreSQL on Supabase, WhiteNoise for static assets, deployed on Render |

---

## 🏗️ Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| **Backend Framework** | Django 5.1 (Python 3.13) |
| **API Layer** | Django REST Framework |
| **Database** | SQLite (dev) → PostgreSQL via Supabase (production) |
| **Static Assets** | WhiteNoise |
| **Transactional Email** | SendGrid Web API |
| **WSGI Server** | Gunicorn |
| **Config Management** | python‑decouple |
| **Image Handling** | Pillow |
| **Hosting** | Render (web service) + Supabase (managed Postgres) |

</div>

### Why this stack?

Django's batteries‑included philosophy made sense for a project with this many interconnected models — jobs, bids, services, portfolios, messages, notifications, and reviews all need to talk to each other cleanly, and Django's ORM and admin panel make that manageable without reinventing the wheel. DRF layers a real API on top for anything that needs to live outside the template‑rendered pages, and Supabase's managed Postgres means production data doesn't live and die with a single dyno.

---

## 📐 Architecture at a Glance

```
┌─────────────────────────────────────────────────────────┐
│                        Client (Browser)                   │
│         Responsive UI · AJAX Polling · Animations          │
└───────────────────────────┬─────────────────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │   Django Application │
                  │  ───────────────────  │
                  │  Views · Templates    │
                  │  DRF API (8 endpoints)│
                  │  Auth + Email (SG)    │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │   PostgreSQL (Supabase) │
                  │  Jobs · Bids · Services │
                  │  Portfolios · Messages  │
                  │  Notifications · Reviews│
                  └─────────────────────┘
```

Deployed end‑to‑end on **Render**, with static files served via **WhiteNoise** rather than a separate CDN — keeping the infrastructure footprint deliberately small while still production‑safe.

---

## 📸 Screenshots

<div align="center">

<table>
<tr>
<td><img src="static/images/craftflowpic1.png" alt="CraftFlow Screenshot 1" width="100%"></td>
<td><img src="static/images/craftflowpic2.png" alt="CraftFlow Screenshot 2" width="100%"></td>
</tr>
<tr>
<td><img src="static/images/craftflowpic3.png" alt="CraftFlow Screenshot 3" width="100%"></td>
<td><img src="static/images/craftflowpic4.png" alt="CraftFlow Screenshot 4" width="100%"></td>
</tr>
<tr>
<td colspan="2" align="center"><img src="static/images/craftflowpic5.png" alt="CraftFlow Screenshot 5" width="50%"></td>
</tr>
</table>

</div>

---

## ⚡ Getting Started

### Prerequisites

- Python 3.13+
- pip
- (Optional) A SendGrid account for outbound email in production

### 1. Clone the repository

```bash
git clone https://github.com/XBanTs/craftflow.git
cd craftflow
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your values:

```env
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
SENDGRID_API_KEY=your-sendgrid-key   # optional for local dev
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 4. Run migrations and seed the database

```bash
python manage.py migrate
python manage.py seed_data
```

### 5. Create a superuser and launch

```bash
python manage.py createsuperuser
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** and you're in.

---

## 🔑 Environment Variables

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Django secret key | random 50‑character string |
| `DEBUG` | Debug mode | `False` in production |
| `DATABASE_URL` | Database connection string | `postgres://user:pass@host:port/db` |
| `ALLOWED_HOSTS` | Comma‑separated allowed hosts | `localhost,craftflow-tyl3.onrender.com` |
| `SENDGRID_API_KEY` | SendGrid API key for transactional email | `SG.xxxxxxxx` |
| `DEFAULT_FROM_EMAIL` | Sender address for outbound email | `noreply@craftflow.com` |

---

## 📡 API Documentation

CraftFlow ships a REST API built on Django REST Framework, covering jobs, bids, services, and portfolios.

- Full endpoint reference: [`api_docs.md`](./api_docs.md)
- Ready‑to‑import collection: [`postman_collection.json`](./postman_collection.json)

Import the Postman collection to start exploring requests immediately — no manual setup required.

---

## 🗺️ Roadmap

- [ ] WebSocket‑based messaging and notifications (replacing AJAX polling)
- [ ] Escrow‑style payment integration
- [ ] In‑app dispute resolution workflow
- [ ] Freelancer skill assessments / certifications
- [ ] Public API rate limiting and API keys for third‑party integrations

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👤 Author

**Emmanuel Ayo "XBanTs" Oyewo**
Principal Software Engineer & Lead Engineer @ [XJ TechSpace](https://xjtechspace.com)

- Portfolio: [ayo.xjtechspace.com](https://ayo.xjtechspace.com)
- Twitter / X: [@XBanTs_](https://twitter.com/XBanTs_)
- Medium: [@Ayo_Oyewo](https://medium.com/@Ayo_Oyewo)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Built with Django, deployed with intent.*

⭐ **If CraftFlow inspired part of your stack, consider starring the repo.**

</div>
