from flask.app import Flask
import pytest
from flask import g
from flask import session
from flaskr.db import get_db
from werkzeug.security import check_password_hash




def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "b", "verifypassword": "b", "email": "gmail.com"})
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
            usuario = get_db().execute("SELECT * FROM user WHERE username = 'a'").fetchone()
            assert (usuario is not None)
            assert (check_password_hash(usuario["password"], "b"))           


@pytest.mark.parametrize(
    ("username", "password", "verifypassword", "message", "email"),
    (
        ("", "", "", "Nombre de usuario es requerido.","gmail.com"),
        ("a", "", "", "Contraseña es requerida.", "gmail.com"),
        ("a", "1234", "", "La verificacion de contraseña es requerida.","gmail.com"),
        ("test", "test", "test", "ya esta registrado", "gmail.com"),
        ("c", "1234", "4321", "Contraseñas distintas.", "gmail.com"),
        ("a", "b", "b", "El email es requerido", "" ),
        ("test", "test", "test", "El email ya esta registrado.", "test" )
    ),
)
def test_register_validate_input(client, username, password, message, verifypassword, email):
    response = client.post(
        "/auth/register", data={"username": username, "password": password, "verifypassword": verifypassword, "email": email }
    )
    assert message in response.data.decode() 
    # decode sirve para decodificar y pasar a nuestro idioma los mensajes 


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user["username"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message","email"),
    (("a", "test", "Nombre de usuario o contraseña incorrecta",""), 
     ("test", "a", "Nombre de usuario o contraseña incorrecta", ""),
     ("a", "b", "Email incorrecto","test"),
     ),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data.decode()


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
