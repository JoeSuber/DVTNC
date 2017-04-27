from flask import Flask, render_template, json, request
import makedb
from werkzeug.security import generate_password_hash, check_password_hash
mydb = makedb.dvtc_db
app = Flask(__name__)


# starting place. Asks for badge, finds a user from db or sends them to /showSignUp
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        _badge = request.form['inputBadge']
        user = mydb.find_person(_badge)
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

    return render_template('/createDevice', keys=keys)     # GET just shows the blanks

# show signup will require password data that only admins possess
@app.route('/showSignUp', methods=['GET', 'POST'])
def showSignUp(badge):
    keys = [k for k in mydb.show_columns("PEOPLE") if k is not "BadgeID"]
    if request.method == 'POST'
        answers = [request.form[a] for a in keys]   # this assumes the keys can be generated in the form
        answers.append(badge)
        keys.append("BadgeID")
        entry = {k:v for k, v in zip(keys, answers)}
        mydb.add_data(entry, "PEOPLE", key_column="BadgeID")

    return render_template('/showSignUp', keys=keys)   # GET just shows the blanks

# show
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
