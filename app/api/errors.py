from flask import render_template, jsonify
from . import api



@api.app_errorhandler(404)
def page_not_found(e):
    return jsonify(error='not found'), 404


@api.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
