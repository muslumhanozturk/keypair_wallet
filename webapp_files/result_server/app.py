# Import Flask modules
from flask import Flask, request, render_template, session, redirect
from flaskext.mysql import MySQL
import os

VALID_USERNAME = "admin"
VALID_PASSWORD = "admin" 

# Create an object named app
app = Flask(__name__, template_folder='templates', static_folder='static')

app.secret_key = os.getenv('MYSQL_PASSWORD')

# Configure mysql database
app.config['MYSQL_DATABASE_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('MYSQL_DATABASE')
app.config['MYSQL_DATABASE_USER'] = os.getenv('MYSQL_USER')
#app.config['MYSQL_DATABASE_PORT'] = 3306
mysql = MySQL()
mysql.init_app(app) 
connection = mysql.connect()
connection.autocommit(True) 
cursor = connection.cursor()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html', error=None) 

@app.before_request
def before_request():
    if not session.get('logged_in') and request.endpoint in ['add_record', 'update_record', 'delete_record', 'find_records']:
        return redirect('/login')

def find_persons(keyword):
    query = f"""
    SELECT * FROM keypair WHERE name like '%{keyword.strip().lower()}%';
    """
    cursor.execute(query)
    result = cursor.fetchall()
    persons =[{'id':row[0], 'name':row[1].strip().title(), 'number':row[2]} for row in result]
    if len(persons) == 0:
        persons = [{'name':'No Result', 'number':'No Result'}]
    return persons 

@app.route('/', methods=['GET', 'POST'])
def find_records():
    if request.method == 'POST':
        keyword = request.form['username']
        persons = find_persons(keyword)
        return render_template('index.html', persons=persons, keyword=keyword, show_result=True, developer_name='M.Han')
    else:
        return render_template('index.html', show_result=False, developer_name='M.Han')

if __name__== '__main__':
       #app.run(debug=True)
    app.run(host='0.0.0.0', port=80)