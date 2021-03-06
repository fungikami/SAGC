import unittest
from app import *
from db_create import create_db
import os

# Para ver si funciona los tests: python tests.py -v
class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_flask.db'
        app.config['TESTING'] = True
        create_db("test_flask.db")

    def tearDown(self):
        os.remove("database/test_flask.db")

    # Verifica que flask esté funcionando exitosamente
    def test_flask(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente (Este no es muy funcional)
    def test_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/')
        self.assertIn(b'Bienvenido', response.data)
        response = tester.get('/login')
        self.assertIn(b'Iniciar', response.data)
        