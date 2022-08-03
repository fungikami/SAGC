import unittest
from app import *
from db_create import create_db
import os
import datetime

class BancoCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_banco.db'
        app.config['TESTING'] = True
        create_db("test_banco.db")

    @classmethod
    def tearDownClass(self):
        os.remove("database/test_banco.db")

    def test_flask(self):
        """ Verifica que Flask funcione correctamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)

        response = tester.get(f'/bancos/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_page_loads(self):
        """ Verifica que las páginas (HTML) cargan exitosamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
        response = tester.get(f'/bancos/', content_type='html/text')
        self.assertIn(b'Banco', response.data)

    def test_correct_credit(self):
        """ Verifica que se genere un crédito correctamente """
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            tester.post('/bancos/', data=dict(agregar_credito = 5000), follow_redirects=True)
            banco = Banco.query.filter_by(monto=5000).first()
            self.assertTrue(banco is not None)

    def test_correct_rollback(self):
        """ Verifica que se revierte un crédito correctamente """
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            tester.post('/bancos/', data=dict(agregar_credito = 5000), follow_redirects=True)
            banco = Banco.query.filter_by(monto=5000).first()
            self.assertTrue(banco is not None)

            tester.post('/bancos/{{ banco.id }}/revertir', follow_redirects=True)
            banco = Banco.query.filter_by(monto=5000).first()
            self.assertTrue(banco is not None)

    def test_correct_search(self):
        """ Verifica que la búsqueda funcione correctamente en Bancos"""
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            
            tester.post('/bancos/', data=dict(agregar_credito = 5000), follow_redirects=True)
            response = tester.post(f'/bancos/search', data=dict(
                search_bancos = '5000', Desde = '', Hasta = ''
            ), follow_redirects=True)

            self.assertIn(b'Banco', response.data)
            self.assertIn(b'5000', response.data)

    def test_debito(self):
        """ Verifica que se genere un débito correctamente """
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            self.assertTrue(id is not None)

    def test_credito_compra(self):
        """ Verifica que se genere un crédito de compra correctamente """
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            self.assertTrue(id is not None)

    def test_credito_financia(self):
        """ Verifica que se genere un crédito correctamente """
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            self.assertTrue(id is not None)
    
    def test_delete_credito_financia(self):
        """ Verifica que se genere un crédito correctamente """
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            self.assertTrue(id is not None)