from flask import render_template, request

from src.frontend import app, logger


@app.errorhandler(404)
def page_not_found(e):
    logger.error(f"404, Page: {request.url}, IP:{request.remote_addr}")
    return render_template('/errors/page-404.html'), 404


@app.errorhandler(403)
def page_forbidden(e):
    logger.error(f"403, Page: {request.url}, IP:{request.remote_addr}")
    return render_template('/errors/page-403.html'), 403


@app.errorhandler(405)
def method_not_allowed(e):
    logger.error(f"405, Page: {request.url}, IP:{request.remote_addr}")
    return '405 - Method not allowed. Please let us know about this situation at Github Issues.', 405


@app.errorhandler(500)
def page_exception(e):
    logger.error(f"500, Page: {request.url}, IP:{request.remote_addr}")
    return render_template('/errors/page-500.html'), 500
