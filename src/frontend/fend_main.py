from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from datetime import datetime
from jinja2 import TemplateNotFound

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
    try:
        endpoints = Endpoints.objects()
        return render_template('index.html', endpoints=endpoints)
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500


@app.route('/crawler.html', methods=['GET', 'POST'])
def crawler():
    try:
        keywords = list(Keywords.objects.exclude("id"))[0]["crawl_keys"]
        return render_template('crawler.html', keywords=keywords)
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500


@app.route('/about.html')
def about():
    try:
        return render_template('about.html')
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500


@app.route('/contact.html', methods=['GET', 'POST'])
def contact():
    try:
        if request.method == 'POST':
            form = list(request.form.values())
        return render_template('contact.html')
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500


@app.route('/endpoint/<path:ep_url>', methods=['GET', 'POST'])
def endpoint(ep_url):
    try:
        endpoints = Endpoints.objects()
        return render_template('endpoint.html', ep_url=ep_url, endpoints=endpoints)
    except TemplateNotFound:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500


@app.route('/selectedEndpoint', methods=['GET', 'POST'])
def selectedEndpoint():
    if request.method == 'POST':
        try:
            ep_url = str(list(request.form.values())[0])
            return redirect(url_for('endpoint', ep_url=ep_url))
        except TemplateNotFound:
            return render_template('page-404.html'), 404
        except:
            return render_template('page-500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)
