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


@app.route('/', methods=['GET', 'POST'])
def index():
    endpoints = Endpoints.objects()
    return render_template('index.html', endpoints=endpoints)


if __name__ == "__main__":
    app.run(debug=True)
