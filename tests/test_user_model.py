from app.models.user import User

def test_new_user(new_user_data):
    user = User(username=new_user_data['username'], email=new_user_data['email'])
    user.set_password(new_user_data['password'])
    assert user.email == new_user_data['email']
    assert user.username == new_user_data['username']
    assert user.password_hash != new_user_data['password']
    assert user.check_password(new_user_data['password'])
    assert not user.check_password("wrongpassword")
