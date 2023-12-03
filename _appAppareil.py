import inspect
import glob
from flask import jsonify
import datetime

from config import app, db
from forms import ComposantForm,GpioForm, Composant2Form, CompteurForm, App2Form, AppareilForm, SondeForm, TempoForm
from flask import render_template, request, redirect, url_for
from models import Composant, Gpio, Status, ConfigBcm,Compteur, Appareil, Sonde, ModeDeMarche, Valeur, Tempo
import Composants
import Appareils
from Composants import *
import json, helpers


def reload():
    #status = Status.query.get(1)
    status = Status.query.filter(Status.identifiant=='reload_config').first()
    if status == None:
        status = Status()
        status.identifiant='reload_config'
    status.status = True
    db.session.add(status)
    db.session.commit()
    return  True


@app.route('/appareil3',methods=['POST','GET'])
def edit_appareil3():
    appareil_id = request.args.get('appareil')


    list_app = dict()

    for name, obj in inspect.getmembers(Appareils):
        if inspect.isclass(obj):
            try:
                if obj.__module__ == 'Appareils':
                    list_app[obj.__name__]=obj
            except:
                print('no label')
    appps = list_app[appareil_id]
    datas = {
        'repr':appps.__repr__(appps),
        'label':appps.__name__,
        'objet': appps
         }

    # Attribution des GpioForm
    form = AppareilForm()

    if form.gpios.data.__len__()==0:


        for data in range(appps.entre):
            gpioform = GpioForm()
            gpioform.mode = 'Input'
            gpioform.info = appps.infos_entre[data]
            form.gpios.append_entry(gpioform)

        for data in range(appps.sortie):
            gpioform = GpioForm()
            gpioform.mode = 'Output'
            gpioform.info = appps.infos_sortie[data]
            form.gpios.append_entry(gpioform)

    # Attribution SondeForm
    sondeform = SondeForm()


    #exit()
    #appareil = Appareil.query.get(appareil_id)
    #instance_appareil = globals()[appareil.categorieappareil](appareil_id)
    #form = App2Form()

    composants = Composant.query.order_by('categoriecomposant').all()
    if form.validate_on_submit():
        appareil = Appareil()
        mode_de_marche = ModeDeMarche()
        mode_de_marche.mode_de_marche = 'off'
        appareil.mode_de_marche = mode_de_marche
        appareil.label  = appps.label.__doc__
        appareil.nbre_gpio = appps.entre+appps.sortie
        appareil.nom = form.nom.data
        appareil.categorieappareil = request.form.get('appareil')
        gpios = list()
        gpios_order = list()
        #####################""
        c_input = 0
        c_output = 0
        allGpios = Gpio.query.order_by('mode', 'nom').all()
        ######################
        for data in form.gpios.data:
            gpio = Gpio()
            gpio.mode = data['mode']
            gpio.valeur = data['valeur']
            gpio.configbcm_used_in = ConfigBcm.query.filter_by(name=data['valeur']).first().id
            gpios_order.append(data['valeur'])

            if data['mode'] == 'Input':
                gpio.nom = helpers.nameIO(data['mode'], appps.entre, allGpios)[c_input]
                gpio.info = appps.infos_entre[c_input]
                c_input += 1

            elif data['mode'] == 'Output':
                gpio.nom = helpers.nameIO(data['mode'], appps.sortie, allGpios)[c_output]
                gpio.info = appps.infos_sortie[c_output]

                c_output += 1


            gpios.append(gpio)

        appareil.order_gpio = json.dumps(gpios_order)

        appareil.gpios = gpios
        if appps.sonde:
            appareil.sonde_actived = form.sonde_actived.data
            appareil.description = form.description.data
            if form.sonde_id.data != '0':
                appareil.sonde_id = form.sonde_id.data
                #appareil.sonde = form.sonde.data
                #appareil.sonde_id = Sonde.query.get(form.sonde_id.data)

        if appps.composant == True:
            ## sequence validation requette

            composants = [(Composant.query.get(value)) for key, value in request.form.to_dict().items() if
                          'composant_' in key]

            appareil.composants = composants[0]


            resultok = True
            if appps.composant_categorie.__len__()!=composants.__len__():
                print(appps.composant_categorie,composants[0].description)
                #resultok = False
                print('L137')


            for composant in composants:

                if composant.description not in appps.composant_categorie:
                        resultok = False
                        print('L142')

            if resultok == False:

                return redirect(request.url)

        #######
        if appps.tempo:
            tep = Tempo()
            tep.consigne = float(5.5)
            tep.start_at = datetime.datetime.now()
            appareil.tempos = tep

        ####
        db.session.add(appareil)
        db.session.commit()
        reload()
        ### Séquence création valeur pour le composant et l'appareil donné
        """
        for composant in composants:
            valeur = Valeur()
            valeur.appareil_id = appareil.id
            valeur.composant_id = composant.id
            valeur.consigne = 10.0
            valeur.val = 14.0
            valeur.min = 11.0
            valeur.max = 18.0
            valeur.actived = False
            valeur.unite = (globals()[composant.categoriecomposant].unite)
            db.session.add(valeur)
            # Détermination si le composant doit enregistrer 2 valeurs
            #print(instance_appareil = globals()[appareil.categorieappareil])
            if(globals()[composant.categoriecomposant].valeur2)== 0:
                valeur = Valeur()
                valeur.appareil_id = appareil.id
                valeur.composant_id = composant.id
                valeur.consigne = 10.0
                valeur.val = 14.0
                valeur.min = 11.0
                valeur.max = 18.0
                valeur.actived = False
                valeur.unite = (globals()[composant.categoriecomposant].unite2)
                db.session.add(valeur)
            

        #############"""
        db.session.commit()
        return redirect('/')
    else:
        print(form,'errrr')


    #return render_template('appareil/edit2.html', appareil=appareil, form=form, instance_appareil=instance_appareil)
    return render_template('appareil/edit3.html', instance_appareil=datas,appareil=None, form=form, composants=composants)


@app.route('/temp')
def temp():

    sondes = Sonde.query.all()
    datas = {}

    for sonde in sondes:
        datas[sonde.id] = {
            'temp':sonde.sonde_valeur_id.valeur,
            'nom':sonde.nom,
            'sonde_info':sonde.info
        }
    return(jsonify(datas))

@app.route('/api/getMore/<int:appareil_id>')
def getMore(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    gpios = [{
        'id':data.id,
        'mode':data.mode,
        'info':data.info,
        'nom':data.nom,
        'valeur':data.valeur} for data in appareil.gpios]

    datas = {
        'appareil_id':appareil.id,
        'description':appareil.description,
        'gpios': gpios,
        'nom':appareil.nom,
        'categorie':appareil.categorieappareil,
    }

    if appareil.tempos:
        datas['tempos'] = appareil.tempos.consigne
    return jsonify(datas)

@app.route('/api/update_consigne_tempo',methods=['post'])
def update_consigne_tempo():
    form = request.form

    appareil = Appareil.query.get(form['appareil'])
    appareil.tempos.consigne = form['consigne']
    db.session.commit()
    return 'Hello'