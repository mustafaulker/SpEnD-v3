# SpEnD v3.0

## SparQL Endpoint Crawler & Analyzer

Crawls various search engines (e.g. **Google**, **Bing**, **Aol**, etc.) with given query keywords.  
Checks if gathered websites is an Endpoint or not, if so stores them in the database. (i.e. **MongoDB**)

- Current discovered **_Endpoints:_** **258**

## Execution

`$ docker compose up`

### UI

[`localhost:5000`](http://localhost:5000/)

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
    │   ├── second_crawl.py
    │   └── scrapy.cfg
    ├── run.py  
    ├── Docker-compose.yml  
    ├── Dockerfile  
    ├── requirements.txt  
    └── README.md
