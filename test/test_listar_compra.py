import unittest
from app import *
from db_create import create_db
import os

class ListarCompraCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_compra.db'
        app.config['TESTING'] = True
        create_db("test_compra.db")

    def tearDown(self):
        os.remove('database/test_compra.db')

    def test_flask(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
        response = tester.get(f'/cosecha/{id}/listar', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        cosecha = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first()
        response = tester.get(f'/cosecha/{cosecha.id}/listar', content_type='html/text')
        str = f'{cosecha.descripcion}: Datos de la Compra'
        self.assertIn(bytes(str, "utf-8"), response.data)
        
    #  Verifica que se puede buscar una compra
    def test_search(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)            
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0, 
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, merma_kg = 0,
                    cantidad_total = 0, monto = 0, observacion = 'PRUEBA',
                ), follow_redirects=True)

            response = tester.post(f'/cosecha/{id}/listar/search', data=dict(
                search_compra = 'PRUEBA'
            ), follow_redirects=True)

            # Buscar tipo de cosecha
            self.assertIn(b'Portafolio de Cosechas', response.data)
            self.assertIn(b'PRUEBA', response.data)

    # Verifica que se puede descargar una compra
    def test_download(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            cosecha = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first()
            self.assertTrue(cosecha is not None)