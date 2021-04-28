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

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

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
                return redirect('/')
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
        cursor.execute("SELECT * FROM tbl_users")
        data = cursor.fetchall()
        for user in data:
            if _email == user[1]:
                return json.dumps({'error': "User already exists!"})
        cursor.execute("INSERT INTO tbl_users(email, password) VALUES (%s, %s)", (_email, _encryptPassword))
        data = cursor.fetchall()
        if len(data) == 0:
            conn.commit()
            return redirect('/')
        else:
            return render_template('error.html', error=str(data[0]))
            # return json.dumps({'error': str(data[0])})
    else:
        return json.dumps({'html':'<span>Enter the required fields</span>'})


@app.route('/showHistory')
def showHistory():
    if session.get('user'):
        return render_template('history.html')
    else:
        return redirect('/showSignIn')

@app.route('/getHistory')
def getHistory():
    try:
        if session.get('user'):
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tbl_history INNER JOIN tbl_products ON tbl_history.productId = tbl_products.id WHERE userId = %s", (_user))

            data = cursor.fetchall()
            # columns in data is in order : transactionId, userId, productId, quantity, id, name, inventory, category, link, deleted

            conn.commit()
            return jsonify(data)

        else:
            return json.dumps({'error': "User not signed in"})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run()