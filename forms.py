# forms.py

from wtforms import Form, StringField, SelectField


class UserSearchForm(Form):
    choices =  [('first_name', 'first name'),
                ('last_name', 'last name'),
                ('email', 'email')]
    select = SelectField('Search for user:', choices=choices)
    search = StringField('')