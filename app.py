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


@app.route('/addToCart', methods=["POST"])
def addToCart():
    try:
        if session.get('user'):
            _itemId = request.json['itemId']
            _quantity = request.json['quantity']
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("INSERT INTO tbl_cart (userId, itemId, quantity) VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE quantity = quantity+%s", (_user , _itemId, _quantity, _quantity))

            conn.commit()

            return json.dumps({'message': 'Inserted Product'})

        else:
            return redirect('/showSignIn')

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/removeFromCart', methods=['DELETE'])
def removeFromCart():
    try:
        if session.get('user'):
            _user = session.get('user')
            _itemId = request.json['itemId']

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM tbl_cart WHERE userId=%s AND itemId=%s", (_user, _itemId))

            data = cursor.fetchall()
            # columns in data is in order : userId, ItemId, quantity, id, name, price, inventory, category, link, deleted

            conn.commit()
            return jsonify(data)

        else:
            return json.dumps({'error': "User not signed in"})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/showCart')
def showCart():
    if session.get('user'):
        return render_template('cart.html')
    else:
        return redirect('/showSignIn')

@app.route('/getCart')
def getCart():
    try:
        if session.get('user'):
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM tbl_cart INNER JOIN tbl_products ON tbl_cart.itemId = tbl_products.id WHERE userId = %s", (_user))

            data = cursor.fetchall()
            # columns in data is in order : userId, ItemId, quantity, id, name, price, inventory, category, link, deleted

            conn.commit()
            return jsonify(data)

        else:
            return json.dumps({'error': "User not signed in"})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()


@app.route('/increaseQuantityInCart', methods=['POST'])
def increaseQuantityInCart():
    try:
        if session.get('user'):
            _user = session.get('user')
            _itemId = request.json['itemId']

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("UPDATE tbl_cart SET quantity = quantity+1 WHERE userId = %s AND itemId = %s AND (SELECT inventory FROM tbl_products WHERE id=%s)>quantity", (_user, _itemId, _itemId))

            data = cursor.rowcount

            if data > 0:
                conn.commit()
                return json.dumps({'message': "update successful"})
            else:
                # Arbitrary error code for "not enough inventory"
                return json.dumps({'error': "36"})

        else:
            return json.dumps({'error': "User not signed in"})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/decreaseQuantityInCart', methods=['POST'])
def decreaseQuantityInCart():
    try:
        if session.get('user'):
            _user = session.get('user')
            _itemId = request.json['itemId']

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("UPDATE tbl_cart SET quantity = quantity-1 WHERE userId = %s AND itemId = %s", (_user, _itemId))

            data = cursor.rowcount

            if data > 0:
                conn.commit()
                return json.dumps({'message': "update successful"})
            else:
                return json.dumps({'error': "Quantity can't be zero"})

        else:
            return json.dumps({'error': "User not signed in"})

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

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

            cursor.execute("SELECT * FROM tbl_history INNER JOIN tbl_products ON tbl_history.itemId = tbl_products.id WHERE userId = %s", (_user))

            data = cursor.fetchall()
            # columns in data is in order : transactionId, userId, itemId, quantity, id, name, price, inventory, category, link, deleted

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