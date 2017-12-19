from flask_wtf import Form
from flask_wtf.file import FileField, FileRequired
from wtforms import (StringField, TextAreaField, BooleanField, SelectField, SubmitField, ValidationError)
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User, Geo, UserType, Branch


class EditProfileForm(Form):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    geo = SelectField('Geo', coerce=int)  # 'coerce': store values as ints
    user_type = SelectField('User Type', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        # set the choices for the role dropdown list
        # give as a list of tuples, with each tuple consisting of two values:
        # and identifier of the item and the text to show in the control
        self.geo.choices = [(geo.id, geo.geo_name)
                             for geo in Geo.query.order_by(Geo.geo_name).all()]
        self.geo.choices.insert(0, (-1, ''))

        self.user_type.choices = \
            [(utype.id, utype.name)
             for utype in UserType.query.order_by(UserType.name).all()]
        self.user_type.choices.insert(0, (-1, ''))


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)  # 'coerce': store values as ints
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    geo = SelectField('Geo', coerce=int)  # 'coerce': store values as ints
    user_type = SelectField('User Type', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # set the choices for the role dropdown list
        # give as a list of tuples, with each tuple consisting of two values:
        # and identifier of the item and the text to show in the control
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]

        self.geo.choices = [(geo.id, geo.geo_name)
                             for geo in Geo.query.order_by(Geo.geo_name).all()]
        self.geo.choices.insert(0, (-1, ''))

        self.user_type.choices = \
            [(utype.id, utype.name)
             for utype in UserType.query.order_by(UserType.name).all()]
        self.user_type.choices.insert(0, (-1, ''))

        self.user = user

    def validate_email(self, field):
        """
        Check if a change was made and ensure the new email does not already
        exist.
        """
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """
        Check if a change was made and ensure the new username does not already
        exist.
        """
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(Form):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')


class UploadForm(Form):
    file_field = FileField("Upload Excel Doc?", validators=[FileRequired()])
    # file_field = FileField()
    submit = SubmitField('Submit')
    
    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)


class QueueForm(Form):
    queue_name = StringField('Queue Name', validators=[Length(0, 64), DataRequired()])
    branch_id = SelectField('Branch', coerce=int)
    status = StringField('Status', validators=[Length(0, 64)])
    country = SelectField('Country', coerce=int)
    all_phones_included = SelectField('Include All numbers', coerce=int)
    submit = SubmitField('Submit')
    
    def __init__(self, *args, **kwargs):
        super(QueueForm, self).__init__(*args, **kwargs)
        self.country.choices = [(geo.id, geo.geo_name)
                             for geo in Geo.query.order_by(Geo.geo_name).all()]
        self.country.choices.insert(0, (-1, ''))
        self.branch_id.choices = [(branch.id, branch.branch_name) for branch in Branch.query.order_by(Branch.branch_name).all()]
        self.branch_id.choices.insert(0, (-1, ''))

        self.all_phones_included.choices = [(1, 'Yes'), (0, 'No')]