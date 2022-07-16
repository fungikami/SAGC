import unittest
from app import *
from db_create import create_db
from flask import url_for, request
import os

class LoginTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_login.db'
        app.config['TESTING'] = True
        create_db("test_login.db")

    @classmethod
    def tearDownClass(self):
        os.remove("database/test_login.db")

    # Verifica que /recolector /perfiles /eventos y /logout requieren de haber iniciado sesión
    def test_route_requires_login(self):
        tester = app.test_client()
        response = tester.get('/perfiles', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
        response = tester.get('/recolector', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
        response = tester.get('/tipo_recolector', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
        response = tester.get('/cosecha', follow_redirects=True)
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
    def test_incorrect_login_username(self):
        tester = app.test_client()
        with tester:
            # Usuario que no existe
            response = tester.post('/login', data=dict(nombre_usuario="wrong", password="wrong"), follow_redirects=True)
            assert request.path == url_for('login')
            self.assertIn(b'Credenciales invalidas', response.data)

    def test_incorrect_login_password(self):
        tester = app.test_client()
        with tester:
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
