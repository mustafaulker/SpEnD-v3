from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from jinja2 import TemplateNotFound
from werkzeug.urls import url_parse

from src.frontend import app, models, login_manager, mail, recaptcha


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        endpoints = models.Endpoints.objects()
        return render_template('index.html', endpoints=endpoints)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/crawler', methods=['GET', 'POST'])
def crawler():
    try:
        keywords = list(models.Keywords.objects.exclude("id"))[0]["crawl_keys"]
        if request.method == 'POST':
            return redirect(url_for("crawler", keywords=keywords))
        return render_template('crawler.html', keywords=keywords)
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
        endpoints = models.Endpoints.objects()
        return render_template('endpoint.html', ep_url=ep_url, endpoints=endpoints)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/selectedEndpoint', methods=['GET', 'POST'])
def selectedEndpoint():
    if request.method == 'POST':
        try:
            ep_url = str(list(request.form.values())[0])
            return redirect(url_for('endpoint', ep_url=ep_url))
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


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        new_endpoints = models.NewEndpoints.objects()
        if not current_user.is_authenticated():
            return render_template('index.html')
        return render_template('/admin/dashboard.html', new_endpoints=new_endpoints)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/pending', methods=['GET', 'POST'])
@login_required
def pending():
    try:
        new_endpoints = models.NewEndpoints.objects()
        if not current_user.is_authenticated():
            return render_template('index.html')
        return render_template('/admin/pending_endpoints.html', new_endpoints=new_endpoints)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/suspended', methods=['GET', 'POST'])
@login_required
def suspended():
    try:
        new_endpoints = models.NewEndpoints.objects()
        if not current_user.is_authenticated():
            return render_template('index.html')
        return render_template('/admin/suspended_endpoints.html', new_endpoints=new_endpoints)
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return abort(403)
