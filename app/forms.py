# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, StringField, SubmitField, RadioField, SelectField, BooleanField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from app.models import users


class signIn(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me', default=False)
    signInBtn = SubmitField('Sign In')


class register(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    reg = SubmitField('Register')

    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    def validate_username(self, username):
        usr = users.query.filter_by(username=username.data).first()
        if usr is not None:
            raise ValidationError('This username already exists! Please choose another.')

    def validate_email(self, email):
        user = users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Account with this email already exists!')


class admin_register(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    isAdmin = BooleanField('User is administrator?')
    reg = SubmitField('Register')

    # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
    def validate_username(self, username):
        usr = users.query.filter_by(username=username.data).first()
        if usr is not None:
            raise ValidationError('This username already exists! Please choose another.')

    def validate_email(self, email):
        user = users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Account with this email already exists!')


class admin_settings(FlaskForm):
    existing_Username = None
    existing_Email = None
    # Radio buttons for if the user can feed the bird, or view the bird (tuple format: ['value', 'label']
    canFeed = RadioField(' can feed bird', choices=[('True', 'Yes'), ('False', 'No')], validators=[DataRequired()],
                         default=True)
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    newPassword = PasswordField('New Password')
    newPassword2 = PasswordField('Repeat Password', validators=[EqualTo('newPassword')])
    apply = SubmitField('Apply Settings')

    # Existing username and email are passed from routes. Validation only fails if you changed the username or email...
    # To another user's email or uname, not if you didn't change yours at all
    def validate_username(self, username):
        usr = users.query.filter_by(username=username.data).first()
        if usr is not None and usr.username is not self.existing_Username:
            raise ValidationError('This username already exists! Please choose another.')

    def validate_email(self, email):
        email = users.query.filter_by(email=email.data).first()
        if email is not None and email.email is not self.existing_Email:
            raise ValidationError('Account with this email already exists!')


class user_settings(FlaskForm):
    existing_Username = None
    existing_Email = None
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    currentPassword = PasswordField('Current Password')
    newPassword = PasswordField('New Password')
    newPassword2 = PasswordField('Repeat New Password', validators=[EqualTo('newPassword')])
    # Dropdown box for the theme selector
    themes = SelectField('Birdbox Theme',
                         choices=(['light', 'Light Theme'], ['dark', 'Dark Theme'], ['contrast', 'High Contrast']))
    apply = SubmitField('Apply Settings')

    # Existing username and email are passed from routes. Validation only fails if you changed the username or email...
    # To another user's email or uname, not if you didn't change yours at all
    def validate_username(self, username):
        usr = users.query.filter_by(username=username.data).first()
        if usr is not None and usr.username is not self.existing_Username:
            raise ValidationError('This username already exists! Please choose another.')

    def validate_email(self, email):
        email = users.query.filter_by(email=email.data).first()
        if email is not None and email.email is not self.existing_Email:
            raise ValidationError('Account with this email already exists!')


class feed_schedule(FlaskForm):
    # Checkbox for turning on scheduled feed
    scheduledFeed = BooleanField('Enable Scheduled Feeding?')
    # Checkboxes for each day
    feedDay_Monday = BooleanField('Monday')
    feedDay_Tuesday = BooleanField('Tuesday')
    feedDay_Wednesday = BooleanField('Wednesday')
    feedDay_Thursday = BooleanField('Thursday')
    feedDay_Friday = BooleanField('Friday')
    feedDay_Saturday = BooleanField('Saturday')
    feedDay_Sunday = BooleanField('Sunday')
    # Dropdown box for each hour of the day. Stored in military time in the DB
    feedHour = SelectField('Hour', choices=(['00', '12 AM'], ['01', '1 AM'], ['02', '2 AM'], ['03', '3 AM'], ['04', '4 AM'],
                                            ['05', '5 AM'], ['06', '6 AM'], ['07', '7 AM'], ['08', '8 AM'], ['09', '9 AM'],
                                            ['10', '10 AM'], ['11', '11 AM'], ['12', '12 PM'], ['13', '1 PM'],
                                            ['14', '2 PM'], ['15', '3 PM'], ['16', '4 PM'], ['17', '5 PM'], ['18', ' 6 PM'],
                                            ['19', '7 PM'], ['20', '8 PM'], ['21', '9 PM'], ['22', '10 PM'],
                                            ['23', '11 PM']))
    # Associated minute for the hour
    feedMinute = SelectField('Minute', choices=(['00', '00'], ['05', '05'], ['10', '10'], ['15', '15'], ['20', '20'],
                                                ['25', '25'], ['30', '30'], ['35', '35'],
                                                ['40', '40'], ['45', '45'], ['50', '50'], ['55', '55']))
    apply = SubmitField('Apply Settings')


class theme_settings(FlaskForm):
    # Dropdown box for the theme selector
    themes = SelectField('Birdbox Theme',
                         choices=(['light', 'Light Theme'], ['dark', 'Dark Theme'], ['contrast', 'High Contrast']))
    apply = SubmitField('Apply Theme')
