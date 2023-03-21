import app
START_SUNDAY = '2023-03-19'

#delete existing database
try:
    db.session.query(Day).delete()
except:
    print("DB doesnt yet exist")

db.create_all()
db = app.db_init(db,START_SUNDAY)
print("Initialized db")
