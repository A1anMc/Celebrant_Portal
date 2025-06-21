from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, DateField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Optional, Length

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])

class CoupleForm(FlaskForm):
    partner1_name = StringField('Partner 1 Name', validators=[DataRequired(), Length(max=100)])
    partner1_email = EmailField('Partner 1 Email', validators=[DataRequired(), Email(), Length(max=120)])
    partner1_phone = TelField('Partner 1 Phone', validators=[Optional(), Length(max=20)])
    
    partner2_name = StringField('Partner 2 Name', validators=[DataRequired(), Length(max=100)])
    partner2_email = EmailField('Partner 2 Email', validators=[DataRequired(), Email(), Length(max=120)])
    partner2_phone = TelField('Partner 2 Phone', validators=[Optional(), Length(max=20)])
    
    ceremony_date = DateField('Ceremony Date', validators=[Optional()])
    ceremony_location = StringField('Ceremony Location', validators=[Optional(), Length(max=200)])
    status = SelectField('Status', 
                        choices=[
                            ('Inquiry', 'Inquiry'),
                            ('Confirmed', 'Confirmed'),
                            ('Completed', 'Completed'),
                            ('Cancelled', 'Cancelled')
                        ],
                        default='Inquiry')
    notes = TextAreaField('Notes', validators=[Optional()])

class CeremonyTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[Optional()])
    content = TextAreaField('Ceremony Content', validators=[DataRequired()])
    ceremony_type = SelectField('Ceremony Type',
                              choices=[
                                  ('Civil', 'Civil'),
                                  ('Religious', 'Religious'),
                                  ('Custom', 'Custom')
                              ],
                              validators=[DataRequired()])
    is_default = BooleanField('Set as default template for this ceremony type') 