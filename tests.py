import unittest 
from app import app

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

    # Verifica que las páginas cargan correctamente
    def test_page_loads(self):
        tester = app.test_client(self)

        response = tester.get('/')
        self.assertIn(b'Bienvenido', response.data)

        response = tester.get('/login')
        self.assertIn(b'Iniciar', response.data)

    # Verifica que /portafolio y /logout requieren de haber iniciado sesión
    def test_route_requires_login(self):
        tester = app.test_client()
        response = tester.get('/perfiles', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)

        response = tester.get('/portafolio', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)

        response = tester.get('/logout', follow_redirects=True)
        self.assertIn(b'Necesitas iniciar ', response.data)
    
    # --------------------------------------------------------------------------
    # Autenticar usuarios
    # --------------------------------------------------------------------------

    # HAY QUE MODIFICAR LOS COMENTADOS

    # Verifica que el login funciona correctamente cuando se dan las credenciales correctas
    # def test_correct_login(self):
    #     tester = app.test_client()
    #     response = tester.post(
    #         '/login',
    #         data=dict(username="admin", password="admin"),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Te has conectado', response.data)

    # Verifica que el login funciona correctamente cuando se dan las credenciales incorrectas
    # def test_incorrect_login(self):
    #     tester = app.test_client()
    #     response = tester.post(
    #         '/login',
    #         data=dict(username="wrong", password="wrong"),
    #         follow_redirects=True
    #     )
    #     self.assertIn(b'Invalid Credentials. Please try again.', response.data)
    
    # Verifica que el logout funciona correctamente
    # def test_logout(self):
    #     tester = app.test_client()
    #     tester.post(
    #         '/login',
    #         data=dict(username="admin", password="admin"),
    #         follow_redirects=True
    #     )
    #     response = tester.get('/logout', follow_redirects=True)
    #     self.assertIn(b'You were logged out', response.data)

    # --------------------------------------------------------------------------
    # Crear perfiles de usuarios
    # --------------------------------------------------------------------------

    # Verifica que el registro funciona correctamente

    # Verifica que se muestra error si se realiza un registro incorrecto

    # Verificar que el registro se guarda en la database

if __name__ == '__main__':
    unittest.main()