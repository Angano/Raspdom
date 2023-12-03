from config import app, db
from models import Tempo, Sonde, Historique
from flask import render_template, url_for,redirect,request
from forms import TempoForm

from flask import jsonify

@app.route('/tempos')
def tempos():
    tempos = Tempo.query.all()
    form = TempoForm()
    historiques = Historique.query.all()
    sondes = Sonde.query.all()
    return render_template('tempo/index.html', tempos=tempos,form=form, sondes=sondes,historiques=historiques)