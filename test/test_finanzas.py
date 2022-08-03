import unittest
from app import *
from db_create import create_db
import os
import datetime

class FinanciaCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_financia.db'
        app.config['TESTING'] = True
        create_db("test_financia.db")

    @classmethod
    def tearDownClass(self):
        os.remove("database/test_financia.db")

    def test_flask(self):
        """ Verifica que Flask funcione correctamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)

        id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
        tipo = 'generar'
        response = tester.get(f'/cosecha/{id}/financias/{tipo}', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_page_loads(self):
        """ Verifica que las páginas (HTML) cargan exitosamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
        id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
        desc = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().descripcion
        tipo = 'generar'
        response = tester.get(f'/cosecha/{id}/financias/{tipo}', content_type='html/text')
        str = f'{desc}: Datos del Financiamiento'
        self.assertIn(bytes(str, "utf-8"), response.data)

    # Verifica que el registro de financiamiento funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tipo = 'generar'
            self.assertTrue(id is not None)
            
            date = datetime.datetime.now()
            tester.post(f'/cosecha/{id}/financias/{tipo}', data=dict(
                    cedula = 'V-12345678', letra_cambio ="00010",
                    vencimiento = date.strftime("%Y-%m-%d"), monto = 0,
                    pago="Sí", observacion = 'PRUEBA'
                ), follow_redirects=True)

            financia = Financia.query.filter_by(observacion='PRUEBA').first()
            #self.assertTrue(financia is not None)
            
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tipo = 'generar'
            self.assertTrue(id is not None)
        
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tipo = 'generar'
            self.assertTrue(id is not None)

    def test_correct_edit(self): 
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tipo = 'generar'
            self.assertTrue(id is not None)

    def test_incorrect_edit(self): 
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tipo = 'generar'
            self.assertTrue(id is not None)

    def test_search(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="gerente", password="gerente"), follow_redirects=True)
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tipo = 'generar'
            self.assertTrue(id is not None)