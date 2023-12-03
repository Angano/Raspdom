import re, os

from config import app, db
from forms import ComposantForm,GpioForm, Composant2Form, CompteurForm
from flask import render_template, request, redirect, url_for
from models import Composant, Gpio, Status, ConfigBcm,Compteur, Appareil, Valeur, Sonde
import Composants
import Appareils
from Composants import *
import json, helpers
from flask import jsonify

@app.route('/api/composants')
def api_composants():
    composants = Composant.query.all()

    datas = dict()
    for composant in composants:
        datas[composant.id]=composant.valeur

    return jsonify(datas)

@app.route('/api/valeurs')
def api_valeurs():
    valeurs = Valeur.query.all()
    datas = list()
    for valeur in valeurs:
        val_temp = {
            'id_valeur':valeur.id,
            'session': valeur.val,
            'consigne': valeur.consigne,
            'min': valeur.min,
            'max': valeur.max,
            'cumul': valeur.valeur_cumule,
            'actived': valeur.actived,
            'composant_id':valeur.titi.id,
            'appareil_id':valeur.toto.id,
            'composant_valeur':valeur.titi.valeur,
            'valeur':valeur.val,
            'unite':valeur.unite
        }

        datas.append(val_temp)

    return jsonify(datas)


@app.route('/api/valeur/update',methods=['post'])
def api_valeur_update():

    valeur_id= request.form.get('valeur_id')

    valeur = Valeur.query.get(int(valeur_id))

    valeur_name = request.form.get('valeur_name')
    valeur_valeur = request.form.get('valeur_valeur')

    if valeur_name == 'init':
        valeur_valeur = bool(request.form.get('valeur_valeur'))
    else:
        valeur_valeur = request.form.get('valeur_valeur')

    if valeur_name == 'actived':
        if valeur.actived == True:
            valeur_valeur = False
        else:
            valeur_valeur = True


    valeur = Valeur.query.get(int(valeur_id))

    setattr(valeur,valeur_name,valeur_valeur)
    db.session.add(valeur)
    db.session.commit()


    return 'nice'

@app.route('/api/sonde',methods=['post'])
def api_sonde_update():
    id = request.form.get('sonde')
    regex = r"(^\d+$)"
    if re.match(regex,id) is not None:
        sonde = Sonde.query.get(id)

        if sonde is not None:
            if sonde.en_service == True:
                sonde.en_service = False
            else:
                sonde.en_service = True
            db.session.add(sonde)
            db.session.commit()

            return str(sonde.en_service)
        else:
            return 'La sonde n\'existe pas'
    else:
        return 'bug'
