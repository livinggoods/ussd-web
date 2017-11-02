from . import api
from flask_login import login_required, current_user
from flask import Response, jsonify
from .. models import (MessageType, UssdMessage, Branch, Phone, PhoneQueue)
import json



@api.route('/run', methods=['POST', 'GET'])
#@login_required
def run():
    messa = UssdMessage.query.filter_by(deleted=False).all()
    return Response(json.dumps(messa, indent=4), mimetype='application/json')

@api.route('/branches', methods=['POST', 'GET'])
#@login_required
def branches():
    branches = Branch.query.filter_by(deleted=False).all()
    return jsonify({'branches': [branch.to_json() for branch in branches]})

@api.route('/geos', methods=['POST', 'GET'])
#@login_required
def geos():
    geos = UssdMessage.query.filter_by(deleted=False).all()
    return jsonify({'geos': [geo.to_json() for geo in geos]})


@api.route('/message_types', methods=['POST', 'GET'])
#@login_required
def message_types():
    messa = UssdMessage.query.filter_by(deleted=False).all()
    return Response(json.dumps(messa, indent=4), mimetype='application/json')

@api.route('/phones', methods=['POST', 'GET'])
#@login_required
def phones():
    phones = Phone.query.filter_by(deleted=False).all()
    return jsonify({'phones': [phone.to_json() for phone in phones]})

@api.route('/phone-queue', methods=['POST', 'GET'])
#@login_required
def phone_queue():
    queue = PhoneQueue.query.filter_by(deleted=False).all()
    return jsonify({'queue': [phone.to_json() for phone in queue]})

@api.route('/roles', methods=['POST', 'GET'])
#@login_required
def roles():
    messa = UssdMessage.query.filter_by(deleted=False).all()
    return Response(json.dumps(messa, indent=4), mimetype='application/json')

@api.route('/user_types', methods=['POST', 'GET'])
#@login_required
def user_types():
    messa = UssdMessage.query.filter_by(deleted=False).all()
    return Response(json.dumps(messa, indent=4), mimetype='application/json')

@api.route('/users', methods=['POST', 'GET'])
#@login_required
def users():
    messa = UssdMessage.query.filter_by(deleted=False).all()
    return Response(json.dumps(messa, indent=4), mimetype='application/json')

@api.route('/ussd_messages', methods=['POST', 'GET'])
#@login_required
def ussd_messages():
    messa = UssdMessage.query.filter_by(deleted=False).all()
    return Response(json.dumps(messa, indent=4), mimetype='application/json')