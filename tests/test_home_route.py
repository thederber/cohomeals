from app import app
def test_home_route():
    response = app.test_client().get('/login')
    assert response.status_code == 200
