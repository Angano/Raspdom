import datetime

from config import app, db
from models import Tempo, Sonde, Historique, Composant, Historiquecomposant
from flask import render_template, url_for,redirect,request
from forms import TempoForm

from sqlalchemy import extract, and_

from flask import jsonify

@app.route('/dashboard/graph/tempSonde')
def dashboard_graph_temp_sonde():

    return render_template('graphique/index.html')

@app.route('/api/graph/tempSonde')
def api_graph_temp_sonde():

    sonde1 = Sonde.query.get(1)
    sonde2 = Sonde.query.get(2)

    datas = dict()
    datas['nom'] = sonde1.nom
    datas['nom2'] = sonde2.nom
    datas['info'] = sonde1.info
    datas['info2'] = sonde2.info

    date_releve = list()
    date2_releve = list()

    temp_releve = list()
    temp2_releve = list()

    for histo in sonde1.historiques:
        date_releve.append(histo.record_at)
        temp_releve.append(histo.valeur)

    for histo in sonde2.historiques:
        date2_releve.append(histo.record_at)
        temp2_releve.append(histo.valeur)

    datas['historique'] = {'date':date_releve, 'temp':temp_releve,'temp2':temp2_releve}
    return jsonify(datas)


@app.route('/dashboard/graph/test_tempSonde')
def test_dashboard_graph_temp_sonde():

    return render_template('graphique/test_index.html')

@app.route('/api/graph/test_tempSonde')
def test_api_graph_temp_sonde():

    sonde1 = Sonde.query.get(1)
    sonde2 = Sonde.query.get(2)

    datas = dict()
    datas['nom'] = sonde1.nom
    datas['nom2'] = sonde2.nom
    datas['info'] = sonde1.info
    datas['info2'] = sonde2.info

    date_releve = list()
    date2_releve = list()

    temp_releve = list()
    temp2_releve = list()

    for histo in sonde1.historiques[:10]:
        date_releve.append(histo.record_at)
        temp_releve.append(histo.valeur)

    for histo in sonde2.historiques[:10]:
        date2_releve.append(histo.record_at)
        temp2_releve.append(histo.valeur)

    datas['historique'] = {'date':date_releve, 'temp':temp_releve,'temp2':temp2_releve}
    return jsonify(datas)


@app.route('/api/graph/composant/<int:composant_id>')
def api_graph_composant(composant_id):
    datas = Composant.query.get(int(composant_id)).get_historique_for_api(start='2023-11-05',end='2023-11-11')

    return jsonify(datas)