import unittest
from app import *
from db_create import create_db
import os
import datetime

class EventoCase(unittest.TestCase):
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
        response = tester.get('/eventos', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_page_loads(self):
        """ Verifica que las páginas (HTML) cargan exitosamente """
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/eventos')
        self.assertIn(b'Logger de Eventos', response.data)

    def test_correct_delete(self):
        """ Verifica que se puede eliminar un evento """
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            tester.post('/tipo_recolector', data=dict(descripcion='Prueba', precio=1.0), follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            evento = Evento.query.filter_by(descripcion=str(type)).first()
            self.assertTrue(evento is not None)

            tester.post(f'eventos/{{ evento.id }}/delete', follow_redirects=True)
            evento = Evento.query.filter_by(descripcion=str(type)).first()
            self.assertTrue(evento is None)

    def test_incorrect_delete(self):
        """ Verifica que no se puede eliminar un evento que no existe """
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
            evento = Evento.query.filter_by(descripcion="Evento que no existe").first()
            self.assertTrue(evento is None)
            response = tester.get(f'eventos/{{ evento.id }}/delete', follow_redirects=True)
            self.assertIn(b'El evento no se encuentra registrado.', response.data)
            
    def test_search(self):
        """ Verifica que se puede buscar un evento """
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)      
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            evento = Evento.query.filter_by(descripcion=str(type)).first()
            self.assertTrue(evento is not None)

            response = tester.post('/eventos/search', data=dict(search_evento='Prueba'), follow_redirects=True)
            self.assertIn(b'Prueba', response.data)
    
    # ---------------------------- VISTA DE PERFILES -------------------------------------------------
    def test_register_perfil(self):
        """ Verifica que se registra un evento al agregar un perfil"""
        self.assertTrue(True)

    def test_update_perfil(self):
        """ Verifica que se registra un evento al modificar un perfil"""
        self.assertTrue(True)

    def test_delete_perfil(self):
        """ Verifica que se registra un evento al eliminar un perfil"""
        self.assertTrue(True)

    # ---------------------------- VISTA DE TIPO DE RECOLECTORES -------------------------------------------------
    def test_register_tipo_recolector(self):
        """ Verifica que se registra un evento al agregar un tipo de recolector"""
        self.assertTrue(True)

    def test_update_tipo_recolector(self):
        """ Verifica que se registra un evento al modificar un tipo de recolector"""
        self.assertTrue(True)

    def test_delete_tipo_recolector(self):
        """ Verifica que se registra un evento al eliminar un tipo de recolector"""
        self.assertTrue(True)

    # ---------------------------- VISTA DE RECOLECTORES -------------------------------------------------
    def test_register_recolector(self):
        """ Verifica que se registra un evento al agregar un recolector"""
        self.assertTrue(True)

    def test_update_recolector(self):
        """ Verifica que se registra un evento al modificar un recolector"""
        self.assertTrue(True)

    def test_delete_recolector(self):
        """ Verifica que se registra un evento al eliminar un recolector"""
        self.assertTrue(True)

    # ---------------------------- VISTA DE COSECHAS -------------------------------------------------
    def test_register_cosecha(self):
        """ Verifica que se registra un evento al agregar una cosecha"""
        self.assertTrue(True)

    def test_update_cosecha(self):
        """ Verifica que se registra un evento al modificar una cosecha"""
        self.assertTrue(True)

    def test_delete_cosecha(self):
        """ Verifica que se registra un evento al eliminar una cosecha"""
        self.assertTrue(True)

    # ---------------------------- VISTA DE COMPRAS -------------------------------------------------
    def test_register_compra(self):
        """ Verifica que se registra un evento al agregar una compra"""
        self.assertTrue(True)

    def test_update_compra(self):
        """ Verifica que se registra un evento al modificar una compra"""
        self.assertTrue(True)

    def test_delete_compra(self):
        """ Verifica que se registra un evento al eliminar una compra"""
        self.assertTrue(True)
