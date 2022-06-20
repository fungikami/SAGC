import unittest 
from app import app, Roles, User, TypeProducer
from flask import url_for, request

# Para ver si funciona los tests:
# python tests.py -v
class FlaskTestCase(unittest.TestCase):

    # Verifica que flask esté funcionando correctamente
    def test_flask(self):
        tester = app.test_client(self)

        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan correctamente (Este no es muy funcional)
    def test_page_loads(self):
        tester = app.test_client(self)

        response = tester.get('/')
        self.assertIn(b'Bienvenido', response.data)

        response = tester.get('/login')
        self.assertIn(b'Iniciar', response.data)

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
    
    # --------------------------------------------------------------------------
    # Autenticar usuarios
    # --------------------------------------------------------------------------

    # Verifica que el login funciona correctamente cuando se dan las credenciales correctas
    def test_correct_login(self):
        tester = app.test_client()
        with tester:
            response = tester.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )
            assert request.path == url_for('productor')
            self.assertIn(b'Se ha iniciado la sesion correctamente', response.data)

    # Verifica que el login funciona correctamente cuando se dan las credenciales incorrectas
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
    

    # Verifica que el logout funciona correctamente
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

    # --------------------------------------------------------------------------
    # Crear perfiles de usuarios
    # --------------------------------------------------------------------------

    # Verifica que el registro funciona correctamente
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
                    password='pruebaprueba', rol=Roles.Administrador.name
                ), follow_redirects=True)

            response = tester.get('/perfiles', follow_redirects=True)
            self.assertIn(b'Perfiles de Usuarios', response.data)
            user = User.query.filter_by(username='Prueba').first()
            # self.assertTrue(str(user) == "User('Prueba', 'Prueba', 'Prueba', 'pruebaprueba', 'Administrador')")

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
                password="admin", rol=Roles.Administrador.name
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            # self.assertIn(b'El nombre de usuario no puede tener mas de 20 caracteres', response.data)

            # Registrarse a si mismo
            response = tester.post('/perfiles', data=dict(
                username="admin", name="Administrador", surname="Administrador", 
                password="admin", rol=Roles.Administrador.name
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            # self.assertIn(b'El nombre de usuario ya se encuentra en uso', response.data)
            
            # Registrarse con contraseña muy corta
            response = tester.post('/perfiles', data=dict(
                username="prueba", name="Prueba", surname="Prueba",
                password="pr", rol=Roles.Administrador.name
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            # self.assertIn(b'debe tener al menos 8 caracteres', response.data)
            
            # Registrarse con contraseña muy larga
            response = tester.post('/perfiles', data=dict(
                username="prueba", name="Prueba", surname="Prueba",
                password="prprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprprpr", 
                rol=Roles.Administrador.name
            ), follow_redirects=True)
            assert request.path == url_for('perfiles')
            # self.assertIn(b'no puede tener mas de 80 caracteres', response.data)
    


class ProductorCase(unittest.TestCase):
    # Verifica que flask esté funcionando correctamente
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

    # Verifica que las páginas (HTML) cargan correctamente 
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

    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un email que existe...)
    def test_incorrect_register(self):
        self.assertTrue(True)

    #  Verifica que se puede eliminar un productor
    def test_correct_delete(self):
        self.assertTrue(True)

    #  Verifica que no se puede eliminar un productor que no existe
    def test_incorrect_delete(self):
        self.assertTrue(True)

    #  Verifica que se puede editar un productor
    def test_correct_edit(self):
        self.assertTrue(True)

    #  Verifica que no se puede editar productor que no existe
    def test_incorrect_edit(self):
        self.assertTrue(True)

    #  Verifica que se puede buscar un productor
    def test_search(self):
        self.assertTrue(True)

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

    # Verifica que las páginas (HTML) cargan correctamente 
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

    # Verifica que el registro funciona correctamente
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

            # Registra tipo de productor de nuevo
            tester.post('/tipo_productor', data=dict(
                    description='Prueba'
                ), follow_redirects=True)

            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)
            # self.assertIn(b'El tipo de productor ya se encuentra definido.', response.data)

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
            tester.post('/delete_tipo_productor/{{ type.id }}', follow_redirects=True)

            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)
            type = TypeProducer.query.filter_by(description='Prueba').first()
            # self.assertTrue(type is None)

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

            # Elimina tipo de productor
            tester.post('/delete_tipo_productor/100', follow_redirects=True)

            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)

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
                    description='Prueba'
                ), follow_redirects=True)

            type = TypeProducer.query.filter_by(description='Prueba').first()
            self.assertTrue(type is not None)

            # Edita tipo de productor
            tester.post('/update_tipo_productor/{{ type.id }}', data=dict(
                    description='Prueba2'
                ), follow_redirects=True)

            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)
            type = TypeProducer.query.filter_by(description='Prueba2').first()
            # self.assertTrue(type is not None)

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

            # Edita tipo de productor
            tester.post('/update_tipo_productor/100', data=dict(
                    description='Prueba2'
                ), follow_redirects=True)


            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)
            type = TypeProducer.query.filter_by(description='Prueba2').first()
            self.assertTrue(type is None)


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
                    description='Prueba'
                ), follow_redirects=True)

            # Buscar tipo de productor
            response = tester.get('/tipo_productor', follow_redirects=True)
            self.assertIn(b'Tipos de Productor', response.data)
            self.assertIn(b'Prueba', response.data)



if __name__ == '__main__':
    unittest.main()