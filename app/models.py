import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
#from sqlalchemy import func, Column, DateTime, ForeignKey, Integer, String, Text, Numeric, text, Float
from flask_login import UserMixin, AnonymousUserMixin
from sqlalchemy.orm import relationship
from . import db, login_manager
from sqlalchemy import func, text


class Permission:
    """
    A specific permission task is given a bit position.  Eight tasks are
    avalible because there are eight bits in a byte.
    """
    FOLLOW = int('00000001', 2)
    COMMENT = int('00000010', 2)
    WRITE_ARTICLES = int('00000100', 2)
    MODERATE_COMMENTS = int('00001000', 2)
    # TASK_TBD = int('00010000', 2)
    # TASK_TBD = int('00100000', 2)
    # TASK_TBD = int('01000000', 2)
    ADMINISTER = int('10000000', 2)  # 0xff


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        """Update or create all Roles."""
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),  # User Role is default
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (int('11111111', 2), False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name
    
    def to_json(self):
        json_record = {
            'id': self.id,
            'name': self.applicant,
            'default': self.recruitment,
            'permissions': self.motivation,
        }
        return json_record

    @staticmethod
    def from_json(json_record):
        id = json_record.get('id')
        name = json_record.get('name')
        default = json_record.get('default')
        permissions = json_record.get('permissions')
        return Role (id = id, name = name, default = default,
            permissions = permissions)



class Branch(db.Model):
    __tablename__ = 'branches'

    id = db.Column(db.Integer, primary_key=True)
    branch_name = db.Column(db.String(45))
    branch_code = db.Column(db.String(45))
    country = db.Column(db.String(45))
    deleted = db.Column(db.Boolean, default=False, index=True)
    
    def to_json(self):
        json = {
            'id':self.id,
            'branch_name':self.branch_name,
            'branch_code':self.branch_code,
            'country':self.country,
            'deleted':self.deleted
        }
        return json
    
    @staticmethod
    def from_json(json):
        return Branch(
            id = json.get('id'),
            branch_name = json.get('branch_name'),
            branch_code = json.get('branch_code'),
            country = json.get('country'),
            deleted = json.get('deleted'))


class Phone(db.Model):
    __tablename__ = 'phones'
    
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.ForeignKey(u'branches.id'), index=True)
    phone_number = db.Column(db.String(45))
    assigned_to = db.Column(db.String(45))
    country = db.Column(db.String(45))
    active = db.Column(db.Boolean, default=False, index=True)
    deleted = db.Column(db.Boolean, default=False, index=True)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow())
    
    def to_json(self):
        json = {
            'id': self.id,
            'branch_id': self.branch_id,
            'phone_number': self.phone_number,
            'assigned_to': self.assigned_to,
            'country': self.country,
            'active': self.active,
            'deleted': self.deleted
        }
        return json
    
    
    @staticmethod
    def from_json(json):
        return Phone(
            id=json.get('id'),
            branch_id=json.get('branch_id'),
            phone_number=json.get('phone_number'),
            assigned_to=json.get('assigned_to'),
            country=json.get('country'),
            active=json.get('active'),
            deleted=json.get('deleted'))


class Queue(db.Model):
    __tablename__ = 'queues'
    
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.ForeignKey(u'branches.id'), index=True,  nullable=True)
    name = db.Column(db.String(45))
    branch_name = db.Column(db.String(45))
    status = db.Column(db.String(45))
    country = db.Column(db.ForeignKey(u'geos.id'), index=True)
    deleted = db.Column(db.Boolean, server_default=text(u'false'),default=False, nullable=False)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow())
    selected = db.Column(db.Boolean, default=False, server_default=text(u'false'), nullable=False)
    completed = db.Column(db.Boolean, default=False, server_default=text(u'false'), nullable=False)
    synced = db.Column(db.Boolean, default=False, server_default=text(u'false'), nullable=False)
    
    branch = relationship(u'Branch')
    geo = relationship(u'Geo')
    
    def to_json(self):
        return {
            'id': self.id,
            'branch_id': self.branch_id,
            'branch_name': self.branch.branch_name if self.branch_id is not None else None,
            'branch': self.branch.to_json() if self.branch_id is not None else None,
            'name': self.name,
            'status': self.status,
            'country': self.geo.geo_code if self.geo is not None else None,
            'deleted': self.deleted,
            'selected': self.selected,
            'completed': self.completed,
            'synced': self.synced,
            'date_added': float(self.date_added.strftime('%s')) if self.date_added is not None else None
        }


class PhoneQueue(db.Model):
    __tablename__ = 'phone_queue'
    
    id = db.Column(db.Integer, primary_key=True)
    branch_id = db.Column(db.ForeignKey(u'branches.id'), index=True, nullable=True)
    queue_id = db.Column(db.ForeignKey(u'queues.id'), index=True)
    phone_number = db.Column(db.String(45))
    assigned_to = db.Column(db.String(45))
    phone_id = db.Column(db.ForeignKey(u'phones.id'), index=True)
    status = db.Column(db.String(45))
    error_message = db.Column(db.String(45))
    country = db.Column(db.String(45))
    sent = db.Column(db.Boolean, default=False)
    deleted = db.Column(db.Boolean, default=False, index=True)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow())
    synced = db.Column(db.Boolean, default=False)
    
    branch = relationship(u'Branch')
    queue = relationship(u'Queue')
    phone = relationship(u'Phone')
    
    def to_json(self):
        json = {
            'id': self.id,
            'branch_id': self.branch_id,
            'branch_name': self.branch.branch_name,
            'phone_number': self.phone_number,
            'status': self.status,
            'queue_id': self.queue_id,
            'country': self.country,
            'error_message': self.error_message,
            'sent': self.sent,
            'assigned_to':self.phone.assigned_to,
            'phone_id':self.phone.id,
            'deleted': self.deleted,
            'synced': self.synced
        }
        return json
    
    @staticmethod
    def from_json(json):
        return PhoneQueue(
            id=json.get('id'),
            branch_id=json.get('branch_id'),
            phone_number=json.get('phone_number'),
            status=json.get('status'),
            error_message=json.get('error_message'),
            country=json.get('country'),
            sent=json.get('sent'),
            deleted=json.get('deleted'))


class UssdMessage(db.Model):
    __tablename__ = 'ussd_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(45))
    message = db.Column(db.Text, nullable=True)
    branch_id = db.Column(db.ForeignKey(u'branches.id'), index=True)
    phone_id = db.Column(db.ForeignKey(u'phones.id'), index=True)
    bundle_balance = db.Column(db.Float, server_default=text("'0'"))
    expiry_datetime = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    message_type_id = db.Column(db.ForeignKey(u'message_types.id'), index=True)
    country = db.Column(db.String(5))
    date_added = db.Column(db.DateTime(), default=datetime.utcnow())
    active = db.Column(db.Boolean, default=False, index=True)
    deleted = db.Column(db.Boolean, default=False, index=True)
    queue_id = db.Column(db.ForeignKey(u'queues.id'), nullable=True)

    queue = relationship(u'Queue')
    
    def to_json(self):
        json = {
            'id': self.id,
            'phone_number': self.phone_number,
            'message': self.message,
            'branch_id': self.branch_id,
            'phone_id': self.phone_id,
            'message_type_id': self.message_type_id,
            'country': self.country,
            'date_added': self.date_added,
            'active': self.active,
            'deleted': self.deleted
        }
        return json
    
    @staticmethod
    def from_json(json):
        return UssdMessage(
            id = json.get('id'),
            phone_number = json.get('phone_number'),
            message = json.get('message'),
            branch_id = json.get('branch_id'),
            phone_id = json.get('phone_id'),
            message_type_id = json.get('message_type_id'),
            country = json.get('country'),
            date_added = json.get('date_added'),
            active = json.get('active'),
            deleted = json.get('deleted')
        )

class MessageType(db.Model):
    __tablename__ = 'message_types'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    status = db.Column(db.Text, nullable=True)
    date_added = db.Column(db.DateTime(), default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, index=True)
    
    def to_json(self):
        return {
            'id':self.id,
            'name':self.name,
            'status':self.status,
            'date_added':self.date_added,
            'deleted':self.deleted
        }
    
    
    @staticmethod
    def from_json(json):
        return MessageType(
            id = json.get('id'),
            name = json.get('name'),
            status = json.get('status'),
            date_added = json.get('date_added'),
            deleted = json.get('deleted')
        )
    
    
class Geo(db.Model):
    __tablename__ = 'geos'
    id = db.Column(db.Integer, primary_key=True)
    geo_name = db.Column(db.String(20), unique=True)
    geo_code = db.Column(db.String(20))
    users = db.relationship('User', backref='geo', lazy='dynamic')
    archived = db.Column(db.Integer, server_default=text("'0'"))
    deleted = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def insert_geos():
        """Update or create all Geos"""
        geos = [{'name':'Kenya', 'code':'KE'},
                {'name':'Uganda', 'code':'UG'}]
        for geo in geos:
            added_geo = Geo.query.filter_by(geo_name=geo['name']).first()
            if added_geo is None:
                geo = Geo(geo_name=geo['name'], geo_code=geo['code'])
            db.session.add(geo)
        db.session.commit()

    def __repr__(self):
        return '<Geo %r>' % self.geo_name
    
    def to_json(self):
        return {
            'id':self.id,
            'geo_name':self.geo_name,
            'geo_code':self.geo_code,
            'users':self.users,
            'archived':self.archived,
            'deleted':self.deleted
        }
    
    @staticmethod
    def from_json(json):
        return Geo(
            id = json.get('id'),
            geo_name = json.get('geo_name'),
            geo_code = json.get('geo_code'),
            users = json.get('users'),
            archived = json.get('archived'),
            deleted = json.get('deleted')
        )


class UserType(db.Model):
    __tablename__ = 'user_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    users = db.relationship('User', backref='user_type', lazy='dynamic')
    deleted = db.Column(db.Boolean, default=False, index=True)

    @staticmethod
    def insert_user_types():
        """Update or create all Geos"""
        types = ['VC BDM',
                 'AI BDM',
                 'VC/AI BDM',
                 'SCR']
        for type in types:
            user_type = UserType.query.filter_by(name=type).first()
            if user_type is None:
                user_type = UserType(name=type)
            db.session.add(user_type)
        db.session.commit()

    def __repr__(self):
        return '<UserType %r>' % self.name
    
    def to_json(self):
        return {
            'id':self.id,
            'name':self.name,
            'deleted':self.deleted
        }
    
    @staticmethod
    def from_json(json):
        return UserType(
            id = json.get('id'),
            name = json.get('name'),
            deleted = json.get('deleted')
        )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())

    # 'default' can take a function so each time a default value needs to be
    # produced, the function is called
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    geo_id = db.Column(db.Integer, db.ForeignKey('geos.id'))
    user_type_id = db.Column(db.Integer, db.ForeignKey('user_types.id'))
    deleted = db.Column(db.Boolean, default=False, index=True)
    

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        # The method seed() sets the integer starting value used in generating
        # random numbers. Call this function before calling any other random
        # module function.
        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            # user might not be random, in which case rollback
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['DASHBOARD_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        """
        Generate a JSON Web Signature token with an expiration.
        """
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)  # commited after end of request
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        # match the security of the client request
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'

        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username
    
    def to_json(self):
        return {
            'id':self.id,
            'email':self.email,
            'username':self.username,
            'role_id':self.role_id,
            #'password_hash':self.password_hash,
            'confirmed':self.confirmed,
            'name':self.name,
            'location':self.location,
            'about_me':self.about_me,
            'member_since':self.member_since,
            'last_seen':self.last_seen,
            'avatar_hash':self.avatar_hash,
            'geo_id':self.geo_id,
            'user_type_id':self.user_type_id,
            'deleted':self.deleted
        }
    
    
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
# Register AnonymousUser as the class assigned to 'current_user' when the user
# is not logged in.  This will enable the app to call 'current_user.can()'
# without having to first check if the user is logged in
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """
    Callback function required by Flask-Login that loads a User, given the
    User identifier.  Returns User object or None.
    """
    return User.query.get(int(user_id))
