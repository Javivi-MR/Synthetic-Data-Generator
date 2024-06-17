from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from models import User, db

class Register(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder": "username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "password"})

    submit = SubmitField('SignUp')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Choose a different one.')

class Login(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    username = StringField('username', validators=[InputRequired(), Length(min=2, max=50)], render_kw={"placeholder": "username"})
    password = PasswordField('password', validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "password"})

    submit = SubmitField('LogIn')