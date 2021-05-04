from flask import Flask, render_template, request, json, redirect
from flaskext.mysql import MySQL
from flask import session

app = Flask(__name__)
app.secret_key = "key"

mysql = MySQL()

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'officesupply'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 8889
mysql.init_app(app)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/showListing")
def showListing():
    return render_template('listing.html')

@app.route('/searchCategory', methods=["POST"])
def searchCategory():
    try:
        _category = request.form['category']

        # make database connection
        con = mysql.connect()
        cursor = con.cursor()

        # send query to get all of the data for all of todolist item entries
        cursor.execute("SELECT * FROM tbl_products WHERE category = %s", (_category))

        # get results
        data = cursor.fetchall()

        # go through each todolist item entry and turn it into a json object then append it to the list for the json dump
        productInfo = []
        for temp in data:
            neededData = {'id':temp[0], 'name':temp[1], 'price':temp[2], 'inventory':temp[3], 'category':temp[4], 'link':temp[5], 'deleted':temp[6]}
            productInfo.append(neededData)

        return json.dumps(productInfo)


    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/searchItem', methods=["POST"])
def searchItem():
    try:
        _name = request.form['name']

        # make database connection
        con = mysql.connect()
        cursor = con.cursor()

        # send query to get all of the data for all of todolist item entries
        cursor.execute("SELECT * FROM tbl_products WHERE UPPER(name) = UPPER(%s)", (_name))

        # get results
        data = cursor.fetchall()

        # go through each todolist item entry and turn it into a json object then append it to the list for the json dump
        productInfo = []
        for temp in data:
            neededData = {'id':temp[0], 'name':temp[1], 'price':temp[2], 'inventory':temp[3], 'category':temp[4], 'link':temp[5], 'deleted':temp[6]}
            productInfo.append(neededData)

        return json.dumps(productInfo)


    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/showProducts')
def showProducts():
    try:
        # make database connection
        con = mysql.connect()
        cursor = con.cursor()

        # send query to get all of the data for all of todolist item entries
        cursor.execute("SELECT * FROM tbl_products")

        # get results
        data = cursor.fetchall()

        # go through each todolist item entry and turn it into a json object then append it to the list for the json dump
        productInfo = []
        for temp in data:
            neededData = {'id':temp[0], 'name':temp[1], 'price':temp[2], 'inventory':temp[3], 'category':temp[4], 'link':temp[5], 'deleted':temp[6]}
            productInfo.append(neededData)

        return json.dumps(productInfo)


    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

if __name__ == "__main__":
    app.run()
