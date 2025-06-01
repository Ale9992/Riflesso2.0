import json
import jwt
from flask import current_app

def test_register_user(client, init_database, new_user_data):
    response = client.post('/auth/register', json=new_user_data)
    assert response.status_code == 201
    assert response.json['message'] == 'New user created!'

    response = client.post('/auth/register', json=new_user_data)
    assert response.status_code == 409
    assert response.json['message'] == 'User already exists'

def test_login_user(client, init_database, new_user_data):
    client.post('/auth/register', json=new_user_data)

    login_data = {"username": new_user_data['username'], "password": new_user_data['password']}
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 200
    assert 'token' in response.json

    token = response.json['token']
    decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    assert decoded_token['user_id'] is not None

    login_data_wrong_pass = {"username": new_user_data['username'], "password": "wrongpassword"}
    response = client.post('/auth/login', json=login_data_wrong_pass)
    assert response.status_code == 401
    assert response.json['message'] == 'Could not verify'

def test_login_nonexistent_user(client, init_database):
    login_data = {"username": "nosuchuser", "password": "password123"}
    response = client.post('/auth/login', json=login_data)
    assert response.status_code == 401
    assert response.json['message'] == 'Could not verify'

def test_missing_fields_register(client, init_database):
    response = client.post('/auth/register', json={"username": "test"})
    assert response.status_code == 400
    assert "Missing username, email, or password" in response.json['message']
