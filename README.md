# SpEnD v3.0

## SparQL Endpoint Crawler

Crawl process is created with the search engines selected and the keywords provided by the admin.

Crawl process can be set as, "Instant", "Crawl once on the specified date" or "Crawl continuously at certain day
intervals".

Endpoints obtained as a result of the Crawl process wait for admin control and approval on the "pending" page.

Endpoints appear on the Home page after admin approval.

---

#### Crawlable Search Engine

- Google
- Bing
- Mojeek
- Aol
- Ask

## Execution

`$ docker compose up`

---

### UI

[`localhost:5000`](http://localhost:5000/)

#### Login

> ID: `admin`  
Password: `pass`

---

### Project Layout

    .
    ├── src/
    │   ├── frontend/
    │   │   ├── static/
    │   │   │   ├── css/
    │   │   │   │   ├── admin/
    │   │   │   │   ├── auth/
    │   │   │   │   └── errors/
    │   │   │   ├── images/
    │   │   │   └── js/
    │   │   ├── templates/
    │   │   │   ├── admin/
    │   │   │   │   ├── crawl/
    │   │   │   │   ├── logs/
    │   │   │   │   ├── manage/
    │   │   │   │   ├── keywords/
    │   │   │   │   ├── users/
    │   │   │   │   └── ...
    │   │   │   ├── auth/
    │   │   │   ├── errors/
    │   │   │   └── ...
    │   │   ├── __init__.py
    │   │   ├── config.py
    │   │   ├── errors.py
    │   │   ├── models.py
    │   │   └── routes.py
    │   ├── SpEnD/
    │   │   ├── spiders/
    │   │   │   └── ...
    │   │   ├── __init__.py
    │   │   ├── items.py
    │   │   ├── middlewares.py
    │   │   ├── pipelines.py
    │   │   └── settings.py
    │   ├── utils/
    │   │   ├── database_controller.py
    │   │   ├── sparql_controller.py
    │   │   └── util.py
    │   ├── main_crawl.py
    │   ├── inner_crawl.py
    │   └── scrapy.cfg
    ├── run.py
    ├── docker-compose.yml
    ├── Dockerfile
    ├── .dockerignore
    ├── requirements.txt
    └── README.md
