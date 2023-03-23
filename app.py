from flask import Flask, request, redirect, render_template,url_for,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import pandas

app = Flask(__name__)
dbname = "Days"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}'.format(dbname)
app.secret_key = datetime.now().strftime('%s')

db = SQLAlchemy(app)

ADMIN_PASSWORD = 'password'
COHO_PASSWORD = 'cohomeals2023'

class Day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    day_name = db.Column(db.String(50),nullable=False)
    row_index = db.Column(db.Integer,default=0)
    cook = db.Column(db.String(10),default='Unassigned',nullable=False)
    assist = db.Column(db.String(10),default='Unassigned',nullable=False)
    clean1 = db.Column(db.String(10),default='Unassigned',nullable=False)
    clean2 = db.Column(db.String(10),default='Unassigned',nullable=False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    def __repr__(self):
        return '<Day %r>' % self.id

def db_init(db,start_date,numweeks=8):
    #to be executed in a Flask shell every 8 weeks.

    #Assume start date is the first sunday.  
    #Fill DB with 8 weeks ending on a Saturday.

    #delete existing entries
    try:
        existing_days = db.session.query.all()
        print("deleting db")
        Day.query.delete()
        db.session.commit()
    except:
        pass

    #get list of date strings ('YYYY-MM-DD')
    numdays = 7*numweeks
    dates = pandas.date_range(start_date,
               datetime.strptime(start_date,'%Y-%m-%d')+timedelta(days=numdays-1), 
            freq='d')
    #add all placeholder days to table
    row = 0
    day_names = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
    for i in range(numdays): 
        if i % 7 == 0: row += 1
        date = dates[i].date()
        new_day = Day(date=date,day_name=day_names[i%7],row_index=row)
        try:
            db.session.add(new_day)
            db.session.commit()
        except:
            raise Exception('Issue adding new day')
    
    return db

@app.route('/login',methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['coho_password'] != COHO_PASSWORD:
            error = 'Incorrect password'
        else:
            #assign unique username to client based on current time
            session['username'] = 'approved'+datetime.now().strftime('%s')
            return redirect(url_for('index'))
    
    return render_template('login.html',error=error)

@app.route('/', methods=['POST', 'GET'])
def index():
    error = None
    username = session.get('username','') #'' is default if not yet signed in
    if not username.startswith('approved'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        if request.form.get('admin_password') != ADMIN_PASSWORD:
            error = "Incorrect password"
        else:
            session['username'] = 'approvedadmin'+datetime.now().strftime('%s') 
    
    admin = session.get('username').startswith('approvedadmin')
    print("admin = ",admin)
    days = db.session.query(Day).order_by(Day.id).all()
    return render_template('index.html',days=days,admin=admin,error=error)

@app.route('/update/<int:id>',methods = ['GET','POST'])
def update(id):
    jobs = ['cook','assist','clean1','clean2']
    day_to_update = Day.query.get_or_404(id)
    admin = session.get('username').startswith('approvedadmin')
    if request.method == 'POST':
        if request.form.get('click') == "Discard Changes/Go Back":
            return redirect(url_for('index'))
        #update database with updated name
        for jobname in jobs:
            try:
                name_in_textbox = request.form[jobname]
            except:
                continue #job was not in update form because it is already assigned--see update.html jinja logic

            if len(name_in_textbox.strip()) == 0:
                #all whitespace--handle differently if admin or not
                if admin:
                    #admin was trying to delete the name
                    name_in_textbox = 'Unassigned'
                else:
                    #silly goose forgot to input a name
                    continue

            exec("day_to_update.{0} = name_in_textbox".format(jobname))

        try:
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return eval("Issue updating {0}".format(day_to_update.date))
    
    return render_template('update.html',day=day_to_update,admin=admin)

if __name__ == '__main__':
    app.run(debug=True)

