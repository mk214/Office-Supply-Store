from flask import Flask, render_template, request, json, redirect
from flaskext.mysql import MySQL
from flask import session, jsonify
import bcrypt

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'officesupply'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3307
mysql.init_app(app)

app.secret_key = 'secret key can be anything!'

@app.route("/")
def main():
    return render_template('index.html')


@app.route('/showSignIn')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']
        _password = _password.encode('utf-8')
        con = mysql.connect()
        cursor = con.cursor()

        cursor.execute("SELECT * FROM tbl_users WHERE email = %s", (_email))

        data = cursor.fetchall()

        if len(data) > 0:
            _encryptPassword = data[0][2]
            _encryptPassword = _encryptPassword.rstrip('\x00')
            _encryptPassword = _encryptPassword.encode('utf-8')

            if bcrypt.checkpw(_password, _encryptPassword):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html', error='Wrong Email address or Password.')
        else:
            return render_template('error.html', error='Wrong Email address or Password.')

    except Exception as e:
        return render_template('error.html', error=str(e))
    finally:
        cursor.close()
        con.close()


@app.route('/showSignUp')
def showSignup():
    return render_template('signup.html')

@app.route('/validateSignUp', methods=["POST"])
def validateSignUp():
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
    _password = _password.encode('utf8')
    _encryptPassword = bcrypt.hashpw(_password, bcrypt.gensalt())

    if _email and _password:
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tbl_user")
        data = cursor.fetchall()
        for user in data:
            if _email == user[1]:
                return json.dumps({'error': "User already exists!"})
        cursor.execute("INSERT INTO tbl_users(email, password) VALUES (%s, %s)", (_email, _encryptPassword))
        data = cursor.fetchall()
        if len(data) == 0:
            conn.commit()
            return json.dumps({'message': 'User created successfully'})
        else:
            return render_template('error.html', error=str(data[0]))
            # return json.dumps({'error': str(data[0])})
    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})


if __name__ == "__main__":
    app.run()