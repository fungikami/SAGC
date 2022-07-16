import unittest
from app import *
from db_create import create_db
import os

class TipoRecolectorCase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_tiporecolector.db'
        app.config['TESTING'] = True
        create_db("test_tiporecolector.db")

    @classmethod
    def tearDownClass(self):
        os.remove("database/test_tiporecolector.db")

    def test_flask(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/tipo_recolector', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/tipo_recolector')
        self.assertIn(b'Tipos de Recolector', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            tester.post('/tipo_recolector', data=dict(descripcion='Prueba', precio=1.0), follow_redirects=True)

            response = tester.get('/tipo_recolector', follow_redirects=True)
            self.assertIn(b'Tipos de Recolector', response.data)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un tipo de recolector que ya existe, una descripción mala...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            # Registra tipo de recolector
            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)           

            # Registra tipo de recolector de nuevo
            response = tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba'
                ), follow_redirects=True)

            self.assertIn(b'El tipo de recolector ya se encuentra definido.', response.data)

    #  Verifica que se puede eliminar un tipo de recolector
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            # Elimina tipo de recolector
            tester.post('/tipo_recolector/delete/' + str(type.id), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is None)

    #  Verifica que no se puede eliminar un tipo de recolector que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)
            id = str(type.id)

            # Elimina tipo de recolector
            tester.post('/tipo_recolector/delete/' + id, follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is None)

            # Elimina tipo de recolector de nuevo
            tester.post('/tipo_recolector/delete/'  + id, follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is None)

    #  Verifica que se puede editar un tipo de recolector
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/tipo_recolector', data=dict(
                    descripcion='PruebaModificar',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='PruebaModificar').first()
            self.assertTrue(type is not None)

            # Edita tipo de recolector
            tester.post('/tipo_recolector/update/' + str(type.id), data=dict(
                    descripcion='PruebaModificar2',
                    precio=1.0
                ), follow_redirects=True)

            # type = TipoRecolector.query.filter_by(descripcion='PruebaModificar').first()
            # self.assertTrue(type is None)

            type = TipoRecolector.query.filter_by(descripcion='PruebaModificar2').first()
            self.assertTrue(type is not None)

    #  Verifica que no se puede editar un tipo de recolector que no existe
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            # Registra tipo de recolector
            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            tester.post('/tipo_recolector', data=dict(
                    descripcion='PruebaModificar',
                    precio=1.0
                ), follow_redirects=True)
            type2 = TipoRecolector.query.filter_by(descripcion='PruebaModificar').first()
            self.assertTrue(type2 is not None)

            # Edita tipo de recolector a uno que ya se encuentra en uso
            response = tester.post('/tipo_recolector/update/' + str(type.id), data=dict(
                    descripcion='PruebaModificar',
                    precio=1.0
                ), follow_redirects=True)

            self.assertIn(b'El tipo de recolector ya se encuentra definido.', response.data)

    #  Verifica que se puede buscar un tipo de recolector
    def test_search(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            # Busca tipo de recolector
            tester.post('/tipo_recolector/search', data=dict(search_tipo_recolector='Prueba'), follow_redirects=True)

            # Buscar tipo de recolector
            response = tester.get('/tipo_recolector', follow_redirects=True)
            self.assertIn(b'Tipos de Recolector', response.data)
            self.assertIn(b'Prueba', response.data)
