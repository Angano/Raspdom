import inspect

from config import app, db
from forms import ComposantForm,GpioForm, Composant2Form, CompteurForm, CompteurComposantForm
from flask import render_template, request, redirect, url_for, jsonify
from models import Composant, Gpio, Status, ConfigBcm,Compteur
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

#### ----- Composant --- #####
@app.route('/composant')
def composant():
    choices = list()
    apps = list()

    for name, obj in inspect.getmembers(Composants):

        if inspect.isclass(obj):
            try:
                if obj.enable:
                    choices.append(name)
            except:
                print('no label')


    for name, obj in inspect.getmembers(Appareils):

        if inspect.isclass(obj):
            try:
                if obj.enable:
                    apps.append({
                        'label':name,
                        'repr':obj.__repr__(obj),
                        'obj':obj
                    })
            except Exception as e:
                print(e,'no label')

    return render_template('composant/composant.html',choices=choices, apps=apps)

@app.route('/composants')
def composants():
    composant = Composant.query.all()
    return render_template('composant/composants.html',composants=composant)


@app.route('/composant/add', methods=['get','post'])
def composant_add():
    instances = list()
    # labels = [(data.categorieappareil, globals()[data.categorieappareil].label.__doc__) for data in appareils]
    #for composant in composants:
    #    instances.append({'modelAppareil': appareil, 'instanceAppareil': (globals()[appareil.categorieappareil])})
    form = ComposantForm(request.form)
    if form.validate_on_submit():
        composant = Composant()
        form.populate_obj(composant)
        instance_composant = globals()[form.categoriecomposant.data]
        composant.nbre_gpio = instance_composant.sortie + instance_composant.entre
        composant.modele = instance_composant.label.__doc__
        composant.description = instance_composant.categoriecomposant
        composant.unite = instance_composant.unite
        #composant.categoriecomposant = instance_composant.categoriecomposant
        db.session.add(composant)
        db.session.commit()

        if instance_composant.gpio:
            return redirect(url_for('composant_edit', id=composant.id))
        else:
            reload()
        return redirect(url_for('composants',))


    return render_template('composant/composant_add.html', form=form)


@app.route('/composants/add',methods=['post'])
def composant_add2():
    form = Composant2Form()
    instance_composant = globals()[request.form.get('composant')]

    if instance_composant:
        if not form.gpios and instance_composant.gpio:

            for i in range(instance_composant.entre):
                gpioform = GpioForm()
                gpioform.mode = 'Input'
                print(Gpio.query.all())
                gpioform.nom = helpers.nameIO('Input',instance_composant.entre,Gpio.query.all())[i]

                try:
                    gpioform.info = instance_composant.infos_entre[i]
                except:
                    gpioform.info = ''
                form.gpios.append_entry(gpioform)

            for i in range(instance_composant.sortie):
                gpioform = GpioForm()
                gpioform.mode = 'Output'
                gpioform.nom = helpers.nameIO('Output',instance_composant.entre,Gpio.query.all())[i]

                try:
                    gpioform.info = instance_composant.infos_sortie[i]
                except:
                    gpioform.info = ''
                form.gpios.append_entry(gpioform)

        if instance_composant.compteur or True:
            compteurform = CompteurForm()
            form.compteur.append_entry(compteurform)

    return render_template('composant/composant_add2.html',form=form, instance_composant=instance_composant)

@app.route('/composant/add/confirm',methods=['post'])
def composant_confirm_add():
    composant = Composant()
    instance_composant = globals()[request.form.get('categoriecomposant')]
    composant.categoriecomposant = instance_composant.__name__
    composant.description = instance_composant.categoriecomposant
    composant.unite = instance_composant.unite
    composant.modele = instance_composant.label.__doc__
    form = Composant2Form(request.form)
    if form.validate_on_submit():

        composant.description = instance_composant.categoriecomposant

        #db.session.add(composant)
        gpios = list()
        gpios_list = Gpio.query.order_by('mode','nom').all()
        if instance_composant.gpio:

            gpios_order = list()

            c_input = 0
            c_output = 0
            for data in form.gpios.data:
                gpioform = GpioForm()
                if data['mode'] == 'Input':
                    gpioform.nom.data = helpers.nameIO(data['mode'], instance_composant.entre, gpios_list)[c_input]
                    c_input += 1
                elif data['mode'] == 'Output':
                    gpioform.nom.data = helpers.nameIO(data['mode'], instance_composant.sortie, gpios_list)[c_output]
                    c_output += 1

                #gpioform.nom.data = data['nom']

                gpioform.mode.data = data['mode']
                gpioform.valeur.data = data['valeur']
                gpioform.info.data = data['info']
                gpio = Gpio()
                gpio.configbcm_used_in = ConfigBcm.query.filter_by(name=data['valeur']).first().id
                gpios_order.append(data['valeur'])
                gpio.composant_id = composant.id

                if gpioform.validate_on_submit():
                    gpioform.populate_obj(gpio)

                    gpios.append(gpio)
                    db.session.add(gpio)


            composant.order_gpio = json.dumps(gpios_order)

        if instance_composant.compteur:
            compteur = Compteur()
            compteur.configbcm_id = request.form.get('compteur-0-configbcm_id')
            compteur.name = request.form.get('compteur-0-name')
            db.session.add(compteur)
            db.session.commit()
            composant.compteur = compteur.id


    composant.gpios = gpios
    db.session.add(composant)
    db.session.commit()
    reload()
    #form.populate_obj(composant)

    #db.session.commit()

    return redirect(url_for('composants'))

@app.route('/composant/<int:id>/delete')
def composant_delete(id):
    composant = Composant.query.get(id)
    db.session.delete(composant)
    db.session.commit()
    reload()

    return redirect('/composants')

@app.route('/composant/<int:id>/edit', methods=['get','post'])
def composant_edit(id):
    composant = Composant.query.get(id)

    form = ComposantForm(obj=composant, data=request.form)
    instance_composant = globals()[composant.categoriecomposant](composant)
    gpios_order = ''

    if form.validate_on_submit():
        if instance_composant.gpio:
            gpios_delete = Gpio.query.filter_by(composant_id=id).all()
            gpios_order = list()
            for data in gpios_delete:
                db.session.delete(data)
                db.session.commit()

            for data in form.gpios.data:
                gpioform = GpioForm()

                gpioform.nom.data = data['nom']
                gpioform.mode.data = data['mode']
                gpioform.valeur.data = data['valeur']
                gpioform.info.data = data['info']
                gpio = Gpio()
                gpios_order.append(data['valeur'])
                gpio.composant_id = id
                if gpioform.validate_on_submit():
                    gpioform.populate_obj(gpio)
                    gpio = data['nom']
                    db.session.add(gpio)
                    db.session.commit()
        form.populate_obj(composant)
        composant.description = instance_composant.categoriecomposant
        composant.order_gpio = json.dumps(gpios_order)
        db.session.add(composant)
        db.session.commit()
        reload()
        return redirect('/composants')

    if instance_composant:
        if not form.gpios:

            for i in range(instance_composant.entre):
                gpioform = GpioForm()
                gpioform.mode = 'Input'

                gpioform.nom = ''

                try:
                    gpioform.info = instance_composant.infos_entre[i]
                except:
                    gpioform.info = ''
                form.gpios.append_entry(gpioform)

            for i in range(instance_composant.sortie):
                gpioform = GpioForm()
                gpioform.mode = 'Output'
                gpioform.nom=''

                try:
                    gpioform.info = instance_composant.infos_sortie[i]
                except:
                    gpioform.info = ''
                form.gpios.append_entry(gpioform)

    reload()
    return render_template('composant/edit.html', form=form)

@app.route('/compteur/add', methods=['post'])
def compteur_add():
    form = CompteurForm(request.form)
    #instance_composant = globals()[request.form.get('composant')]
    compteur = Compteur()
    if form.validate_on_submit():
        form.populate_obj(compteur)
        """compteur.actived = bool(request.form.get('actived'))
        compteur.name = request.form.get('name')"""
        #compteur.gpio = ConfigBcm.query.get(request.form.get('gpio'))

        db.session.add(compteur)
        db.session.commit()
        reload()
    else:
        print('error',form.errors)
    return render_template('/compteur/add.html',form=form)

@app.route('/compteurs')
def compteurs():
    compteurs = Compteur.query.all()
    return render_template('compteur/compteurs.html', compteurs=compteurs)

@app.route('/api/compteur/getValues')
def api_compteur_getValues():
    datas = [(compteur.id, compteur.valeur,compteur.moyenne) for compteur in Compteur.query.all() ]
    tab = list()
    for data in datas:
        tab.append({
            'id_compteur':data[0],
            'valeur':data[1],
            'moyenne':data[2]

        })

    return jsonify(tab)
