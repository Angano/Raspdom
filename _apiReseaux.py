from config import app, db
from forms import ComposantForm,GpioForm, Composant2Form, CompteurForm
from flask import render_template, request, redirect, url_for, jsonify
from models import Composant, Gpio, Status, ConfigBcm,Compteur
import Composants
import Appareils
from Composants import *
import json, helpers
import os,re

@app.route('/api/config/reseaux',methods=['get','post'])
def api_config_reseaux():
    ordre = request.form.get('ordre')
    ssid = re.sub(r"[ ]{1}",'\ ',request.form.get('ssid'))

    if ordre == 'disconnect':
        ordre = 'down'
    elif ordre == 'connect':
        ordre = 'up'
    else:

        return False
    #os.popen('nmcli c """ordre""" """ssid"""')
    s = f" nmcli c {ordre} {ssid} "
    try:
        if os.popen(s).errors:

            return "True"
        else:
            pass
    except:
        pass
        return "False"

# gestion du réseau wifi
@app.route('/config/reseaux')
def config_reseaux():
    wifi = os.popen('nmcli device wifi').read().split('\n')
    wifi.pop(0)

    datas = list()
    for line in wifi:
        line.rstrip()
        if line != "":
            data = re.sub(r"[ ]{2,99}", '###', line).split('###')
            datas.append(data)
    return render_template('/config/reseaux.html', wifi=datas)

@app.route('/api/test/reseau')
def api_test_reseau():
    tab = list()

    texte = re.sub('\n\n', '\n#1#\n', os.popen('nmcli device show').read()).split('#1#')

    for bloc in texte:
        item = dict()
        for line in bloc.split('\n'):
            try:
                item[line.split(':')[0]] = re.sub(r"[\ ]{2,99}",'',line.split(':')[1].rstrip())
            except:
                pass
        tab.append(item)
    return jsonify(tab)