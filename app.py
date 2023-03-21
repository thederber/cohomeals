from flask import Flask, request, redirect, render_template,url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import pandas

app = Flask(__name__)
dbname = "Days"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}'.format(dbname)
    
db = SQLAlchemy(app)

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


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        #cook_name = request.form['content']
        #date_clicked = '2023-03-22' #test
        #try:
        #    Day.query.filter(Day.date == date_clicked).update({'cook': cook_name})
        #    db.session.commit()
        #    return redirect('/')
        #except:
        #    return 'Issue adding new name to db.'
        return redirect('/')
    else:
        days = db.session.query(Day).order_by(Day.id).all()
        return render_template('index.html',days=days)


@app.route('/update/<int:id>',methods = ['GET','POST'])
def update(id):
    jobs = ['cook','assist','clean1','clean2']
    day_to_update = Day.query.get_or_404(id)
    if request.method == 'POST':
        if request.form.get('click') == 'Discard Changes':
            return redirect('/')
        #update database with updated name
        for jobname in jobs:
            try:
                name_in_textbox = request.form[jobname]
            except:
                continue #job was not in update form because it is already assigned--see update.html jinja logic

            if len(name_in_textbox.strip()) == 0: 
                #silly goose tried to submit empty name
                continue

            exec("day_to_update.{0} = name_in_textbox".format(jobname))

        try:
            db.session.commit()
            return redirect('/')
        except:
            return eval("Issue updating {0}".format(day_to_update.date))
    else:
        return render_template('update.html',day=day_to_update)


"""
@app.route('/delete/<int:id>')
def delete(id):
    day_to_delete = Day.query.get_or_404(id)
    day_to_delete.cook = 'Unassigned'
    try:
        db.session.commit()
        return redirect('/')
    except:
        return "Issue deleting"
"""

if __name__ == '__main__':
    app.run(debug=True)

