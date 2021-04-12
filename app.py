from flask import Flask, render_template, request, json, redirect
from flaskext.mysql import MySQL
from flask import session, jsonify

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

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin', methods=['POST'])
def validateLogin():
    try:
        _email = request.form['inputEmail']
        _password = request.form['inputPassword']

        con = mysql.connect()
        cursor = con.cursor()

        cursor.execute("SELECT * FROM tbl_users WHERE email = %s", (_email))

        data = cursor.fetchall()

        if len(data) > 0:
            if str(data[0][2]) == _password:
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


if __name__ == "__main__":
    app.run()