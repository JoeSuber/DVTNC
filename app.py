from flask import Flask, render_template, json, request
import makedb
from werkzeug.security import generate_password_hash, check_password_hash
mydb = makedb.dvtc_db
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        _badge = request.form['inputName']
        if mydb.find_person(_badge):
            render_template()

    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'
    # the code below is executed if the request method
    # was GET or the credentials were invalid
    return render_template('login.html', error=error)
@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

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
