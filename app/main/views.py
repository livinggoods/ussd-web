from flask import (render_template, redirect, url_for, flash, request, abort, session,
                   Response, current_app, jsonify)
from flask_login import current_user, login_required
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, UploadForm, QueueForm
from .. import db
from ..models import (Phone, Role, User, Geo, UserType, Branch, PhoneQueue, Queue, UssdMessage)
from ..decorators import admin_required, permission_required
from werkzeug.utils import secure_filename
import os
import io
import flask_excel as excel
from flask import Response
from ..utils import process_phone_csv
import json



@main.route('/', methods=['GET', 'POST'])
def index():
    # if current_user.is_anonymous():
    #     return redirect(url_for('auth.login'))
    # else:
    #     pass
    form = UploadForm()
    if request.method =="POST":
        if form.validate_on_submit():
            f = form.file_field.data
            filename = secure_filename(f.filename)
            
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'data', filename)
            f.save(path)
            data = process_phone_csv(path)
            for chp_phone in data:
              #   get the Branch ID
              branch = Branch.query.filter_by(branch_name=chp_phone.get('branch_name')).first()
              if branch is None:
                branch = Branch(
                  branch_name =chp_phone.get('branch_name'),
                  country = 'UG'
                )
                db.session.add(branch)
                db.session.commit()
              # create the phone
              phone = Phone.query.filter_by(branch_id=branch.id, phone_number=chp_phone.get('phone')).first()
              if phone is None:
                phone = Phone(
                    branch_id=branch.id,
                    phone_number=chp_phone.get('phone'),
                    assigned_to=chp_phone.get('name'),
                    country='UG')
                db.session.add(phone)
            return jsonify(data=process_phone_csv(path))
        else:
            return jsonify(filename='none')
    return render_template('index.html', form = form)

# @api.route('/phone-queue/<int:id>', methods=['GET', 'POST'])
# @api.route('/phone-queue', methods=['POST', 'GET'])
# #@login_required
# def phone_queue(id=None):

@main.route('/phone_queues/<int:id>')
@main.route('/phone_queues')
def phone_queue(id=None):
    if id is not None:
      queues = PhoneQueue.query.filter_by(deleted=False, queue_id=id).all()
    else:
      queues = PhoneQueue.query.filter_by(deleted=False).all()
    return render_template('phone_queues.html', queues=queues,
                           title="Phone Queues", subtitle="")


@main.route('/phone_queues/new', methods=['GET', 'POST'])
def new_phone_queue():
    form = QueueForm()
    if form.validate_on_submit():
      # create a queue
      queue = Queue(
        branch_id = form.branch_id.data if form.branch_id.data != -1 else None,
        name = form.queue_name.data,
        status = form.status.data,
        country = form.country.data,
      )
      db.session.add(queue)
      db.session.commit()
      session['branch'] = form.branch_id.data if form.branch_id.data != -1 else None
      if form.all_phones_included.data == 1:
        # if Branch is selected, only include phone numbers for that Branch
        if form.branch_id.data != -1:
          phones = Phone.query.filter_by(deleted=False, branch_id=form.branch_id.data).all()
        else:
          phones = Phone.query.filter_by(deleted=False).all()
        for phone in phones:
          phone_queue = PhoneQueue(
            country = form.country.data,
            branch_id=form.branch_id.data,
            queue_id=queue.id,
            phone_number=phone.phone_number,
            assigned_to=phone.assigned_to,
            phone_id=phone.id,
            sent=False
          )
          db.session.add(phone_queue)
        db.session.commit()
        return redirect(url_for('main.phone_queue'))
      else:
        return redirect('/phone_queues/new/'+str(queue.id))
    return render_template('new_phone_queues.html', form=form,
                           title="New Phone Queue", subtitle="")

@main.route('/phone_queues/new/<int:id>', methods=['GET', 'POST'])
def select_phones_queue(id):
    if request.method=="POST":
      selected_phones=request.form.getlist('phones[]')
      queue= request.form.get('queue')
      for p in selected_phones:
        phone = Phone.query.filter_by(id=p).first()
        phone_queue = PhoneQueue(
            country = phone.country,
            branch_id = phone.branch_id,
            queue_id = queue,
            phone_number = phone.phone_number,
            assigned_to = phone.assigned_to,
            phone_id = phone.id,
            sent = False,
            deleted = False
        )
        db.session.add(phone_queue)
        db.session.commit()
      return jsonify(data={'queue':queue, 'phone':selected_phones})

    branch = session.get('branch', None)
    if branch is not None:
      phones = Phone.query.filter_by(deleted=False, branch_id=branch).all()
    else:
      phones = Phone.query.filter_by(deleted=False).all()
    return render_template('new_queue_phone_selection.html', phones=phones,
                           title="New Phone Queue", subtitle="", queue=id)

@main.route('/queues')
def queue():
    queues = Queue.query.filter_by(deleted=False).all()
    return render_template('queues.html', queues=queues, title="Queues")

@main.route('/bundle-balance/<int:queue_id>')
def get_bundle_balance(queue_id):
  dest = io.StringIO()
  data = []
  balances = UssdMessage.query.filter_by(queue_id=queue_id).all()
  queue_name = Queue.query.filter_by(id=queue_id).first()
  header = ['Name', 'Phone', 'Balance (in Mbs)', 'Expiry']
  data.append(header)
  for msg in balances:
    queue = PhoneQueue.query.filter_by(id=msg.id).first()
    row = [queue.assigned_to, queue.phone_number, msg.bundle_balance, msg.expiry_datetime]
    data.append(row)
  output = excel.make_response_from_array(data, 'csv')
  output.headers["Content-Disposition"] = "attachment; filename="+queue_name.name+".csv"
  output.headers["Content-type"] = "text/csv"
  return output


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.outerjoin(Geo).outerjoin(UserType)\
        .with_entities(User, Geo, UserType)\
        .filter(User.username==username).first_or_404()
    return render_template('user.html')


@main.route('/users/<username>')
@login_required
def users(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.', 'error')
        return redirect(url_for('main.index'))

    # get request arguments
    followed = request.args.get('followed', 1, type=int)

    return render_template('user_list.html', user=user)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # change values based on form input
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        current_user.geo = Geo.query.get(form.geo.data)
        current_user.user_type = UserType.query.get(form.user_type.data)
        db.session.add(current_user)
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('main.user', username=current_user.username))
    # set inital values
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    form.geo.data = current_user.geo_id
    form.user_type.data = current_user.user_type_id
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.geo = Geo.query.get(form.geo.data)
        user.user_type = UserType.query.get(form.user_type.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.', 'success')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.geo.data = user.geo_id
    form.user_type.data = user.user_type_id
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)
