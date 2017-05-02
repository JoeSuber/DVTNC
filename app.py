''' some help with wtforms and flask-wtf:   
https://www.youtube.com/watch?v=eu0tg4vgFr4

Build a User Login System With Flask-Login, Flask-WTForms, Flask-Bootstrap, and Flask-SQLAlchemy:  
https://www.youtube.com/watch?v=8aTnmsDMldY
'''

from flask import Flask, render_template, json, request, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

__dbfn__ = "DVTCinventory"
__sqlext__ = '.sqlite'
__sql_inventory_fn__ = os.getcwd() + os.sep + __dbfn__ + __sqlext__
print("Database file located at: {}".format(__sql_inventory_fn__))

app = Flask(__name__)
app.secret_key = 'development key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+__sql_inventory_fn__
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Person(db.Model):
    __tablename__ = "people"
    badge_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(55), index=True)
    department = db.Column(db.String(30))

    def __init__(self, badge, name, dept):
        self.badge_id = badge
        self.name = name
        self.department = dept

    def __repr__(self):
        print("<Person %r>" % self.badge_id)

class Phone(db.Model):
    """  will add relations to Person http://flask-sqlalchemy.pocoo.org/2.1/quickstart/"""
    __tablename__ = "devices"
    MEID = db.Column(db.String(28), primary_key=True)
    OEM = db.Column(db.String(50))
    SKU = db.Column(db.String(50))
    IMEI = db.Column(db.String(50))
    MODEL = db.Column(db.String(50))
    Hardware_Type = db.Column(db.String(50))
    In_Date = db.Column(db.String(50))
    Out_Date = db.Column(db.String(50))
    Archived = db.Column(db.String(50))
    TesterName = db.Column(db.String(50))
    DVT_Admin = db.Column(db.String(50))
    Serial_Number = db.Column(db.String(50))
    MSLPC = db.Column(db.String(50))
    Comment = db.Column(db.String(255))

    def __init__(self, meid):
        self.meid = meid

    def __repr__(self):
        print("<Phone %r" % self.meid)

db.create_all()

###### Flask Forms ########
class BadgeForm(FlaskForm):
    badge_id = StringField("Badge Barcode",[DataRequired("Please enter your Badge code.")])
    #submit = SubmitField("Submit")

class PersonForm(FlaskForm):
    badge_id = StringField("Badge Barcode",[DataRequired("Required badge barcode ID")])
    name = StringField("Your Name", [DataRequired("Your real name")])
    department = StringField("Department", [DataRequired("Your division or job area")])

class DeviceForm(FlaskForm):
    MEID = IntegerField("MEID barcode", [DataRequired("Required device ID")])
    OEM = StringField("OEM")
    SKU = StringField("SKU")
    IMEI = StringField("IMEI")
    MODEL = StringField("MODEL")
    Hardware_Type = StringField("Hardware Type")
    In_Date = StringField("In Date")
    Out_Date = StringField("Out Date")
    Archived = StringField("Archived")
    TesterName = StringField("Tester Name")
    DVT_Admin = StringField("DVT Admin")
    Serial_Number = StringField("Serial Number")
    MSLPC = StringField("MSLPC")
    Comment = StringField("Comment")

class MeidForm(FlaskForm):
    meid = IntegerField("MEID barcode", [DataRequired("Please input an existing device")])

class TargetPerson(FlaskForm):
    badge_id = StringField("Badge Barcode",[DataRequired("Required badge barcode ID")])

#######   end Forms  ##############

# starting place. Asks for badge, finds a user from db or sends them to /showSignUp
@app.route('/', methods=['GET', 'POST'])
def main():
    _badge = BadgeForm()
    if _badge.validate_on_submit():
        existing = Person.query.filter_by(badge_id=_badge.data['badge_id'])
        if not existing:  # badge isn't in the database
            return render_template(url_for('create_person'), badge=_badge.data['badge_id'])
        else:           # user exists, continue on to device entry screen
            return render_template(url_for('checkmeid'), user=_badge)
    return render_template('idx.html', form=_badge)     # 'GET'

# add a person to Persons table
@app.route('/create_persion.html', methods=['GET', 'POST'])
def create_person(badge=None):
    person = PersonForm()   #todo figure out how to pass in badge and show it on POST
    if request.method == 'POST':
        pass
    return render_template('/create_person.html', form=person)

# gets a user, collects an MEID, querry db to see if user owns MEID, calls giveaway() or takein()
@app.route('/checkMEID.html', methods=['GET', 'POST'])
def checkmeid(user=None):
    if user is None:
        raise Exception("checkmeid must have a 'user' form")
    _meid = MeidForm()
    if request.method == 'POST':
        device = Phone.query.filter_by(MEID=_meid.data['meid'])
        print("device = {}".format(device))
        if not device:
            return redirect(url_for('create_device', user=user, meid=_meid))
        else: # device exists
            if Phone.query.filter_by(MEID=_meid.data['TesterName']) == user.data['name']:
                return redirect(url_for('giveaway'), user=user, meid=_meid)
            else:
                return redirect(url_for('takefrom'), user=user, meid=_meid)

    return render_template('/checkMEID.html', form=_meid)

# add a device to inventory
@app.route('/createDevice.html', methods=['GET', 'POST'])
def create_device(user=None, meid=None):
    device = DeviceForm()
    if request.method == 'POST':
        pass    # send form contents to db
        redirect(url_for('checkmeid'), user = user)  # go back to meid entry screen

    return render_template('/createDevice.html', form=device)

def swap(current_owner, device, target_owner):
    return True

# ask for the destination Person and transfer device
@app.route('/giveaway.html')
def giveaway(user, meid):
    target = TargetPerson()
    if request.method == 'POST':
        redirect(url_for('success'), user, meid, target)
        swap(user, meid, target)
    return render_template('/giveaway.html', form=target)

@app.route('/takefrom.html')
def takefrom(user, meid):
    target = TargetPerson()
    if request.method == 'POST':
        redirect(url_for('success'), user, meid, target)
        swap(user, meid, target)
    return render_template('/takefrom.html', form=target)

@app.route('/success.html')
def success(use, meid, target):

"""
@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        _badge = request.form['inputName']

        _username = request.form['inputEmail']
        _department = request.form['inputPassword']
        # validate the received values
        if _badge:
            
            # do some db
            _hashed_name = generate_password_hash(_badge)
            data = mydb.checkname(_badge)
            # data = cursor.fetchall()

            if len(data) is 0:
                # do stuff here to add data to database
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})
    finally:
        cursor.close() 
        conn.close()


device42 = Phone(MEID = '99000751003652',
               OEM = 'Motorolla',
               SKU = 'Moto',
               IMEI = '990007510036524',
               MODEL = 'SUX-9000',
               Hardware_Type = "Phone",
               In_Date = "September 11, 2001",
               Out_Date = "12/12/12",
               Archived = "",
               TesterName = "Joe Schmo",
               DVT_Admin = "Ivana Hugenkiss",
               Serial_Number = "1234567",
               MSLPC = "",
                Comment = "I am the very model")

realperson = Person(badge_id = 1234,
                name = 'Joe Schmo',
                department = 'Gnomes of Zurich')
"""
if __name__ == "__main__":
    app.run(port=5002, debug=True)
