# SpEnD v3.0

## SparQL Endpoint Crawler

Crawls search engines with various crawling options for **SparQL Endpoints**.

Provides continuous and flexible crawl options.

Aims to keep the Endpoint database fresh and up to date.

Crawls more than **200** endpoints in a single run.

### Crawlable Search Engines

- Google
- Bing
- Mojeek
- Aol
- Ask

## Execution

`$ docker compose up`

### UI

[`localhost:5000`](http://localhost:5000/)

### Login

> Username: `admin`  
> Password: `pass`

## Usage

### Crawl

Crawl tasks created on the **Crawler** page under Crawling menu.  
At least one search engine and one keyword must be selected to create a crawling task.

Keywords do not just have to be chosen from default keywords; desired keywords can be crawled by writing them to the
**Add keyword** field.  
Keywords can be managed on the specific page under Keyword Management menu.

#### Scheduling a Crawl Task

Tasks can be scheduled as;

- **Instant**: Starts crawling right away.
- **Specific** date: Starts crawling at specified date and time.
- **Specific interval**: Starts crawling at specified date interval. (e.g., every four days)

#### Inner Crawl

Makes the crawl process even deeper.  
Searches for the missed endpoints right after the main crawl process.

### Task Management

Created tasks can be managed later on the Scheduled Tasks page.

Tasks can be postponed by one day, paused/resumed, or removed.

**auto_crawl** is a task that daily crawls all search engines with all crawling keywords. Also, the inner crawl option
is selected.  
**status_check** is a task that checks the response status of all endpoints except the removed links.

### Endpoint Management

Freshly crawled endpoints will appear on the **Pending** page to await admin approval.

Crawled endpoints can be either approved, suspended or removed.

**Approved** endpoints will appear in the table on the **Home** page.

**Suspended** endpoints can be thought as Quarantined.  
This option can be used in the situations like, perfectly working endpoint is down for more than 3-4 days, and you do
not want to keep it in the Home table.

There is no way to remove an object permanently. Removed objects are listed on the **Removed** page as a design choice,
or you may want to recover them.

### Logs

Various log records can be viewed, such as;

- Exceptions/Errors
- Crawler logs
- Status Check logs
- Authentications
- Guests

### Keyword Management

Keywords can be inserted or removed on this page.

- **Crawl keys**: Keywords to be crawled in the main crawl.
- **Inner keys**: Keywords to be crawled in the inner crawl.
- **Wanted keys**: Keywords to filter crawl results. The crawled page must contain one of these keywords, otherwise the
  page will be ignored.
- **Unwanted keys**: Keywords to filter crawl results. The crawled page will be ignored, if the page contains any of
  these keywords.

## Further Development

- Improvements can be made on the ban problem of search engines. Such as Region Changing or using Proxy Servers.
- Filtering can be improved to avoid non-endpoint pages. Adding more accurate filter keywords or using RegEx should be
  considered.

## Project Layout

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
    ├── .gitattributes
    ├── .gitignore
    ├── requirements.txt
    ├── LICENSE
    └── README.md

## License

**SpEnD-v3** is licensed under [MIT License](https://github.com/mustafaulker/SpEnD-v3/blob/master/LICENSE).
