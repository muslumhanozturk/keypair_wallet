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
project_db = os.getenv('MYSQL_DATABASE')
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
    if not session.get('logged_in') and request.endpoint in ['add_record', 'update_record', 'delete_record']:
        return redirect('/login')

def init_keypair_db():
    keypair_table = """
    CREATE TABLE IF NOT EXISTS """+ project_db +""".keypair(
    id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL, 
    number VARCHAR(3000) NOT NULL,
    PRIMARY KEY (id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    cursor.execute(keypair_table) 

def insert_person(name, number):
    query = f"""
    SELECT * FROM keypair WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is not None:
        return f'Person with name {row[1].title()} already exits.'

    insert = f"""
    INSERT INTO keypair (name, number)
    VALUES ('{name.strip().lower()}', '{number}');
    """
    cursor.execute(insert)
    result = cursor.fetchall()
    return f'Person {name.strip().title()} added to keypair successfully'

def update_person(name, number):
    query = f"""
    SELECT * FROM keypair WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return f'Person with name {name.strip().title()} does not exist.'
        
    update = f"""
    UPDATE keypair
    SET name='{row[1]}', number = '{number}'
    WHERE id= {row[0]};
    """
    cursor.execute(update)

    return f'keypair record of {name.strip().title()} is updated successfully'

def delete_person(name):
    query = f"""
    SELECT * FROM keypair WHERE name like '{name.strip().lower()}';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return f'Person with name {name.strip().title()} does not exist, no need to delete.'

    delete = f"""
    DELETE FROM keypair
    WHERE id= {row[0]};
    """
    cursor.execute(delete)
    return f'keypair record of {name.strip().title()} is deleted from the keypair successfully'

@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, action_name='save', developer_name='M.Han')
        
        keypair_number = request.form['keypairnumber']
        if keypair_number is None or keypair_number.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Keypair number can not be empty', show_result=False, action_name='save', developer_name='M.Han')

        result = insert_person(name, keypair_number)
        return render_template('add-update.html', show_result=True, result=result, not_valid=False, action_name='save', developer_name='M.Han')
    else:
        return render_template('add-update.html', show_result=False, not_valid=False, action_name='save', developer_name='M.Han')

@app.route('/update', methods=['GET', 'POST'])
def update_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, action_name='update', developer_name='M.Han')
        keypair_number = request.form['keypairnumber']
        if keypair_number is None or keypair_number.strip() == "":
            return render_template('add-update.html', not_valid=True, message='Invalid input: keypair number can not be empty', show_result=False, action_name='update', developer_name='M.Han')
        elif not keypair_number.isdecimal():
            return render_template('add-update.html', not_valid=True, message='Invalid input: keypair number should be in numeric format', show_result=False, action_name='update', developer_name='M.Han')

        result = update_person(name, keypair_number)
        return render_template('add-update.html', show_result=True, result=result, not_valid=False, action_name='update', developer_name='M.Han')
    else:
        return render_template('add-update.html', show_result=False, not_valid=False, action_name='update', developer_name='M.Han')

@app.route('/delete', methods=['GET', 'POST'])
def delete_record():
    if request.method == 'POST':
        name = request.form['username']
        if name is None or name.strip() == "":
            return render_template('delete.html', not_valid=True, message='Invalid input: Name can not be empty', show_result=False, developer_name='M.Han')
        result = delete_person(name)
        return render_template('delete.html', show_result=True, result=result, not_valid=False, developer_name='M.Han')
    else:
        return render_template('delete.html', show_result=False, not_valid=False, developer_name='M.Han')

@app.route('/', methods=['GET', 'POST'])
def find_records():
    return render_template('index.html', show_result=False, developer_name='MHan')

if __name__== '__main__':
    init_keypair_db()
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=80) 
