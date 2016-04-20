# -*- coding: utf-8 -*-
from flask import Flask, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import FieldList
from wtforms import Form as NoCsrfForm
from wtforms.fields import StringField, FormField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
db = SQLAlchemy(app)

# - - - Models - - -
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(40))
    age = db.Column(db.String(10))
    organisation = db.Column(db.String(50))
    contact_postion = db.Column(db.String(50))
    hours_of_service = db.Column(db.String(10))
    phones = db.relationship('Phone')
    addresses = db.relationship('Address')
    emails = db.relationship('Email_Address')
    # this 'phones' match names with the form 'phones' or populate_obj fails


class Phone(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    phone_number = db.Column(db.String(50))
    phone_TTD_number = db.Column(db.String(50))
    phone_fax_number = db.Column(db.String(50))

class Address(db.Model):
    __tablename__ = 'addresses'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    addr_name = db.Column(db.String(50))
    city_name = db.Column(db.String(50))
    state_name = db.Column(db.String(50))
    country_name = db.Column(db.String(50))

class Email_Address(db.Model):
    __tablename__ = 'email_addresses'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
    email_addr_name = db.Column(db.String(50))



# - - - Forms - - -
class PhoneForm(NoCsrfForm):
    # this forms is never exposed so we can user the non CSRF version
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    phone_TTD_number = StringField('Phone TTD Number')
    phone_fax_number = StringField('Phone Facsimile Number')

class AddressForm(NoCsrfForm):
    # this forms is never exposed so we can user the non CSRF version
    addr_name = StringField('Address Line 1', validators=[DataRequired()])
    city_name = StringField('City')
    state_name = StringField('State/Province')
    country_name = StringField('Country')

class EmailAddressForm(NoCsrfForm):
    # this forms is never exposed so we can user the non CSRF version
    email_addr_name = StringField('Email Address Line 1', validators=[DataRequired()])


class CombinedForm(Form):
    username = StringField('User', validators=[DataRequired()])
    age = StringField('Age', validators=[DataRequired()])
    organisation =StringField('Organisation', validators=[DataRequired()])
    contact_position = StringField('Contact_position', validators=[DataRequired()])
    hours_of_service = StringField('Hours_of_service', validators=[DataRequired()])
    # we must provide empth Phone() instances else populate_obj will fail
    phones = FieldList(FormField(PhoneForm, default=lambda: Phone()))
    addresses = FieldList(FormField(AddressForm, default=lambda: Address()))
    emails = FieldList(FormField(EmailAddressForm, default=lambda: Email_Address()))
    submit = SubmitField('Submit')


# - - - Routes - - -
@app.route('/', methods=['GET', 'POST'])
def index():
    # always "blindly" load the user
    user = User.query.first()

    # if User has no phones, provide an empty one so table is rendered
    if len(user.phones) == 0:
        user.phones = [Phone(phone_number="example")]
        #flash("empty Phone provided")

    if len(user.addresses) == 0:
        user.addresses = [Address(addr_name = "example")]
        #flash("empty Address provided")
    # else: forms loaded through db relation
    if len(user.emails) == 0:
        user.emails = [Email_Address(email_addr_name = "example")]


    form = CombinedForm(obj=user)

    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        flash("Saved Changes")
    return render_template('multi.html', form=form)


# - - - Execute - - -
def prep_db():
    db.drop_all()
    db.create_all()
    db.session.add(User(username='User 1'))
    db.session.commit()

if __name__ == '__main__':
    prep_db()
    app.run(debug=True, port=5000)
