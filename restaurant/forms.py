from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class BasicRestaurantForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=4, max=20)])
    address = StringField('Address', validators=[DataRequired(), Length(min=8, max=60)])
    opening_hours = StringField('Opening Hours', validators=[DataRequired()])
    cuisine_type = SelectField('Cuisine Type', choices=[('italian', 'Italian'), ('mexican', 'Mexican'), ('indian', 'Indian')])
    location = StringField('Location', validators=[DataRequired()])
    directions = TextAreaField('Directions', validators=[DataRequired()])
    space = TextAreaField('Space', validators=[DataRequired()])
    room_image = TextAreaField('Space', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    firstname = StringField('firstname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    lastname= StringField('lastname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    phoneNumber= IntegerField('phoneNumber',
                           validators=[DataRequired(), Length(min=11, max=15)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    repeat_password = PasswordField('Repeat Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class MenuForm(FlaskForm):
    dish_name = StringField('Dish Name', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[DataRequired()])

class StaffForm(FlaskForm):
    chef_qualification = TextAreaField('Chef Qualification', validators=[DataRequired()])
    chef_experience = TextAreaField('Chef Experience', validators=[DataRequired()])
    service_personnel = TextAreaField('Service Personnel', validators=[DataRequired()])
