from app.routes.auth import authenticate_demo_user


def test_demo_user_login_succeeds():
    result = authenticate_demo_user("admin@skillbridge.local", "admin123")
    assert result is not None
    assert result["role"] == "admin"


def test_unknown_demo_user_fails():
    result = authenticate_demo_user("no-user@example.com", "wrong")
    assert result is None
