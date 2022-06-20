import unittest 
from app import app, Roles, User
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
    
    # Verifica que el login funciona correctamente cuando se dan las credenciales correctas
    def test_correct_login(self):
        tester = app.test_client()
        with tester:
            response = tester.post(
                '/login',
                data=dict(username="admin", password="admin"),
                follow_redirects=True
            )
            assert request.path == url_for('perfiles')
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

class PerfilesTestCase(unittest.TestCase):

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
                    password='Pruebaprueba1*', rol=1, cosecha=''
                ), follow_redirects=True
            )

            response = tester.get('/perfiles', follow_redirects=True)
            self.assertIn(b'Perfiles de Usuarios', response.data)
            user = User.query.filter_by(username='Prueba').first()
            self.assertTrue(str(user) == "User('Prueba', 'Prueba', 'Prueba', 'Pruebaprueba1*', '1')")

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

if __name__ == '__main__':
    unittest.main()