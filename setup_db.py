import app
START_SUNDAY = '2023-03-19'
db.session.query(Day).delete()
db.create_all()
db = app.db_init(db,START_SUNDAY)
print("Initialized db")
