from flask import Flask, render_template, request, json, redirect
from flaskext.mysql import MySQL
from flask import session, jsonify
import bcrypt
from random import randrange

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'officesupply'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 8889
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

@app.route('/checkout', methods=["POST"])
def checkout():
    try:
        if session.get('user'):
            _user = session.get('user')

            conn = mysql.connect()
            cursor = conn.cursor()

            # Move all items in cart to checkout
            cursor.execute("INSERT INTO tbl_history (userId, itemId, quantity) SELECT * FROM tbl_cart WHERE userId=%s", (_user ))
            conn.commit()

            # Update inventory of products at checkout
            cursor.execute("SELECT quantity,itemId FROM tbl_cart WHERE userId = %s",_user)
            data = cursor.fetchall()
            conn.commit()

            sql = "UPDATE tbl_products SET inventory = inventory-%s WHERE id=%s"
            cursor.executemany(sql, data)
            conn.commit()

            # Clear cart
            cursor.execute("DELETE FROM tbl_cart WHERE userId=%s",(_user))
            conn.commit()

            return json.dumps({'message': 'Transaction Successful'})

        else:
            return redirect('/showSignIn')

    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/addToCart', methods=["POST"])
def addToCart():
    try:
        if session.get('user'):
            _itemId = request.json['productId']
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

@app.route('/adminDashboard')
def showAdminDashboard():
    try:
        if session.get('user'):
            # VERIFY the user is admin
            _user_id = session.get('user')
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM tbl_users WHERE id = {0}".format(_user_id))
            data = cursor.fetchall()
            user_name = data[0][0]
          
            if user_name != "admin@gmail.com":
                return render_template('index.html') 

           
            #Get all products whre deleted is 1 (true)??
            cursor.execute("SELECT * FROM tbl_products WHERE deleted = 0")

            data = cursor.fetchall()

            product_ids = []
            name_list = []
            price_list = []
            inventory_list = []
            category_list = []
            link_list = []
            deleted_list = []

            for li in data:
                product_ids.append(str(li[0]))
                name_list.append(str(li[1]))
                price_list.append(str(li[2]))
                inventory_list.append(str(li[3]))
                category_list.append(str(li[4]))
                link_list.append(str(li[5]))
                # deleted_list.append(str(li[6]))

            return render_template('admin.html', product_ids = product_ids, name_list = name_list, price_list = price_list, inventory_list = inventory_list, category_list = category_list, link_list=link_list) 
        else:
            return render_template('index.html')
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        cursor.close()
        conn.close()

@app.route('/deleteProduct/<product_id>', methods=['GET', 'POST'])
def delItem(product_id):
    try:
        if session.get('user'):
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("UPDATE tbl_products SET deleted=%s WHERE id = %s", (1, product_id))

            # cursor.execute("DELETE FROM tbl_products WHERE id = {0}".format(product_id))
            conn.commit()
            return redirect('/adminDashboard')
            
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route('/showAddProduct')
def showAddItem():
    return render_template('addProduct.html')

@app.route('/addProduct', methods=['POST'])
def addItem():
    try:
        if session.get('user'):
            _title = request.form['inputName']
            _price = request.form['inputPrice']
            _inventory= request.form['inputInventory']
            _category = request.form['inputCategory']
            _link = request.form['inputLink']
            _product_id = randrange(1,100000)
            
            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("INSERT INTO tbl_products(id,name, price, inventory, category, link, deleted) VALUES (%s, %s, %s, %s, %s, %s, %s)", (_product_id,_title, _price, _inventory, _category, _link, 0))

            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                # return json.dumps({'message':'Todo item created successfully'})
                return redirect('/adminDashboard')
            else:
                return render_template('error.html', error='An error occured!')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()


@app.route('/showEditProduct/<product_id>')
def showEditItem(product_id):
    if session.get('user'):
        conn = mysql.connect()
        cursor = conn.cursor()
        _user = session.get('user')
        cursor.execute("SELECT * FROM tbl_products WHERE id = {0}".format(product_id))
        data = cursor.fetchall()

        return render_template('editProduct.html', data=data[0])
    else:
        return render_template('error.html',error = 'Unauthorized Access')


@app.route('/editProduct/<product_id>', methods=['POST'])
def editProduct(product_id):
    try:
        if session.get('user'):
            _title = request.form['inputName']
            _price = request.form['inputPrice']
            _inventory= request.form['inputInventory']
            _category = request.form['inputCategory']
            _link = request.form['inputLink']

            conn = mysql.connect()
            cursor = conn.cursor()

            cursor.execute("UPDATE tbl_products SET name=%s, price=%s, inventory=%s, category=%s, link=%s WHERE id = %s", (_title, _price, _inventory, _category, _link, product_id))
            conn.commit()

            return redirect('/adminDashboard')
        else:
                return render_template('error.html', error='An error occured!')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        conn.close()



if __name__ == "__main__":
    app.run()