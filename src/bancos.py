from flask import flash, redirect, url_for, request, render_template, session
from app import app, db
from src.models import Banco
from src.decoradores import login_required

@app.route('/bancos', methods=['GET'])
@login_required
def bancos():
    """ Logger de transacciones bancarias """
    bancos = Banco.query.all()

    return render_template('banco.html', bancos=bancos)