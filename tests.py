import unittest 
from app import app
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

    # Verifica que /portafolio /perfiles /eventos y /logout requieren de haber iniciado sesión
    def test_route_requires_login(self):
        tester = app.test_client()
        response = tester.get('/perfiles', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)

        response = tester.get('/portafolio', follow_redirects=True)
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
            assert request.path == url_for('portafolio')
            self.assertIn(b'Se ha iniciado la sesion correctamente', response.data)

    # Verifica que el login funciona correctamente cuando se dan las credenciales incorrectas
    def test_incorrect_login(self):
        tester = app.test_client()
        with tester:
            response = tester.post(
                '/login',
                data=dict(username="wrong", password="wrong"),
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
    # def test_user_registeration(self):
    #     with self.client:
    #         response = self.client.post('register/', data=dict(
    #             username='Michael', email='michael@realpython.com',
    #             password='python', confirm='python'
    #         ), follow_redirects=True)
    #         self.assertIn(b'Welcome to Flask!', response.data)
    #         self.assertTrue(current_user.name == "Michael")
    #         self.assertTrue(current_user.is_active())
    #         user = User.query.filter_by(email='michael@realpython.com').first()
    #         self.assertTrue(str(user) == '<name - Michael>')


    # Verifica que se muestra error si se realiza un registro incorrecto (ya sea un user que ya existe, una contraseña mala...)
    # def test_incorrect_user_registeration(self):
    #     with self.client:
    #         response = self.client.post('register/', data=dict(
    #             username='Michael', email='michael',
    #             password='python', confirm='python'
    #         ), follow_redirects=True)
    #         self.assertIn(b'Invalid email address.', response.data)
    #         self.assertIn(b'/register/', request.url)

    

if __name__ == '__main__':
    unittest.main()