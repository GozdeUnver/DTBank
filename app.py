from flask import Flask, request, render_template, url_for
from flask_mysqldb import MySQL
import hashlib

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'group4'
app.config['MYSQL_DB'] = 'dtbank'
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods = ['POST'])
def login():
    username = request.form['Username']
    #hashed_pw = hashlib.sha256(request.form['Password'].encode()).hexdigest()
    hashed_pw=request.form['Password']
    type = request.form['Type']
    con = mysql.connection
    cur = con.cursor()
    if type == 'Manager':
        cur.execute('SELECT COUNT(1) FROM DatabaseManager DM WHERE DM.username = %s AND DM.password = %s', (username, hashed_pw))
        rc = int(cur.fetchone()[0]) # return code
        con.commit()
        if rc: return render_template('manager.html', username=username)
        return render_template('login_error.html')
    elif type == 'User': 
        cur.execute('SELECT COUNT(1) FROM User U WHERE U.username = %s AND U.password = %s', (username, hashed_pw))
        rc = int(cur.fetchone()[0]) # return code
        con.commit()
        if rc: return render_template('user.html', username=username)
        return render_template('login_error.html')
    else: return render_template('login_error.html')


@app.route('/adduser', methods = ['GET', 'POST'])
def add_user():
    # TODO: Add a check for whether the user is already registered or not
    if request.method == 'GET':
        return render_template('adduser.html')
    else:
        hashed_pw = hashlib.sha256(request.form['Password'].encode()).hexdigest()
        params =  (request.form['Username'], hashed_pw, request.form['Institute'])
        print(params)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO User(username, password, institute) \
            VALUES (%s, %s, %s)", params)
        mysql.connection.commit()
        return render_template('manager.html', added_user=True)

@app.route('/deletedrugs', methods = ['GET', 'POST'])
def delete_drug():
    # TODO: Add a check for whether the user is already registered or not
    if request.method == 'GET':
        return render_template('deletedrugs.html')
    elif request.method == 'POST':
        drugbank_id = request.form['drugid']
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM Drug WHERE drugbank_id = %s", (drugbank_id,))
        cur.execute("SELECT ROW_COUNT()")
        rc = int(cur.fetchone()[0])
        mysql.connection.commit()
        if rc:
            return render_template('deletedrugs.html', success=True)
        else: return render_template('deletedrugs.html', success=False)

@app.route('/drugs',methods=['GET'])
def drugs():
    return render_template('drugsOptions.html')

@app.route('/drugs/<subpath>',methods=['GET','POST'])
def drugsSubpaths(subpath):
    if subpath=='viewDrugs':
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM Drug D,(SELECT drugbank_id,target_name FROM Bindings) T,DrugCausedSideEffect S \
            WHERE D.drugbank_id=S.drugbank_id \
            AND D.drugbank_id=T.drugbank_id")
        table=cur.fetchall()

        # Html daha olmadı
        return render_template('viewDrugs.html',table=table)



if __name__ == "__main__":
    app.run(debug=True)