import datetime

from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from jinja2 import TemplateNotFound
from werkzeug.urls import url_parse

from src.frontend import app, models, login_manager, mail, recaptcha, search_engine_dict
from src.main_crawl import endpoint_crawler
from src.utils.database_controller import Database


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        endpoints = models.Endpoints.objects.filter(tag="approved")
        return render_template('index.html', endpoints=endpoints)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/crawler', methods=['GET', 'POST'])
def crawler():
    try:
        keywords = Database.get_keywords("crawl_keys")
        if request.method == 'POST':
            selected_search_engines = request.form.getlist("cb_se")
            selected_keywords = request.form.getlist("cb_kw")
            keyword_input = request.form.get("keyword_input").split("\r\n")
            user_inputs = []
            [user_inputs.append(keyword.strip()) for keyword in keyword_input]
            selected_keywords.extend(list(filter(None, user_inputs)))

            flash(f"Selected Search Engines: {selected_search_engines}")
            flash(f"Selected Keywords: {selected_keywords}")

            spiders = list(map(search_engine_dict.get, selected_search_engines))

            endpoint_crawler(spiders=spiders, query=selected_keywords)

            return redirect(url_for("crawler", keywords=keywords, s_engines=list(search_engine_dict.keys())))
        return render_template('crawler.html', keywords=keywords, s_engines=list(search_engine_dict.keys()))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    try:
        if request.method == 'POST':
            if recaptcha.verify():
                cont_name = request.form.get('cont_name')
                cont_subject = request.form.get('cont_subject')
                cont_email = request.form.get('cont_email')
                cont_message = request.form.get('cont_message')
                msg = Message(
                    subject=cont_subject,
                    sender=app.config['MAIL_USERNAME'][0],
                    recipients=app.config['MAIL_RECIPIENTS'],
                    body=f"""
                                      From: {cont_name} \n
                                      Mail: {cont_email} \n
                                      Message: {cont_message} \n
                                      """
                )
                mail.send(msg)
                flash('Your message has been sent successfully.')
                return redirect(url_for("contact"))
            else:
                flash('Please complete the reCaptcha.')
        return render_template('contact.html')
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/endpoint/<path:ep_url>', methods=['GET', 'POST'])
def endpoint(ep_url):
    try:
        selected_endpoint = models.Endpoints.objects(url=ep_url).first()
        return render_template('endpoint.html', ep_url=ep_url, endpoint=selected_endpoint)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/selectedEndpoint', methods=['GET', 'POST'])
def selectedEndpoint():
    if request.method == 'POST':
        try:
            endpoint_url = request.form.get('inspect')
            return redirect(url_for('endpoint', ep_url=endpoint_url))
        except TemplateNotFound:
            abort(404)
        except:
            abort(500)


@login_manager.user_loader
def load_user(pk):
    return models.User.objects.get(pk=pk)


@app.route('/login', methods=('GET', 'POST'))
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            form_username = request.form['username']
            form_password = request.form['userpass']

            user = models.User.objects(username=form_username).first()

            if user is None or not user.check_password(form_password):
                flash('Invalid username or password.')
                return redirect(url_for('login'))
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)

        return render_template('/auth/login.html')
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/logout')
def logout():
    try:
        logout_user()
        return redirect(url_for('index'))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return abort(403)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="approved")
        alive_count = len(models.Endpoints.objects.filter(tag="approved", up_now=True))
        pending_count = len(models.Endpoints.objects.filter(tag="pending"))

        start = datetime.datetime.now()
        ago_30 = (start - datetime.timedelta(30))
        ago_180 = (start - datetime.timedelta(180))

        last_30 = {'date_alive': {'$gte': ago_30}}
        last_180 = {'date_alive': {'$gte': ago_180}}

        alive_30_count = len(models.Endpoints.objects(tag="approved", __raw__=last_30))
        alive_180_count = len(models.Endpoints.objects(tag="approved", __raw__=last_180))

        return render_template('/admin/dashboard.html', endpoints=endpoints, pending_count=pending_count,
                               alive_30_count=alive_30_count, alive_180_count=alive_180_count, alive_count=alive_count)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/pending', methods=['GET', 'POST'])
@login_required
def pending():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="pending")

        return render_template('/admin/pending_endpoints.html', endpoints=endpoints, pending_count=len(endpoints))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/suspended', methods=['GET', 'POST'])
@login_required
def suspended():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="suspended")
        pending_count = len(models.Endpoints.objects.filter(tag="pending"))

        return render_template('/admin/suspended_endpoints.html', endpoints=endpoints, pending_count=pending_count)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/approve', methods=['GET', 'POST'])
@login_required
def approve():
    if request.method == 'POST':
        Database.update("endpoints", {"url": request.form.get('approve')}, {"$set": {"tag": "approved"}})
    return redirect(url_for("pending"))


@app.route('/suspend', methods=['GET', 'POST'])
@login_required
def suspend():
    if request.method == 'POST':
        Database.update("endpoints", {"url": request.form.get('suspend')}, {"$set": {"tag": "suspended"}})
    if request.referrer.endswith("dashboard"):
        return redirect(url_for("dashboard"))
    if request.referrer.endswith("pending"):
        return redirect(url_for("pending"))


@app.route('/unsuspend', methods=['GET', 'POST'])
@login_required
def unsuspend():
    if request.method == 'POST':
        Database.update("endpoints", {"url": request.form.get('unsuspend')}, {"$set": {"tag": "pending"}})
    return redirect(url_for("suspended"))


@app.route('/remove', methods=['GET', 'POST'])
@login_required
def remove():
    if request.method == 'POST':
        Database.update("endpoints", {"url": request.form.get('remove')}, {"$set": {"tag": "removed"}})
    if request.referrer.endswith("dashboard"):
        return redirect(url_for("dashboard"))
    elif request.referrer.endswith("pending"):
        return redirect(url_for("pending"))
    elif request.referrer.endswith("suspended"):
        return redirect(url_for("suspended"))
