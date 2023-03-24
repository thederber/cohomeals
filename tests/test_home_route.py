import app
from flask import session
from app import app as flaskapp

def test_index_notloggedin():
    response = flaskapp.test_client().get('/',follow_redirects=True)
    assert response.request.path == '/login'

def test_update_notloggedin():
    response = flaskapp.test_client().get('/update/1',follow_redirects=True)
    assert response.request.path == '/login'

#now do some tests with a logged-in client
client = flaskapp.test_client()

def test_login():
    #login first
    with client:
        client.post("/login",data={"coho_password": app.COHO_PASSWORD})
        assert session["username"].startswith('approved')

def test_index():
    response = client.get('/')
    assert response.status_code == 200

def test_update():
    #verify update->submit works
    response = client.post("/update/12", follow_redirects=True,
        data={
        "cook": "Derek",
        "assist": "Derek",
        "clean1": "Derek",
        "clean2": "Derek",
        "click": "Submit Changes",
    })
    assert response.status_code == 200
    #verify update->discard changes works
    response = client.post("/update/3", follow_redirects=True,
        data={
        "cook": "Derek",
        "assist": "Derek",
        "clean1": "Derek",
        "clean2": "Derek",
        "click": "Discard Changes/Go Back",
    })
    assert response.status_code == 200

