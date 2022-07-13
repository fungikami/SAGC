import unittest
from app import *
from db_create import create_db
from flask import url_for, request
import os

#----------------------------------------------------------------------------------------------------------------------
class RecolectorCase(unittest.TestCase):

    def setUp(self):
        print("\nRecolectorTest: Iniciando pruebas...")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_recolector.db'
        app.config['TESTING'] = True
        create_db("test_recolector.db")

    def tearDown(self):
        os.remove("database/test_recolector.db")

    # Verifica que flask esté funcionando exitosamente
    def test_flask(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/recolector', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)
        response = tester.get('/recolector')
        self.assertIn(b'Datos personales del Recolector', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            # Registra recolector
            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is not None)

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un email que existe...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            # Registra recolector
            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is not None)

            # Registra recolector con una cedula que ya existe
            response = tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='PruebaModificar', apellido='PruebaModificar',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            self.assertIn(b'El recolector con dicha cedula ya se encuentra registrado.', response.data)

            # Registra recolector con un nombre largo
            response = tester.post('/recolector', data=dict(
                cedula=33333333, nombre='Prueba3Prueba3Prueba3Prueba3Prueba3', apellido='Prueba3',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            self.assertIn(b'El nombre y apellido no puede tener mas de 20 caracteres.', response.data)


    #  Verifica que se puede eliminar un recolector
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is not None)

            # Elimina recolector
            response = tester.post('/recolector/delete/' + str(prod.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is None)

    #  Verifica que no se puede eliminar un recolector que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is not None)
            id = str(prod.id)

            # Elimina recolector
            tester.post('/recolector/delete/' + id, follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is None)

            # Elimina recolector que no existe
            tester.post('/recolector/delete/' + id, follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is None)

    #  Verifica que se puede editar un recolector
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is not None)

            # Edita recolector
            response = tester.post('/recolector/update/' + str(prod.id), data=dict(
                cedula="V-22222222", nombre='PruebaModificar', apellido='PruebaModificar',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)

            self.assertIn(b'Se ha modificado exitosamente.', response.data)

            prod = Recolector.query.filter_by(ci="V-22222222", nombre='Prueba').first()
            self.assertTrue(prod is None)

            prod = Recolector.query.filter_by(ci="V-22222222", nombre='PruebaModificar').first()
            self.assertTrue(prod is not None)

    #  Verifica que no se puede editar recolector que no existe
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is not None)

            tester.post('/recolector', data=dict(
                cedula="V-11111111", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod2 = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod2 is not None)

            # Edita recolector 1 con la cédula del recolector 2
            response = tester.post('/recolector/update/' + str(prod.id), data=dict(
                cedula="V-11111111", nombre='PruebaModificar', apellido='PruebaModificar',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)

            self.assertIn(b'El recolector con dicha cedula ya se encuentra registrado.', response.data)
            prod2 = Recolector.query.filter_by(ci="V-11111111", nombre='PruebaModificar').first()
            self.assertTrue(prod2 is None)

    #  Verifica que se puede buscar un recolector
    def test_search(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            tester.post('/recolector', data=dict(
                cedula="V-22222222", nombre='Prueba', apellido='Prueba',
                telefono='0412-12345678', celular='0412-12345678',
                direccion1='Calle falsa 123', direccion2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Recolector.query.filter_by(ci="V-22222222").first()
            self.assertTrue(prod is not None)

            # Busca recolector
            response = tester.post('/recolector/search', data=dict(
                search_recolector=22222222
            ), follow_redirects=True)

            self.assertIn(b'Prueba', response.data)

if __name__ == '__main__':

    # Se cambia la base de datos para usar la de los test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_db.db'
    app.config['TESTING'] = True
    # Verificamos si no existe la base de datos para los test
    if not os.path.exists("database/test_db.db"):
        create_db("database/test_db.db")

    unittest.main()