# SpEnD v3.0
## SparQL Endpoint Crawler & Analyzer

Crawls various search engines (e.g. Google, Bing, Yahoo, etc.) with given query keywords.  
Checks if gathered websites is an Endpoint or not, if so stores them in the database. (i.e. MongoDB)

- Current discovered **_Endpoints:_** **210** 

### Requirements
- [SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper)
- [PyMongo](https://github.com/mongodb/mongo-python-driver)
- [Search-Engines-Scraper](https://github.com/tasos-py/Search-Engines-Scraper)

Run the following command in the project folder to install all dependencies.

`pip install -r requirements.txt`

### DB Configuration
This project uses **MongoDB** as DBMS.  
If needed, client host can be modified in the **Database** class.

`URI = 'mongodb://localhost:27017/'`

### Search Engine Configuration
Search engines to be crawled, can be selected.  
All engines have been defined in the **Crawler** class.
```python
single_search_engine('keywords', 'duckduckgo')

multiple_search_engine('keywords', 'bing', 'ask')

all_search_engines('keywords')
```

## Execution
Run `python main.py` in the project folder.  
or just  
Run `docker-compose up` without any configuration.
