from flask import render_template

from src.frontend import app


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/errors/page-404.html'), 404


@app.errorhandler(403)
def page_forbidden(e):
    return render_template('/errors/page-403.html'), 403


@app.errorhandler(500)
def page_exception(e):
    return render_template('/errors/page-500.html'), 500
