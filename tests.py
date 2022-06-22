import unittest 
from app import app, Roles, User, TypeProducer, Producer
from flask import url_for, request

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

    # Verifica que /productor /perfiles /eventos y /logout requieren de haber iniciado sesión
    def test_route_requires_login(self):
        tester = app.test_client()
        response = tester.get('/perfiles', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)

        response = tester.get('/productor', follow_redirects=True)
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
                data=dict(username="admin", password="admin"),
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
                data=dict(username="", password=""),
                follow_redirects=True
            )
            assert request.path == url_for('login')
            self.assertIn(b'Todos los campos son obligatorios', response.data)

            # Usuario que no existe
            response = tester.post(
                '/login',
                data=dict(username="wrong", password="wrong"),
                follow_redirects=True
            )
            assert request.path == url_for('login')
            self.assertIn(b'Credenciales invalidas', response.data)

            # Usuario que existe, pero contraseña incorrecta
            response = tester.post(
                '/login',
                data=dict(username="admin", password="wrong"),
                follow_redirects=True
            )
            assert request.path == url_for('login')
            self.assertIn(b'Credenciales invalidas', response.data)
    
    # Verifica que el logout funciona exitosamente
    def test_logout(self):
        tester = app.test_client()
        tester.post(
            '/login',
            data=dict(username="admin", password="admin"),
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
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )
            
            # Registra perfil
            tester.post('/perfiles', data=dict(
                    username='Prueba', name='Prueba', surname='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )

            response = tester.get('/perfiles', follow_redirects=True)
            self.assertIn(b'Perfiles de Usuarios', response.data)
            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(user is not None)

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un user que ya existe, una contraseña mala...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )

            # Registro con usuario largo
            response = tester.post('/perfiles', data=dict(
                username="adminadminadminadminadmin", name="Administrador", surname="Administrador", 
                password="admin", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'El nombre de usuario no puede tener mas de 20 caracteres', response.data)

            # Registrarse a si mismo
            response = tester.post('/perfiles', data=dict(
                username="admin", name="Administrador", surname="Administrador", 
                password="admin", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'El nombre de usuario ya se encuentra en uso', response.data)
            
            # Registrarse con contraseña muy corta
            response = tester.post('/perfiles', data=dict(
                username="prueba", name="Prueba", surname="Prueba",
                password="pr", rol=1, cosecha=''
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            self.assertIn(b'debe tener al menos 8 caracteres', response.data)
            
            # Registrarse con contraseña muy larga
            response = tester.post('/perfiles', data=dict(
                username="prueba", name="Prueba", surname="Prueba",
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
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    username='Prueba', name='Prueba', surname='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(user is not None)

            # Elimina perfil
            response = tester.post('/deleteperfil/' + str(user.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)

            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(user is None)

    #  Verifica que no se puede eliminar un perfil que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    username='Prueba', name='Prueba', surname='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(user is not None)
            id = str(user.id)

            # Elimina perfil
            response = tester.post('/deleteperfil/' + str(user.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)
            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(user is None)

            # Elimina perfil que no existe
            tester.post('/deleteperfil/' + id, follow_redirects=True)
            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(user is None)

    #  Verifica que se puede editar un perfil
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    username='PruebaModificar', name='Prueba', surname='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = User.query.filter_by(username='PruebaModificar').first()
            self.assertTrue(user is not None)

            # Edita perfil
            response = tester.post('/updateperfil/' + str(user.id), data=dict(
                    username='PruebaModificar', name='Prueba2', surname='Prueba2',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            self.assertIn(b'Se ha modificado exitosamente.', response.data)

            user = User.query.filter_by(username='PruebaModificar', name='Prueba').first()
            self.assertTrue(user is None)

            user = User.query.filter_by(username='PruebaModificar', name='Prueba2').first()
            self.assertTrue(user is not None)

    #  Verifica que no se puede editar perfil que no existe
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    username='PruebaModificar', name='Prueba', surname='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = User.query.filter_by(username='PruebaModificar').first()
            self.assertTrue(user is not None)

            # Edita perfil con un username que ya existe
            response = tester.post('/updateperfil/' + str(user.id), data=dict(
                    username='admin', name='Prueba2', surname='Prueba2',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            self.assertIn(b'El nombre de usuario ya se encuentra en uso.', response.data)

            user = User.query.filter_by(username='Prueba2').first()
            self.assertTrue(user is not None)

    #  Verifica que se puede buscar un perfil
    def test_search(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )

            # Registra perfil
            tester.post('/perfiles', data=dict(
                    username='Prueba', name='Prueba', surname='Prueba',
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )
            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(user is not None)

            # Busca perfil
            response = tester.post('/search_perfil', data=dict(
                    search_perfil='Prueba'
                ), follow_redirects=True
            )
            self.assertIn(b'Prueba', response.data)

#----------------------------------------------------------------------------------------------------------------------
class ProductorCase(unittest.TestCase):
    # Verifica que flask esté funcionando exitosamente
    def test_flask(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(username="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/productor', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(username="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/productor')
        self.assertIn(b'Datos personales del Productor', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra productor
            tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is not None)

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un email que existe...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra productor
            tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is not None)

            # Registra productor con una cedula que ya existe
            response = tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba2', surname='Prueba2',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            self.assertIn(b'El productor con dicha cedula ya se encuentra registrado.', response.data)

            # Registra productor con un nombre largo
            response = tester.post('/productor', data=dict(
                cedula=33333333, name='Prueba3Prueba3Prueba3Prueba3Prueba3', surname='Prueba3',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            self.assertIn(b'El nombre y apellido no puede tener mas de 20 caracteres.', response.data)


    #  Verifica que se puede eliminar un productor
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra productor
            tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is not None)

            # Elimina productor
            response = tester.post('/delete_productor/' + str(prod.id), follow_redirects=True)
            self.assertIn(b'Se ha eliminado exitosamente.', response.data)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is None)

    #  Verifica que no se puede eliminar un productor que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra productor
            tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is not None)
            id = str(prod.id)

            # Elimina productor
            tester.post('/delete_productor/' + id, follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is None)

            # Elimina productor que no existe
            tester.post('/delete_productor/' + id, follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is None)

    #  Verifica que se puede editar un productor
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra productor
            tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is not None)

            # Edita productor
            response = tester.post('/update_productor/' + str(prod.id), data=dict(
                cedula=22222222, name='Prueba2', surname='Prueba2',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)

            self.assertIn(b'Se ha modificado exitosamente.', response.data)

            prod = Producer.query.filter_by(ci=22222222, name='Prueba').first()
            self.assertTrue(prod is None)

            prod = Producer.query.filter_by(ci=22222222, name='Prueba2').first()
            self.assertTrue(prod is not None)

    #  Verifica que no se puede editar productor que no existe
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra productor
            tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is not None)

            tester.post('/productor', data=dict(
                cedula=222222223, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod2 = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod2 is not None)

            # Edita productor 1 con la cédula del productor 2
            response = tester.post('/update_productor/' + str(prod.id), data=dict(
                cedula=222222223, name='Prueba2', surname='Prueba2',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)

            self.assertIn(b'El productor con dicha cedula ya se encuentra registrado.', response.data)
            prod2 = Producer.query.filter_by(ci=222222223, name='Prueba2').first()
            self.assertTrue(prod2 is None)

    #  Verifica que se puede buscar un productor
    def test_search(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra productor
            tester.post('/productor', data=dict(
                cedula=22222222, name='Prueba', surname='Prueba',
                telephone='12345678', phone='12345678',
                direction1='Calle falsa 123', direction2='Calle falsa 123',
                rol=1)
            , follow_redirects=True)
            prod = Producer.query.filter_by(ci=22222222).first()
            self.assertTrue(prod is not None)

            # Busca productor
            response = tester.post('/search_productor', data=dict(
                search_productor=22222222
            ), follow_redirects=True)

            self.assertIn(b'Prueba', response.data)

#----------------------------------------------------------------------------------------------------------------------
class TipoProductorCase(unittest.TestCase):
    def test_flask(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(username="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/tipo_productor', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)

        # Inicia Sesión
        tester.post(
            '/login',
            data=dict(username="user", password="user"),
            follow_redirects=True
        )

        response = tester.get('/tipo_productor')
        self.assertIn(b'Tipos de Productor', response.data)

    # Verifica que el registro funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de productor
            tester.post('/tipo_productor', data=dict(
                    description='Prueba'
                ), follow_redirects=True)

            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)
            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is not None)
            self.assertTrue(str(type) == "TypeProducer('Prueba')")

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un tipo de productor que ya existe, una descripción mala...)
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de productor
            tester.post('/tipo_productor', data=dict(
                    description='Prueba'
                ), follow_redirects=True)

            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is not None)           

            # Registra tipo de productor de nuevo
            response = tester.post('/tipo_productor', data=dict(
                    description='Prueba'
                ), follow_redirects=True)

            self.assertIn(b'El tipo de productor ya se encuentra definido.', response.data)

    #  Verifica que se puede eliminar un tipo de productor
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de productor
            tester.post('/tipo_productor', data=dict(
                    description='Prueba'
                ), follow_redirects=True)

            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is not None)

            # Elimina tipo de productor
            tester.post('/delete_tipo_productor/' + str(type.id), follow_redirects=True)
            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is None)

    #  Verifica que no se puede eliminar un tipo de productor que no existe
    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de productor
            tester.post('/tipo_productor', data=dict(
                    description='Prueba'
                ), follow_redirects=True)

            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is not None)
            id = str(type.id)

            # Elimina tipo de productor
            tester.post('/delete_tipo_productor/' + id, follow_redirects=True)
            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is None)

            # Elimina tipo de productor de nuevo
            tester.post('/delete_tipo_productor/'  + id, follow_redirects=True)
            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is None)

    #  Verifica que se puede editar un tipo de productor
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de productor
            tester.post('/tipo_productor', data=dict(
                    description='PruebaModificar'
                ), follow_redirects=True)

            type = TypeProducer.query.filter_by(description='PruebaModificar').first()
            self.assertTrue(type is not None)

            # Edita tipo de productor
            tester.post('/update_tipo_productor/' + str(type.id), data=dict(
                    description='PruebaModificar2'
                ), follow_redirects=True)

            # type = TypeProducer.query.filter_by(description='PruebaModificar').first()
            # self.assertTrue(type is None)

            type = TypeProducer.query.filter_by(description='PruebaModificar2').first()
            self.assertTrue(type is not None)

    #  Verifica que no se puede editar un tipo de productor que no existe
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            # Registra tipo de productor
            tester.post('/tipo_productor', data=dict(
                    description='Prueba'
                ), follow_redirects=True)
            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is not None)

            tester.post('/tipo_productor', data=dict(
                    description='Prueba2'
                ), follow_redirects=True)
            type2 = TypeProducer.query.filter_by(description='Prueba2').first()
            self.assertTrue(type2 is not None)

            # Edita tipo de productor a uno que ya se encuentra en uso
            response = tester.post('/update_tipo_productor/' + str(type.id), data=dict(
                    description='Prueba2'
                ), follow_redirects=True)

            self.assertIn(b'El tipo de productor ya se encuentra definido.', response.data)

    #  Verifica que se puede buscar un tipo de productor
    def test_search(self):
        tester = app.test_client()
        with tester:
            # Inicia Sesión
            tester.post(
                '/login',
                data=dict(username="user", password="user"),
                follow_redirects=True
            )

            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is not None)

            # Registra tipo de productor
            tester.post('/search_tipo_productor', data=dict(
                    search_productor='Prueba'
                ), follow_redirects=True)

            # Buscar tipo de productor
            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)
            self.assertIn(b'Prueba', response.data)

if __name__ == '__main__':
    unittest.main()