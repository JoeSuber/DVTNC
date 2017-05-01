''' some help with wtforms and flask-wtf:   
https://www.youtube.com/watch?v=eu0tg4vgFr4

Build a User Login System With Flask-Login, Flask-WTForms, Flask-Bootstrap, and Flask-SQLAlchemy:  
https://www.youtube.com/watch?v=8aTnmsDMldY
'''

from flask import Flask, render_template, json, request
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

__dbfn__ = "DVTCinventory"
__sqlext__ = '.sqlite'
__sql_inventory_fn__ = os.getcwd() + os.sep + __dbfn__ + __sqlext__
print("Database file located at: {}".format(__sql_inventory_fn__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+__sql_inventory_fn__
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

# starting place. Asks for badge, finds a user from db or sends them to /showSignUp
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        _badge = request.form['inputBadge']
        user = Person.query.filter_by(badge_id=_badge).first()
        print("user = {}".format(user))
        if not user:    # badge isn't in the database
            return render_template('/showSignUp', badge=_badge)
        else:   # user exists
            return render_template('/checkMEID', user=user)

    return render_template('index.html')

# gets a user, collects an MEID, querry db to see if user owns MEID, calls giveaway() or takein()
@app.route('/checkMEID', methods=['GET', 'POST'])
def checkmeid(user):
    if request.method == 'POST':
        _meid = request.form['inputMEID']
        device = mydb.find_device(_meid)
        if not device:
            return render_template('/createDevice', user=user, meid=_meid)
        else: # device exists
            if mydb.owner_of_device(user, _meid):
                return render_template('/transferTo', user=user, meid=_meid)
            else:
                return render_template('/receiveFrom', user=user, meid=_meid)

    return render_template('/checkMEID')

# present and update the columns required to add a device to inventory
@app.route('/createDevice', methods=['GET', 'POST'])
def create_device(user, meid):
    keys = [k for k in mydb.show_columns("INVENTORY") if k is not "MEID"]
    if request.method == 'POST':
        answers = [request.form[a] for a in keys]   # this assumes the keys can be generated in the form
        answers.append(meid)
        keys.append("MEID")
        entry = {k:v for k, v in zip(keys, answers)}
        mydb.add_data(entry, "INVENTORY", key_column="MEID")
        render_template('/checkMeid', user=user)    # go back to meid entry screen

    return render_template('/createDevice', keys=keys, meid=meid)     # GET just shows the blanks

# show signup will require password data that only admins possess
@app.route('/showSignUp', methods=['GET', 'POST'])
def showSignUp(badge):
    keys = [k for k in mydb.show_columns("PEOPLE") if k is not "BadgeID"]
    if request.method == 'POST':
        answers = [request.form[a] for a in keys]   # this assumes the keys can be generated in the form
        answers.append(badge)
        keys.append("BadgeID")
        entry = {k:v for k, v in zip(keys, answers)}
        mydb.add_data(entry, "PEOPLE", key_column="BadgeID")

    return render_template('/showSignUp', keys=keys, badge=badge)   # GET just shows the blanks

@app.route('/transferTo')
def giveaway(user, meid):
    pass

@app.route('/receiveFrom')
def takefrom(user, meid):
    pass
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
"""
if __name__ == "__main__":
    app.run(port=5002, debug=True)
