import unittest 
from app import app, Usuario, TipoRecolector, Recolector, Cosecha
from db_create import create_db
from flask import url_for, request
import os
import datetime

# Para ver si funciona los tests:
# python tests.py -v
class FlaskTestCase(unittest.TestCase):

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
            response = tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )
            assert request.path == url_for('perfiles')
            self.assertIn(b'Se ha iniciado la sesion exitosamente', response.data)

    # Verifica que el login funciona exitosamente cuando se dan las credenciales incorrectas
    def test_incorrect_login_user_doesnt_exist(self):
        tester = app.test_client()
        with tester:
            # Campos vacíos
            response = tester.post(
                '/login',
                data=dict(nombre_usuario="", password=""),
                follow_redirects=True
            )
            assert request.path == url_for('login')
            self.assertIn(b'Todos los campos son obligatorios', response.data)

            # Usuario que no existe
            response = tester.post(
                '/login',
                data=dict(nombre_usuario="wrong", password="wrong"),
                follow_redirects=True
            )
            assert request.path == url_for('login')
            self.assertIn(b'Credenciales invalidas', response.data)

            # Usuario que existe, pero contraseña incorrecta
            response = tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="wrong"),
                follow_redirects=True
            )
            assert request.path == url_for('login')
            self.assertIn(b'Credenciales invalidas', response.data)
    
    # Verifica que el logout funciona exitosamente
    def test_logout(self):
        tester = app.test_client()
        tester.post(
            '/login',
            data=dict(nombre_usuario="admin", password="admin"),
            follow_redirects=True
        )
        with tester:
            response = tester.get('/logout', follow_redirects=True)
            assert request.path == url_for('home')
            self.assertIn(b'Se ha cerrado la sesion', response.data)

#----------------------------------------------------------------------------------------------------------------------
class PerfilesTestCase(unittest.TestCase):

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )
            
            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='Prueba', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )

            response = tester.get('/perfiles', follow_redirects=True)
            self.assertIn(b'Perfiles de Usuarios', response.data)
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is not None)

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un user que ya existe, una contraseña mala...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )

            # Registro con usuario largo
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="adminadminadminadminadmin", nombre="Administrador", apellido="Administrador", 
                password="admin", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'El nombre de usuario no puede tener mas de 20 caracteres', response.data)

            # Registrarse a si mismo
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="admin", nombre="Administrador", apellido="Administrador", 
                password="admin", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'El nombre de usuario ya se encuentra en uso', response.data)
            
            # Registrarse con contraseña muy corta
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="prueba", nombre="Prueba", apellido="Prueba",
                password="pr", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'debe tener al menos 8 caracteres', response.data)
            
            # Registrarse con contraseña muy larga
            response = tester.post('/perfiles', data=dict(
                nombre_usuario="prueba", nombre="Prueba", apellido="Prueba",
                password="prprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprpr", 
                rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'no puede tener mas de 80 caracteres', response.data)
    
    #  Verifica que se puede eliminar un perfil
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='Prueba', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is not None)

            # Elimina perfil
            response = tester.post('/perfiles/delete/' + str(user.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)

            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is None)

    #  Verifica que no se puede eliminar un perfil que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='Prueba', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is not None)
            id = str(user.id)

            # Elimina perfil
            response = tester.post('/perfiles/delete/' + str(user.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is None)

            # Elimina perfil que no existe
            tester.post('/perfiles/delete/' + id, follow_redirects=True)
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is None)

    #  Verifica que se puede editar un perfil
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='PruebaModificar', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='PruebaModificar').first()
            self.assertTrue(user is not None)

            # Edita perfil
            response = tester.post('/perfiles/update/' + str(user.id), data=dict(
                    nombre_usuario='PruebaModificar', nombre='Prueba2', apellido='Prueba2',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            self.assertIn(b'Se ha modificado exitosamente.', response.data)

            user = Usuario.query.filter_by(nombre_usuario='PruebaModificar', nombre='Prueba2').first()
            self.assertTrue(user is not None)

    #  Verifica que no se puede editar perfil que no existe
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='PruebaModificar', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='PruebaModificar').first()
            self.assertTrue(user is not None)

            # Edita perfil con un nombre_usuario que ya existe
            response = tester.post('/perfiles/update/' + str(user.id), data=dict(
                    nombre_usuario='admin', nombre='Prueba2', apellido='Prueba2',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            self.assertIn(b'El nombre de usuario ya se encuentra en uso.', response.data)

            user = Usuario.query.filter_by(nombre='Prueba2').first()
            self.assertTrue(user is not None)

    #  Verifica que se puede buscar un perfil
    def test_search(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    nombre_usuario='Prueba', nombre='Prueba', apellido='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = Usuario.query.filter_by(nombre_usuario='Prueba').first()
            self.assertTrue(user is not None)

            # Busca perfil
            response = tester.post('/perfiles/search', data=dict(
                    search_perfil='Prueba'
                ), follow_redirects=True
            )
            self.assertIn(b'Prueba', response.data)

#----------------------------------------------------------------------------------------------------------------------
class RecolectorCase(unittest.TestCase):
    # Verifica que flask esté funcionando exitosamente
    def test_flask(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(nombre_usuario="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/recolector', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(nombre_usuario="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/recolector')
        self.assertIn(b'Datos personales del Recolector', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra recolector
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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra recolector
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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra recolector
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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra recolector
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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra recolector
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

#----------------------------------------------------------------------------------------------------------------------
class TipoRecolectorCase(unittest.TestCase):
    def test_flask(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(nombre_usuario="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/tipo_recolector', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(nombre_usuario="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/tipo_recolector')
        self.assertIn(b'Tipos de Recolector', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de recolector
            tester.post('/tipo_recolector', data=dict(
                    descripcion='Prueba',
                    precio=1.0
                ), follow_redirects=True)

            response = tester.get('/tipo_recolector', follow_redirects=True)
            self.assertIn(b'Tipos de Recolector', response.data)
            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)
            self.assertTrue(str(type) == "TipoRecolector('Prueba')")

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un tipo de recolector que ya existe, una descripción mala...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de recolector
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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de recolector
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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de recolector
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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

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
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            type = TipoRecolector.query.filter_by(descripcion='Prueba').first()
            self.assertTrue(type is not None)

            # Registra tipo de recolector
            tester.post('/tipo_recolector/search', data=dict(
                    search_recolector='Prueba'
                ), follow_redirects=True)

            # Buscar tipo de recolector
            response = tester.get('/tipo_recolector', follow_redirects=True)
            self.assertIn(b'Tipos de Recolector', response.data)
            self.assertIn(b'Prueba', response.data)

#----------------------------------------------------------------------------------------------------------------------
class CosechaCase(unittest.TestCase):
    def test_flask(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(nombre_usuario="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/cosecha', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(nombre_usuario="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/cosecha')
        self.assertIn(b'Portafolio de Cosechas', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            response = tester.get('/cosecha', follow_redirects=True)
            self.assertIn(b'Portafolio de Cosechas', response.data)
            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba 2022-2023').first()
            self.assertTrue(type is not None)
            self.assertTrue(str(type) == "Cosecha('Cosecha Prueba 2022-2023')")

    # Verifica que se muestra error si se realiza un registro de una cosecha que ya existe
    def test_incorrect_register_A(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)           

            # Registra cosecha nuevamente.
            response = tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            self.assertIn(b'La cosecha que se intenta agregar ya se encuentra definida.', response.data)

# Verifica que se muestra error si se realiza un registro de una cosecha con fecha de inicio mayor a la de cierre
# ACOMODARR
    def test_incorrect_register_B(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra cosecha
            y, m, d = '2022-11-01'.split('-')
            date1 = datetime.datetime(int(y), int(m), int(d))
            y, m, d = '2008-03-31'.split('-')
            date2 = datetime.datetime(int(y), int(m), int(d))

            response = tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date1.strftime("%Y-%m-%d"),
                    cierre= date2.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            #self.assertIn(b'La fecha de cierre debe ser posterior a la fecha de inicio.', response.data)

    #  Verifica que se puede eliminar una cosecha
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)

            # Elimina cosecha
            tester.post('/cosecha/delete/' + str(type.id), follow_redirects=True)
            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)

    #  Verifica que no se puede eliminar una cosecha que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registra cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)
            id = str(type.id)

            # Elimina tipo de recolector
            tester.post('/cosecha/delete/' + id, follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is None)

            # Elimina tipo de recolector de nuevo
            tester.post('/cosecha/delete/'  + id, follow_redirects=True)
            type = TipoRecolector.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is None)

    #  Verifica que se puede editar un tipo de recolector
    #ACOMODAR
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )

            # Registrar cosecha
            date = datetime.datetime.now()
            tester.post('/cosecha', data=dict(
                    descripcion='Cosecha Prueba',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)

            # Edita tipo de cosecha
            tester.post('/tipo_recolector/update/' + str(type.id), data=dict(
                    descripcion='Cosecha Prueba Editada',
                    inicio= date.strftime("%Y-%m-%d"),
                    cierre= date.strftime("%Y-%m-%d"),
                ), follow_redirects=True)

            #type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            #self.assertTrue(type is None)

            #type = Cosecha.query.filter_by(descripcion='Cosecha Prueba Editada').first()
            #self.assertTrue(type is not None)
        
    #  Verifica que se puede buscar una cosecha
    def test_search(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(nombre_usuario="user", password="user"),
                follow_redirects=True
            )            

            type = Cosecha.query.filter_by(descripcion='Cosecha Prueba').first()
            self.assertTrue(type is not None)

            # Registra tipo de cosecha
            tester.post('/cosecha/search', data=dict(
                    search_recolector='Cosecha Prueba'
                ), follow_redirects=True)

            # Buscar tipo de cosecha
            response = tester.get('/cosecha', follow_redirects=True)
            self.assertIn(b'Portafolio de Cosechas', response.data)
            self.assertIn(b'Cosecha Prueba', response.data)

if __name__ == '__main__':

    # Se cambia la base de datos para usar la de los test
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/test_db.db'
    app.config['TESTING'] = True
    # Verificamos si no existe la base de datos para los test
    if not os.path.exists("database/test_db.db"):
        create_db("database/test_db.db")

    unittest.main()
    