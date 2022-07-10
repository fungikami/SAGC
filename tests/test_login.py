import unittest
from app import *
from db_create import create_db
from flask import url_for, request
import os

class LoginTestCase(unittest.TestCase):
    # Verifica que /recolector /perfiles /eventos y /logout requieren de haber iniciado sesión
    def test_route_requires_login(self):
        tester = app.test_client()
        response = tester.get('/perfiles', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
        response = tester.get('/recolector', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
        response = tester.get('/eventos', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
        response = tester.get('/logout', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
    
    # Verifica que el login funciona exitosamente cuando se dan las credenciales correctas
    def test_correct_login(self):
        tester = app.test_client()
        with tester:
            response = tester.post('/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'Se ha iniciado la sesion exitosamente', response.data)

    # Verifica que el login funciona exitosamente cuando se dan las credenciales incorrectas
    def test_incorrect_login_user_doesnt_exist(self):
        tester = app.test_client()
        with tester:
            response = tester.post('/login', data=dict(nombre_usuario="", password=""), follow_redirects=True)
            assert request.path == url_for('login')
            self.assertIn(b'Todos los campos son obligatorios', response.data)

            # Usuario que no existe
            response = tester.post('/login', data=dict(nombre_usuario="wrong", password="wrong"), follow_redirects=True)
            assert request.path == url_for('login')
            self.assertIn(b'Credenciales invalidas', response.data)

            # Usuario que existe, pero contraseña incorrecta
            response = tester.post('/login', data=dict(nombre_usuario="admin", password="wrong"),follow_redirects=True)
            assert request.path == url_for('login')
            self.assertIn(b'Credenciales invalidas', response.data)
    
    # Verifica que el logout funciona exitosamente
    def test_logout(self):
        tester = app.test_client()
        tester.post('/login', data=dict(nombre_usuario="admin", password="admin"), follow_redirects=True)
        with tester:
            response = tester.get('/logout', follow_redirects=True)
            assert request.path == url_for('home')
            self.assertIn(b'Se ha cerrado la sesion', response.data)

if __name__ == '__main__':

    # Se cambia la base de datos para usar la de los test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_db.db'
    app.config['TESTING'] = True
    # Verificamos si no existe la base de datos para los test
    if not os.path.exists("database/test_db.db"):
        create_db("database/test_db.db")

    unittest.main()