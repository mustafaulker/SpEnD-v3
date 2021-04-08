from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, current_user, login_required, login_user, UserMixin, logout_user
from flask_mail import Mail, Message
from flask_mongoengine import MongoEngine
from jinja2 import TemplateNotFound
from werkzeug.urls import url_parse

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'frontend',
    'host': 'localhost',
    'port': 27017
}

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='-',
    MAIL_PASSWORD='-',
    MAIL_RECIPIENTS=['-', '-']
)

app.secret_key = 'super_secret_key'

db = MongoEngine()
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)


class Endpoints(db.Document):
    date_created = db.DateTimeField(default=datetime.now())
    url = db.StringField()
    endpoint = db.StringField()


class Keywords(db.Document):
    crawl_keys = db.DictField()
    recrawl_keys = db.DictField()
    wanted_keys = db.DictField()
    unwanted_keys = db.DictField()


class User(UserMixin, db.Document):
    meta = {'collection': 'users'}
    username = db.StringField(unique=True)
    password = db.StringField(default=True)
    active = db.BooleanField(default=True)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        endpoints = Endpoints.objects()
        return render_template('index.html', endpoints=endpoints)
    except TemplateNotFound:
        return render_template('/errors/page-404.html'), 404
    except:
        return render_template('/errors/page-500.html'), 500


@app.route('/crawler', methods=['GET', 'POST'])
def crawler():
    try:
        keywords = list(Keywords.objects.exclude("id"))[0]["crawl_keys"]
        return render_template('crawler.html', keywords=keywords)
    except TemplateNotFound:
        return render_template('/errors/page-404.html'), 404
    except:
        return render_template('/errors/page-500.html'), 500


@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except TemplateNotFound:
        return render_template('/errors/page-404.html'), 404
    except:
        return render_template('/errors/page-500.html'), 500


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    try:
        if request.method == 'POST':
            cont_name = request.form.get('cont_name')
            cont_subject = request.form.get('cont_subject')
            cont_email = request.form.get('cont_email')
            cont_message = request.form.get('cont_message')
            msg = Message(
                subject=cont_subject,
                sender=app.config['MAIL_USERNAME'][0],
                recipients=app.config['MAIL_RECIPIENTS'],
                body=f"""
                      From: {cont_name}
                      Mail: {cont_email}
                      Message: {cont_message}
                      """
            )
            mail.send(msg)
            flash('Your message has been sent successfully.')
            return redirect(url_for("contact"))
        return render_template('contact.html')
    except TemplateNotFound:
        return render_template('/errors/page-404.html'), 404
    except:
        return render_template('/errors/page-500.html'), 500


@app.route('/endpoint/<path:ep_url>', methods=['GET', 'POST'])
def endpoint(ep_url):
    try:
        endpoints = Endpoints.objects()
        return render_template('endpoint.html', ep_url=ep_url, endpoints=endpoints)
    except TemplateNotFound:
        return render_template('/errors/page-404.html'), 404
    except:
        return render_template('/errors/page-500.html'), 500


@app.route('/selectedEndpoint', methods=['GET', 'POST'])
def selectedEndpoint():
    if request.method == 'POST':
        try:
            ep_url = str(list(request.form.values())[0])
            return redirect(url_for('endpoint', ep_url=ep_url))
        except TemplateNotFound:
            return render_template('/errors/page-404.html'), 404
        except:
            return render_template('/errors/page-500.html'), 500


@login_manager.user_loader
def load_user(pk):
    return User.objects.get(pk=pk)


@app.route('/login.html', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        form_username = request.form['username']
        form_password = request.form['userpass']

        user = User.objects(username=form_username).first()

        if user is None or not user.check_password(form_password):
            return redirect(url_for('login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)

    return render_template('/auth/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_authenticated():
        return render_template('index.html')
    return render_template('dashboard.html')


@login_manager.unauthorized_handler
def unauthorized_callback():
    return render_template('/errors/page-403.html'), 403


if __name__ == "__main__":
    app.run(debug=True)
