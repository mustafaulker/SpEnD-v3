from flask import Flask, render_template
from flask_mongoengine import MongoEngine
from datetime import datetime

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'frontend',
    'host': 'localhost',
    'port': 27017
}

db = MongoEngine()
db.init_app(app)


class Endpoints(db.Document):
    date_created = db.DateTimeField(default=datetime.now())
    url = db.StringField()
    endpoint = db.StringField()


class Keywords(db.Document):
    crawl_keys = db.DictField()
    recrawl_keys = db.DictField()
    wanted_keys = db.DictField()
    unwanted_keys = db.DictField()


@app.route('/', methods=['GET', 'POST'])
def index():
    endpoints = Endpoints.objects()
    return render_template('index.html', endpoints=endpoints)


@app.route('/crawler.html', methods=['GET', 'POST'])
def crawler():
    keywords = list(Keywords.objects.exclude("id"))[0]["crawl_keys"]
    return render_template('crawler.html', keywords=keywords)


@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(debug=True)
