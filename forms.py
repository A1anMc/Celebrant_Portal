from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, TelField, DateField, TextAreaField, SelectField, BooleanField, PasswordField, DateTimeField
from wtforms.validators import DataRequired, Email, Optional, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

class CoupleForm(FlaskForm):
    partner1_name = StringField('Partner 1 Name', validators=[DataRequired(), Length(max=100)])
    partner1_email = StringField('Partner 1 Email', validators=[DataRequired(), Email(), Length(max=120)])
    partner1_phone = StringField('Partner 1 Phone', validators=[Optional(), Length(max=20)])
    
    partner2_name = StringField('Partner 2 Name', validators=[DataRequired(), Length(max=100)])
    partner2_email = StringField('Partner 2 Email', validators=[DataRequired(), Email(), Length(max=120)])
    partner2_phone = StringField('Partner 2 Phone', validators=[Optional(), Length(max=20)])
    
    ceremony_date = DateTimeField('Ceremony Date', format='%Y-%m-%d', validators=[Optional()])
    ceremony_location = StringField('Ceremony Location', validators=[Optional(), Length(max=200)])
    status = SelectField('Status',
                        choices=[
                            ('Inquiry', 'Inquiry'),
                            ('Confirmed', 'Confirmed'),
                            ('Completed', 'Completed'),
                            ('Cancelled', 'Cancelled')
                        ],
                        validators=[DataRequired()])
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
    template_file = FileField('Upload Template File', 
                            validators=[
                                Optional(),
                                FileAllowed(['txt', 'docx', 'doc'], 'Please upload a document file (TXT, DOC, DOCX)')
                            ])


class LegalFormUploadForm(FlaskForm):
    """Form for couples to upload legal documents."""
    file = FileField('Legal Form Document', 
                    validators=[
                        FileRequired('Please select a file to upload'),
                        FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 
                                  'Please upload a PDF, image (JPG/PNG), or document file')
                    ])
    submitted_by = StringField('Submitted By', 
                             validators=[DataRequired(), Length(max=100)],
                             render_kw={'placeholder': 'Enter your full name'})


class FormValidationForm(FlaskForm):
    """Form for celebrants to validate submitted legal forms."""
    is_valid = BooleanField('Form is valid and complete')
    validation_notes = TextAreaField('Validation Notes', 
                                   validators=[Optional(), Length(max=1000)],
                                   render_kw={'placeholder': 'Enter any notes about the form validation...'})


class LegalFormRequirementForm(FlaskForm):
    """Form for setting up legal form requirements for a couple."""
    form_type = SelectField('Form Type',
                          choices=[
                              ('noim', 'Notice of Intended Marriage (NOIM)'),
                              ('declaration', 'Declaration of No Impediment'),
                              ('divorce_certificate', 'Divorce Certificate'),
                              ('death_certificate', 'Death Certificate')
                          ],
                          validators=[DataRequired()])
    is_required = BooleanField('This form is required for this couple')
    custom_deadline = DateField('Custom Deadline (optional)', 
                              validators=[Optional()],
                              render_kw={'type': 'date'})
    notes = TextAreaField('Special Instructions', 
                         validators=[Optional(), Length(max=500)],
                         render_kw={'placeholder': 'Any special instructions for this form...'}) 