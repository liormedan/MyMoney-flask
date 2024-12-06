from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('כתובת אימייל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמה', validators=[DataRequired()])
    remember_me = BooleanField('זכור אותי')
    submit = SubmitField('התחבר')

class RegistrationForm(FlaskForm):
    username = StringField('שם משתמש', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('כתובת אימייל', validators=[DataRequired(), Email()])
    password = PasswordField('סיסמה', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('אימות סיסמה', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('שם פרטי', validators=[DataRequired()])
    last_name = StringField('שם משפחה', validators=[DataRequired()])
    submit = SubmitField('הרשם')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('שם המשתמש כבר קיים במערכת')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('כתובת האימייל כבר קיימת במערכת')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('כתובת אימייל', validators=[DataRequired(), Email()])
    submit = SubmitField('בקש איפוס סיסמה')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('סיסמה חדשה', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('אימות סיסמה', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('איפוס סיסמה')
