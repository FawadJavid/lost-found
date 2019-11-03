from flask import Flask,request,session,redirect,render_template
from flask_mysqldb import MySQL
import yaml
import os


app=Flask(__name__)

#database Configuration
db=yaml.load(open('db.yaml'))
app.config['MYSQL_HOST']= db['mysql_host']
app.config['MYSQL_USER']= db['mysql_user']
app.config['MYSQL_PASSWORD']= db['mysql_password']
app.config['MYSQL_DB']= db['mysql_db']

mysql=MySQL(app)



@app.route('/')
def index():
    return '<h1><center>Welcome to Lost and Found</center></h1><br><br><br>' \
           '<h1>Routes:</h1><br>' \
           '<h4>localhost:5000/register?username=(your username)&password=(your password)</h4>'' \
           ''<h4>localhost:5000/signIn?(your username)&password=(your password)</h4>'

@app.route('/home')
def home():
    if 'name' in session:
        return '<h1><center>Welcome '+session['name']+' to Lost and Found</center></h1>' \
               '<br><br><br>'' \
               ''<h1>Routes:</h1><br>localhost:5000/home/add'
    else:
        return "</h1>Login First</h1>"


@app.route('/register')
def register():
    username=request.args.get('username')
    password=request.args.get('password')
    cur=mysql.connection.cursor()
    cur.execute("INSERT INTO USER(username,password) VALUES(%s, %s)",(username,password))
    mysql.connection.commit()
    cur.close()
    return username+'! You are Successfully Registered'

@app.route('/login')
def login():
    username=request.args.get('username')
    #password=request.args.get('password')
    cur=mysql.connection.cursor()
    cur.execute("""SELECT * FROM USER WHERE username = %s""", (username,))
    user=cur.fetchone()
    cur.close()
    if user is None:
        return "<center><h1 style='color:red;'>!!! wrong username or password !!!</h1></center>"
    else:
        session['name']=user[0]
        return redirect('/home')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/home/add',methods=['GET','POST'])
def add():
    if 'name' in session:
    #getting file and saving it
        render_template('form.html')
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        target=os.path.join(dir_path,'images/')
        if not os.path.isdir(target):
            os.mkdir(target,mode=0o777)

        file=request.files["file"]
        filename=file.filename
        destination="/".join([target,filename])
        file.save(destination)

        #getting remaining data from the form
        item_name=request.form['item_name']
        location=request.form['location']
        descrip=request.form['descrip']
        datee=request.form['datee']

        #sending the data to db
        cur=mysql.connection.cursor()
        query="""INSERT INTO LOSTFOUND(item_name,location,descrip,datee,picture) VALUES(%s, %s, %s, %s, %s)"""
        data=(item_name, location, descrip, datee, destination)
        cur.execute(query, data)
        mysql.connection.commit()
        cur.close()

        return '<h1><center>Welcome ' + session['name'] + ' to Lost and Found</center></h1>' \
               '<br><h1>report registered<br>Go back to home: localhost:5000/home</h1> '
    else:
        return "</h1>Login First</h1>"

@app.route('/home/delete')
def delete():
    if 'name' in session:
        item_name=request.args.get('item')
        cur = mysql.connection.cursor()
        query = """DELETE FROM LOSTFOUND WHERE item_name=%s"""
        data = (item_name,)
        cur.execute(query, data)
        mysql.connection.commit()
        cur.close()
        return "<h1>Item deleted<h1>"
    else:
        return "</h1>Login First</h1>"

@app.route('/home/view')
def view():
    if 'name' in session:
        cur=mysql.connection.cursor()
        query="""SELECT * FROM LOSTFOUND"""
        cur.execute(query)
        mysql.connection.commit()
        data=cur.fetchall()
        cur.close()
        return render_template('view.html', data=data)
    else:
        return "</h1>Login First</h1>"

@app.route('/home/search',methods=['GET','POST'])
def search():
    if 'name' in session:
        render_template('search.html')
        itemname=request.form['item_name']
        location=request.form['location']
        cur = mysql.connection.cursor()
        query = """SELECT * FROM LOSTFOUND WHERE item_name=%s AND location=%s"""
        data = (itemname,location,)
        cur.execute(query, data)
        mysql.connection.commit()
        data=cur.fetchall()
        cur.close()
        return render_template('searchview.html', data=data)
    else:
        return "</h1>Login First</h1>"





if __name__=="__main__":
    app.secret_key="th3g3ntl3m4n"
    app.run(debug='TRUE')
