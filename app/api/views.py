from . import api
from flask_login import login_required, current_user
from flask import Response, jsonify, request, make_response
from .. models import (MessageType, UssdMessage, Branch, Phone, PhoneQueue, Queue, Geo)
import json
from .. import db
from datetime import datetime



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


@api.route('/phone-queue/<int:id>', methods=['GET', 'POST'])
@api.route('/phone-queue', methods=['POST', 'GET'])
#@login_required
def phone_queue(id=None):
    if id is not None:
        queue = PhoneQueue.query.filter_by(deleted=False, sent=False, queue_id=id).all()
    else:
        queue = PhoneQueue.query.filter_by(deleted=False, sent=False).all()
    return jsonify({'queue': [phone.to_json() for phone in queue]})


@api.route('/phone-queue/received', methods=['GET', 'POST'])
@api.route('/phone-queue/<int:id>/received', methods=['GET', 'POST'])
#@login_required
def phone_queue_received(id=None):
    if request.method == "POST":
        if id is not None:
            queue = PhoneQueue.query.filter_by(deleted=False, id=id).first()
            queue.sent=True
            db.session.add(queue)
            db.session.commit()
            return jsonify(status=queue.to_json())
        else:
            if request.json:
                received_phones = request.json.get('phones')
                updated_phones =[]
                for q in received_phones:
                    # country is a string
                    saved_record = PhoneQueue.query.filter_by(id=q.get('id')).first()
                    saved_record.sent = True
                    db.session.add(saved_record)
                    db.session.commit()
                    updated_phones.append(saved_record.to_json())
                return jsonify({'updated': updated_phones})
            else:
                return jsonify({'error': "no data found"})
            return jsonify({'error': "queue-id is required"})
    else:
        return make_response(jsonify(error="method not allowed"), 405)

@api.route('/queue', methods=['POST', 'GET'])
#@login_required
def get_queues():
    queue = Queue.query.filter_by(selected=False, deleted=False).all()
    return jsonify({'queue': [q.to_json() for q in queue]})


@api.route('/selectedqueues', methods=['POST', 'GET'])
#@login_required
def get_selectedqueues():
    if request.method == "GET":
        queue = Queue.query.filter_by(deleted=False).all()
        return jsonify({'queue': [q.to_json() for q in queue]})
    else:
        selected_queues =request.json.get('queue')
        for q in selected_queues:
            # country is a string
            saved_record = Queue.query.filter_by(id=q.get('id')).first()
            saved_record.selected = q.get('selected')
            db.session.add(saved_record)
            db.session.commit()
        return jsonify(status='ok')

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
    if request.method == "GET":
        messa = UssdMessage.query.filter_by(deleted=False).all()
        return Response(json.dumps(messa, indent=4), mimetype='application/json')
    else:
        messages = request.json.get('messages')
        saved_messages = []
        for message in messages:
            #message is a dictionary
            text_msg = message.get('message')
            #Split this guy by space
            text_msg = text_msg.replace('is being ', '')
            details = text_msg.split(" ")
            mb = details[details.index('is')+1]
            expiry = details[details.index('on')+1]
            expiry = expiry[:-1] + " " + details[details.index('until')+1]
            ph = Phone.query.filter_by(phone_number=message.get('phone_number')).first()
            # Check if the ussdmessage exists, so that we do not add it.
            ussd = UssdMessage.query.filter_by(phone_number=message.get('phone_number'),
                                               queue_id=message.get('queue_id')
                                               if message.get('queue_id') != '' else None).first()
            if not ussd:
                ussd = UssdMessage(
                    phone_number=message.get('phone_number'),
                    message = message.get('message'),
                    branch_id = ph.branch_id,
                    phone_id =ph.id,
                    queue_id =message.get('queue_id') if message.get('queue_id') != '' else None,
                    bundle_balance = mb,
                    expiry_datetime = datetime.strptime(expiry, '%d-%m-%Y %H:%M'),
                    country = ph.country,
                )
            # Save
            db.session.add(ussd)
            db.session.commit()
            saved_messages.append(ussd.to_json())
        return jsonify(messages=saved_messages)