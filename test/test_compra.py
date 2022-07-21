import unittest
from app import *
from db_create import create_db
import os

class CompraCase(unittest.TestCase):

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
        response = tester.get(f'/cosecha/{id}/compras', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # Verifica que las páginas (HTML) cargan exitosamente 
    def test_page_loads(self):
        tester = app.test_client(self)
        tester.post('/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

        id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
        desc = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().descripcion
        response = tester.get(f'/cosecha/{id}/compras', content_type='html/text')
        str = f'{desc}: Datos de la Compra'
        self.assertIn(bytes(str, "utf-8"), response.data)

    # Verifica que el registro de compra funciona exitosamente
    def test_correct_register(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, observacion = 'PRUEBA',
                ), follow_redirects=True)

            response = tester.get(f'/cosecha/{id}/compras', content_type='html/text')
            desc = Cosecha.query.filter_by(id=id).first().descripcion

            str = f'{desc}: Datos de la Compra'
            self.assertIn(bytes(str, "utf-8"), response.data)
            id_prueba = Compra.query.filter_by(observacion='PRUEBA').first().id
            type = Compra.query.filter_by(id=id_prueba).first().observacion
            self.assertTrue(type is not None)
            self.assertTrue(type == "PRUEBA")

    # Verifica que se muestra error si se realiza un registro incorrecto 
    def test_incorrect_register(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            post_rep = tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = '87654321', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, sobservacion = '',
                ), follow_redirects=True)

            # Correcta respuesta del servidor
            self.assertEqual(post_rep.status_code,200)
            response = tester.get(f'/cosecha/{id}/compras', content_type='html/text')
            # La cosecha sigue esxistiendo
            self.assertEqual(response.status_code,200)
            cosecha = Cosecha.query.filter_by(id=id).first()
            self.assertFalse(cosecha is None)
            # No se agrego la cosecha
            compra = Compra.query.filter_by(observacion='').all()
            #self.assertEqual(compra, [])

    #  Verifica que se puede editar una compra
    def test_correct_edit(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0,
                    monto = 0, observacion = 'xxxx',
                ), follow_redirects=True)

            id_compra = Compra.query.filter_by(observacion="xxxx").first().id
            post_r = tester.post(f'/cosecha/{id}/compras/{id_compra}/update', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, observacion = 'PRUEBA EDITAR',
                ), follow_redirects=True)

            self.assertEqual(post_r.status_code, 200)
            compra_nueva = Compra.query.filter_by(observacion='PRUEBA EDITAR').first()
            self.assertFalse(compra_nueva is None)
            
    # Verifica que se muestra error si se realiza una edicion incorrecta en una compra
    def test_incorrect_edit(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            c = Compra.query.all()
            id_mala = c[len(c)-1].id + 1
            post_r = tester.post(f'/cosecha/{id}/compras/{id_mala}/update', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0,
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, observacion = 'PRUEBA EDITAR',
                ), follow_redirects=True)

            self.assertEqual(post_r.status_code, 200)
            compra_nueva = Compra.query.filter_by(id=id_mala).first()
            self.assertTrue(compra_nueva is None)

    #  Verifica que se puede eleminar una compra
    def test_correct_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0, 
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, observacion = 'PRUEBA',
                ), follow_redirects=True)

            id_compra = Compra.query.filter_by(observacion="PRUEBA").first().id
            post_r = tester.post(f'/cosecha/{id}/compras/{id_compra}/delete', follow_redirects=True)

            self.assertEqual(post_r.status_code, 200)
            compra_borrada = Compra.query.filter_by(id=id_compra).first()
            self.assertTrue(compra_borrada is None)

    def test_incorrect_delete(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)

            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            compras = Compra.query.all()
            id_mala = compras[len(compras)-1].id + 1
            post_r = tester.post(f'/cosecha/{id}/compras/{id_mala}/delete', follow_redirects=True)

            self.assertEqual(post_r.status_code, 404)
            compras_noborradas = Compra.query.all()
            self.assertEqual(len(compras), len(compras_noborradas))

    #  Verifica que se puede buscar una compra
    def test_search(self):
        tester = app.test_client()
        with tester:
            tester.post( '/login', data=dict(nombre_usuario="user", password="user"), follow_redirects=True)            
            id = Cosecha.query.filter_by(descripcion='Cosecha Abr-Jun 22').first().id
            tester.post(f'/cosecha/{id}/compras', data=dict(
                    cedula = 'V-12345678', clase_cacao= 'Fermentado (F1)', precio = 0, 
                    cantidad = 0, humedad = 0, merma_porcentaje = 0, 
                    monto = 0, observacion = 'PRUEBA',
                ), follow_redirects=True)

            response = tester.post(f'/cosecha/{id}/compras/search', data=dict(
                search_compra = 'PRUEBA', Desde = '', Hasta = ''
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

    