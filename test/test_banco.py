import unittest
from app import *
from db_create import create_db
import os
import datetime

class FinanciaCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_evento.db'
        app.config['TESTING'] = True
        create_db("test_evento.db")

    @classmethod
    def tearDownClass(self):
        os.remove("database/test_evento.db")

    def test_flask(self):
        """ Verifica que Flask funcione correctamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

        response = tester.get(f'/bancos', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_page_loads(self):
        """ Verifica que las páginas (HTML) cargan exitosamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get(f'/banco', content_type='html/text')
        self.assertIn(b'Banco', response.data)

    def test_correct_credit(self):
    def test_correct_rollback(self):
    def test_correct_search(self):

    # tambien se pudiesen probar los debitos por compras, creditos por reverso de compras,
    # creditos por finanzas y eliminacion de credito al eliminarse una finanza pero mucho trabaj0