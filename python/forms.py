# Explanation: WTForms for user auth, reporting, resources, plans, and safety check-in.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class RegisterForm(FlaskForm):
    # Explanation: Registration form with validation.
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=255)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    phone = StringField("Phone", validators=[Optional(), Length(max=50)])
    address = StringField("Address", validators=[Optional()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    # Explanation: Login form for user/admin.
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class ReportForm(FlaskForm):
    # Explanation: Community report submission.
    disaster_type = SelectField("Disaster Type", choices=[
        ("Typhoon", "Typhoon"), ("Flood", "Flood"), ("Earthquake", "Earthquake"),
        ("Fire", "Fire"), ("Landslide", "Landslide"), ("Other", "Other")
    ], validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired(), Length(max=255)])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Submit Report")

class ResourceForm(FlaskForm):
    # Explanation: Admin resource management.
    name = StringField("Name", validators=[DataRequired(), Length(max=255)])
    category = SelectField("Category", choices=[
        ("Hospital", "Hospital"), ("Evacuation Center", "Evacuation Center"),
        ("Hotline", "Hotline"), ("Police", "Police"), ("Fire Station", "Fire Station"),
        ("Other", "Other")
    ])
    address = TextAreaField("Address", validators=[Optional()])
    contact = StringField("Contact", validators=[Optional(), Length(max=100)])
    latitude = FloatField("Latitude", validators=[Optional()])
    longitude = FloatField("Longitude", validators=[Optional()])
    submit = SubmitField("Save Resource")

class PlanForm(FlaskForm):
    # Explanation: Emergency plan creation.
    household_members = IntegerField("Household Members", validators=[Optional(), NumberRange(min=1)], default=1)
    meeting_point = StringField("Meeting Point", validators=[Optional(), Length(max=255)])
    evacuation_routes = TextAreaField("Evacuation Routes", validators=[Optional()])
    supply_checklist = TextAreaField("Supply Checklist", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Save Plan")

class SafetyForm(FlaskForm):
    # Explanation: Safety check-in status update.
    status = SelectField("Status", choices=[("Safe", "Safe"), ("Needs Help", "Needs Help"), ("Missing", "Missing")], validators=[DataRequired()])
    note = TextAreaField("Note", validators=[Optional()])
    submit = SubmitField("Update Status")
