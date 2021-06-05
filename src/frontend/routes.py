import datetime
from itertools import chain

from bson import ObjectId
from flask import render_template, request, redirect, url_for, flash, abort
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from jinja2 import TemplateNotFound
from werkzeug.urls import url_parse

from src.frontend import app, models, login_manager, mail, recaptcha, search_engine_dict, logger, scheduler
from src.main_crawl import endpoint_crawler
from src.utils.database_controller import Database


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        endpoints = models.Endpoints.objects.filter(tag="approved")
        logger.info(f"{request.remote_addr}")
        return render_template('index.html', endpoints=endpoints)
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
            if request.form.get('cont_subject'):
                flash('Not configured yet, please use GitHub Issues', 'error')
                return redirect(url_for("contact"))
            else:
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
                    flash('Your message has been sent successfully.', 'info')
                    return redirect(url_for("contact"))
                else:
                    flash('Please complete the reCaptcha.', 'error')
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


@login_manager.user_loader
def load_user(pk):
    try:
        return models.User.objects.get(pk=pk)
    except:
        abort(500)


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            form_username = request.form.get('username')
            form_password = request.form.get('userpass')

            user = models.User.objects(username=form_username).first()

            if user is None or not user.check_password(form_password):
                flash('Invalid username or password.', 'error')
                logger.error(f"({request.remote_addr}) - Failed authentication.")
                return redirect(url_for('login'))
            login_user(user)

            logger.info(f"User({request.remote_addr}) has logged-in.")

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('dashboard')
            return redirect(next_page)

        return render_template('./auth/login.html')
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/logout')
def logout():
    try:
        logout_user()
        logger.info(f"User({request.remote_addr}) has logged-out.")
        return redirect(url_for('index'))
    except:
        abort(500)


@app.route('/admin/users/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    try:
        if request.method == 'POST':
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')

            user = models.User.objects(username=current_user.username).first()

            if user is None or not user.check_password(current_password):
                flash('Invalid current password.', 'error')
                logger.error(f"Failed password change attempt: {request.remote_addr}")
                return redirect(url_for('change_password'))

            user.change_pass(new_password)
            user.save()
            flash('Password has changed.', 'info')
            logger.info(f"({request.remote_addr}) has changed the password of {current_user.username}.")

        return render_template('./admin/users/change_password.html',
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@login_manager.unauthorized_handler
def unauthorized_callback():
    return abort(403)


@app.route('/admin/crawl/crawler', methods=['GET', 'POST'])
@login_required
def crawler():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')
        keywords = Database.get_keywords('crawl_keys')

        if request.method == 'POST':
            selected_search_engines = request.form.getlist('cb_se')
            selected_keywords = request.form.getlist('cb_kw')
            keyword_input = set(request.form.get('keyword_input').split("\r\n"))
            inner_crawl = request.form.get('inner_crawl') is not None
            user_inputs = []
            [user_inputs.append(keyword.strip()) for keyword in keyword_input]
            selected_keywords.extend(list(filter(None, user_inputs)))

            # Insert written keyword/s to the DB.
            if '' in keyword_input:
                keyword_input.remove('')
            if keyword_input:
                for key in keyword_input.copy():
                    if key in Database.get_keywords('crawl_keys'):
                        keyword_input.remove(key)
                Database.insert_keyword('crawl_keys', list(keyword_input))

            # SE and KW selection control.
            if not selected_search_engines or not selected_keywords:
                flash('- No SEs or Keywords selected.', 'error')
                return redirect(url_for('crawler'))
            else:
                flash(f'- Selected Search Engines:\n{selected_search_engines}', 'info')
                flash(f'- Selected Keywords:\n{selected_keywords}', 'info')
                flash(f'- Inner Crawl:\n{inner_crawl}', 'info')

            spiders = list(map(search_engine_dict.get, selected_search_engines))

            # Instant crawl button pressed.
            if 'manuel_crawl' in request.form:
                scheduler.add_job(func=endpoint_crawler, args=[spiders, selected_keywords, inner_crawl],
                                  id='manuel_crawl', run_date=datetime.datetime.now())

            # Schedule a crawl button pressed.
            elif 'schedule_crawl' in request.form:
                date, time = request.form.get('schedule_date'), request.form.get('schedule_time')

                if datetime.datetime.fromisoformat(f'{date} {time}') < datetime.datetime.now():
                    flash('- Past date/time selected.', 'error')
                    return redirect(url_for('crawler'))

                scheduler.add_job(func=endpoint_crawler, args=[spiders, selected_keywords, inner_crawl],
                                  id=None, name='schedule_crawl', run_date=f'{date} {time}')

                flash(f'- Crawl will be triggered on '
                      f'{datetime.datetime.strptime(date, "%Y-%m-%d").date().strftime("%d.%m.%y")} at {time}', 'info')

            # Schedule Crawl Interval button pressed.
            elif 'schedule_interval' in request.form:
                interval = request.form.get('crawl_interval')

                scheduler.add_job(func=endpoint_crawler, args=[spiders, selected_keywords, inner_crawl],
                                  id=None, name='interval_crawl', trigger='interval', days=int(interval))
                flash(f'- Crawl will be triggered {interval} days apart', 'info')

            return redirect(url_for('crawler'))
        return render_template('./admin/crawl/crawler.html', s_engines=list(search_engine_dict.keys()), zip=zip,
                               keywords=keywords, pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except ValueError:
        flash('- Invalid date/time.', 'error')
        return redirect(url_for('crawler'))
    except TemplateNotFound:
        abort(404)
    except Exception as e:
        logger.error(f'Err, Crawler. {e}')
        abort(500)


@app.route('/admin/crawl/scheduled_tasks', methods=['GET', 'POST'])
@login_required
def scheduled_tasks():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        tasks = scheduler.get_jobs()

        return render_template('./admin/crawl/scheduled_tasks.html', tasks=tasks,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="approved")
        alive_count = len(models.Endpoints.objects.filter(tag="approved", up_now=True))

        start = datetime.datetime.now()
        last_30 = {'date_alive': {'$gte': (start - datetime.timedelta(30))}}
        last_180 = {'date_alive': {'$gte': (start - datetime.timedelta(180))}}

        alive_30_count = len(models.Endpoints.objects(tag="approved", __raw__=last_30))
        alive_180_count = len(models.Endpoints.objects(tag="approved", __raw__=last_180))

        return render_template('./admin/dashboard.html', endpoints=endpoints, alive_30_count=alive_30_count,
                               alive_180_count=alive_180_count, alive_count=alive_count,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/manage/approved', methods=['GET', 'POST'])
@login_required
def approved():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="approved")

        return render_template('./admin/manage/approved_endpoints.html', endpoints=endpoints,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/manage/pending', methods=['GET', 'POST'])
@login_required
def pending():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="pending")

        return render_template('./admin/manage/pending_endpoints.html', endpoints=endpoints,
                               pending_count=len(endpoints))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/manage/suspended', methods=['GET', 'POST'])
@login_required
def suspended():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="suspended")

        return render_template('./admin/manage/suspended_endpoints.html', endpoints=endpoints,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/manage/removed', methods=['GET', 'POST'])
@login_required
def removed():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        endpoints = models.Endpoints.objects.filter(tag="removed")

        return render_template('./admin/manage/removed_endpoints.html', endpoints=endpoints,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/logs/exceptions', methods=['GET', 'POST'])
@login_required
def log_exceptions():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        logs = sorted(models.Logs.objects.filter(levelname="ERROR"),
                      key=lambda instance: instance.time, reverse=True)

        return render_template('./admin/logs/log_exceptions.html', logs=logs,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/logs/crawler', methods=['GET', 'POST'])
@login_required
def log_crawler():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        logs = sorted(models.Logs.objects.filter(funcName="crawl"),
                      key=lambda instance: instance.time, reverse=True)

        return render_template('./admin/logs/log_crawler.html', logs=logs,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/logs/status', methods=['GET', 'POST'])
@login_required
def log_status():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        logs = sorted(models.Logs.objects.filter(funcName='check_endpoints'),
                      key=lambda instance: instance.time, reverse=True)

        return render_template('./admin/logs/log_status.html', logs=logs,
                               pending_count=len(models.Endpoints.objects.filter(tag='pending')))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/logs/authentications', methods=['GET', 'POST'])
@login_required
def log_authentications():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        logs = sorted(chain(models.Logs.objects.filter(funcName="login"),
                            models.Logs.objects.filter(funcName="logout")),
                      key=lambda instance: instance.time, reverse=True)

        return render_template('./admin/logs/log_authentications.html', logs=logs,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/logs/guests', methods=['GET', 'POST'])
@login_required
def log_guests():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        logs = list(models.Logs.objects.filter(funcName="index").aggregate(
            [{"$sortByCount": "$message"}]))

        return render_template('./admin/logs/log_guests.html', logs=logs,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/keywords/crawl_keys', methods=['GET', 'POST'])
@login_required
def crawl_keys():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        keywords = Database.get_keywords('crawl_keys')

        return render_template('./admin/keywords/crawl_keys.html', keywords=keywords,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/keywords/second_crawl_keys', methods=['GET', 'POST'])
@login_required
def second_crawl_keys():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        keywords = Database.get_keywords('second_crawl_keys')

        return render_template('./admin/keywords/second_crawl_keys.html', keywords=keywords,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/keywords/wanted_keys', methods=['GET', 'POST'])
@login_required
def wanted_keys():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        keywords = Database.get_keywords('wanted_keys')

        return render_template('./admin/keywords/wanted_keys.html', keywords=keywords,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.route('/admin/keywords/unwanted_keys', methods=['GET', 'POST'])
@login_required
def unwanted_keys():
    try:
        if not current_user.is_authenticated():
            return render_template('index.html')

        keywords = Database.get_keywords('unwanted_keys')

        return render_template('./admin/keywords/unwanted_keys.html', keywords=keywords,
                               pending_count=len(models.Endpoints.objects.filter(tag="pending")))
    except TemplateNotFound:
        abort(404)
    except:
        abort(500)


@app.post('/insert_keyword')
@login_required
def insert_keyword():
    try:
        if request.method == 'POST':
            keys = set()
            keyword_textarea = request.form.get('keyword_textarea').split("\r\n")
            [keys.add(keyword.strip()) for keyword in keyword_textarea]

            for key in keys.copy():
                if key in Database.get_keywords(request.referrer.rsplit('/', 1)[-1]):
                    keys.remove(key)

            if '' in keys:
                keys.remove('')

            if not keys:
                flash(f'No Keywords provided.', 'error')
            else:
                Database.insert_keyword(request.referrer.rsplit('/', 1)[-1], list(keys))
                flash(f'Keywords has added.', 'info')
            return redirect(url_for(request.referrer.rsplit('/', 1)[-1]))
    except Exception as e:
        logger.error(f"Err, Insert_Keyword. {e}")
        abort(500)


@app.post('/remove_keyword')
@login_required
def remove_keyword():
    try:
        if request.method == 'POST':
            Database.remove_keyword(request.referrer.rsplit('/', 1)[-1], request.form.get('remove_key'))
            return redirect(url_for(request.referrer.rsplit('/', 1)[-1]))
    except Exception as e:
        logger.error(f'Err, Remove_Keyword. {e}')
        abort(500)


@app.post('/approve')
@login_required
def approve():
    try:
        if request.method == 'POST':
            Database.update_one("endpoints", {"url": request.form.get('approve')}, {"$set": {"tag": "approved"}})
        return redirect(url_for("pending"))
    except Exception as e:
        logger.error(f"Err, Approve_EP. {e}")
        abort(500)


@app.post('/suspend')
@login_required
def suspend():
    try:
        if request.method == 'POST':
            Database.update_one("endpoints", {"url": request.form.get('suspend')}, {"$set": {"tag": "suspended"}})
            return redirect(url_for(request.referrer.rsplit('/', 1)[-1]))
    except Exception as e:
        logger.error(f"Err, Suspend_EP. {e}")
        abort(500)


@app.post('/unsuspend')
@login_required
def unsuspend():
    try:
        if request.method == 'POST':
            Database.update_one("endpoints", {"url": request.form.get('unsuspend')}, {"$set": {"tag": "pending"}})
        return redirect(url_for("suspended"))
    except Exception as e:
        logger.error(f"Err, Unsuspend_EP. {e}")
        abort(500)


@app.post('/remove')
@login_required
def remove():
    try:
        if request.method == 'POST':
            Database.update_one("endpoints", {"url": request.form.get('remove')}, {"$set": {"tag": "removed"}})
            return redirect(url_for(request.referrer.rsplit('/', 1)[-1]))
    except Exception as e:
        logger.error(f"Err, Remove_EP. {e}")
        abort(500)


@app.post('/recover')
@login_required
def recover():
    try:
        if request.method == 'POST':
            Database.update_one("endpoints", {"url": request.form.get('recover')}, {"$set": {"tag": "pending"}})
        return redirect(url_for("removed"))
    except Exception as e:
        logger.error(f"Err, Recover_EP. {e}")
        abort(500)


@app.post('/remove_log')
@login_required
def remove_log():
    try:
        if request.method == 'POST':
            if 'guests' in request.referrer:
                Database.delete_many('logs', {'msg': request.form.get('remove_log')})
                return redirect(url_for("log_guests"))
            else:
                Database.delete_one('logs', {'_id': ObjectId(request.form.get('remove_log'))})
        if 'exceptions' in request.referrer:
            return redirect(url_for('log_exceptions'))
        elif 'crawler' in request.referrer:
            return redirect(url_for('log_crawler'))
        elif 'authentications' in request.referrer:
            return redirect(url_for('log_authentications'))
        elif 'status' in request.referrer:
            return redirect(url_for('log_status'))
    except Exception as e:
        logger.error(f'Err, Remove_Log. {e}')
        abort(500)


@app.post('/remove_logs')
@login_required
def remove_logs():
    try:
        if request.method == 'POST':
            if 'exceptions' in request.referrer:
                Database.delete_many('logs', {'levelname': 'ERROR'})
                return redirect(url_for('log_exceptions'))
            elif 'crawler' in request.referrer:
                Database.delete_many('logs', {'funcName': 'crawler'})
                return redirect(url_for('log_crawler'))
            elif 'authentications' in request.referrer:
                Database.delete_many('logs', {'funcName': {'$in': ["login", "logout"]}})
                return redirect(url_for('log_authentications'))
            elif 'status' in request.referrer:
                Database.delete_many('logs', {'funcName': 'check_endpoints'})
                return redirect(url_for('log_status'))
            elif 'guests' in request.referrer:
                Database.delete_many('logs', {'funcName': 'index'})
                return redirect(url_for('log_guests'))
    except Exception as e:
        logger.error(f'Err, Remove_Logs. {e}')
        abort(500)


@app.post('/remove_task')
@login_required
def remove_task():
    try:
        if request.method == 'POST':
            scheduler.remove_job(request.form.get("remove_task"))
        return redirect(url_for("scheduled_tasks"))
    except Exception as e:
        logger.error(f"Err, Remove_Task. {e}")
        abort(500)


@app.post('/resume_task')
@login_required
def resume_task():
    try:
        if request.method == 'POST':
            scheduler.resume_job(request.form.get('resume_task'))
        return redirect(url_for("scheduled_tasks"))
    except Exception as e:
        logger.error(f"Err, Resume_Task. {e}")
        abort(500)


@app.post('/pause_task')
@login_required
def pause_task():
    try:
        if request.method == 'POST':
            scheduler.pause_job(request.form.get('pause_task'))
        return redirect(url_for("scheduled_tasks"))
    except Exception as e:
        logger.error(f"Err, Pause_Task. {e}")
        abort(500)


@app.post('/postpone_task')
@login_required
def postpone_task():
    try:
        if request.method == 'POST':
            scheduler.modify_job(id=request.form.get("postpone_task"), next_run_time=scheduler.get_job(
                request.form.get("postpone_task")).next_run_time + datetime.timedelta(days=1))
        return redirect(url_for("scheduled_tasks"))
    except Exception as e:
        logger.error(f"Err, Postpone_Task. {e}")
        abort(500)
