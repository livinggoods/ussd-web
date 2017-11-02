import flask_admin as admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import filters
from ..models import (User, UssdMessage)

class UssdMessagesAdmin(sqla.ModelView):
  
  column_choices = {
    'name': [
      ('draft', 'Draft'),
      ('completed', 'Completed'),
    ],
    'readonly':[
      ('1', 'True'),
      ('0', 'False'),
    ],
    'country': [
      ('KE', 'Kenya'),
      ('UG', 'Uganda'),
    ]
  }

  def __init__(self, session):
    # Just call parent class with predefined model.
    super(UssdMessagesAdmin, self).__init__(UssdMessage, session)
  
# column_sortable_list = ('title', ('user', 'user.username'), 'date')


class UsersAdmin(sqla.ModelView):
  column_choices = {
    'name': [
      ('draft', 'Draft'),
      ('completed', 'Completed'),
    ],
    'readonly': [
      ('1', 'True'),
      ('0', 'False'),
    ],
    'country': [
      ('KE', 'Kenya'),
      ('UG', 'Uganda'),
    ]
  }
  
  def __init__(self, session):
    # Just call parent class with predefined model.
    super(UsersAdmin, self).__init__(User, session)
    
    # column_sortable_list = ('title', ('user', 'user.username'), 'date')