import inspect
import json
from datetime import datetime, timedelta, time as toto
import Appareils
import os, time, re

from itertools import groupby
from operator import attrgetter


from config import app, db
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_required, login_user, \
                        logout_user, current_user

from forms import App2Form, UserForm, LoginForm, EditUserForm, AppareilForm, GpioForm, ProgrammationForm, ModeDeMarcheForm, SondeForm, Ds1820bForm, ReglageSondeForm
from models import User, Appareil, Gpio, Programmation, ModeDeMarche, Sonde, Manuel, Status, ValeurSonde, Mf, Composant, ConfigBcm
#from Appareils import Eclairage, ChauffageR, ChauffeEau, Pompe, Hygro, Contacteur2I, Demarreur_Etoile_Triangle
from Appareils import *

from Composants import *

import helpers

from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# recharchement liste des appareils

helpers.update_time()

# Création d'un admin
try:
    if User.query.filter(User.username=='admin').first()==None:
        user = User()
        user.username = 'admin'
        user.hash_password('admin')
        db.session.add(user)
        db.session.commit()
except:
    print('eeeeeeeeeeeeeeeeeeeeeeeerrrrrrorrrrr')
    pass


@login_manager.user_loader
def user_load(user_id):
    return User.query.get(user_id)

import _appComposant, _appConfigBcm, _appAppareil, _apiComposant, _apiReseaux, _appSystem, _appTempos, _appGraphique
from _appAppareil import reload

@app.route('/')
@login_required
def index():
    appareils = Appareil.query.all()
    # Récupération des instances des appareils en cours
    labels = dict()
    instances = list()
    #labels = [(data.categorieappareil, globals()[data.categorieappareil].label.__doc__) for data in appareils]
    for appareil in appareils:
        instances.append({'modelAppareil':appareil,'instanceAppareil':(globals()[appareil.categorieappareil])})

    gpios = Gpio.query.order_by('appareil_id').all()
    try:
        programmations = Programmation.query.order_by('appareil').all()
    except:
        programmations = []

    date_machine = Status.query.filter_by(identifiant='now_time').first().time_now
    print(date_machine)
    return render_template('index.html', date_machine=date_machine,appareils=appareils, gpios=gpios, programmations=programmations, instances=instances)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        flash(message='Vous êtes déjà conecté')
        return redirect(url_for('index'))

    loginform = LoginForm(request.form)
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if user and user.check_password(loginform.password.data):
            login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html', loginform=loginform)


@app.route('/profil')
@login_required
def profil():
    return render_template('profil.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/user', methods=['POST', 'GET'])
def user():
    userform = UserForm(request.form)
    if userform.validate_on_submit():
        user = User()
        userform.populate_obj(user)
        user.hash_password(userform.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users'))

    return render_template('user.html', userform=userform)


@app.route('/user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_user(user_id):
    user = User.query.get(user_id)
    userform = EditUserForm(obj=user, data=request.form)
    if userform.validate_on_submit():
        userform.populate_obj(user)
        db.session.add(user)
        return redirect(url_for('users'))
    return render_template('edit_user.html', userform=userform)


@app.route('/users')
@login_required
def users():
    users_list = User.query.all()
    return render_template('users.html', users=users_list)


@app.route('/user/delete/<int:user_id>', methods=['GET', 'POST'])
def user_delete(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))


# appareil
@app.route('/appareil', methods=['POST', 'GET'])
def appareil():
    appareilform = AppareilForm(request.form)
    mode_de_marcheform = ModeDeMarcheForm(request.form)

    if appareilform.validate_on_submit():
        appareil = Appareil()

        mode_de_marche = ModeDeMarche()

        appareilform.populate_obj(appareil)

        mode_de_marcheform.populate_obj(mode_de_marche)

        try :
            instance_appareil = globals()[appareilform.categorieappareil.data]
            appareil.nbre_gpio = instance_appareil.sortie+instance_appareil.entre

        except ValueError:
            print(ValueError)

        appareil.label = instance_appareil.label.__doc__
        db.session.add(appareil)
        db.session.commit()

        mode_de_marche.appareil_id=appareil.id
        db.session.add(mode_de_marche)
        db.session.commit()

        return redirect(url_for('edit_appareil', appareil_id=appareil.id))
    else:
        print(appareilform.errors)
    #appareilform.categorie_appareil_id.choices = [(data.id, data.nom) for data in Categorieappareil.query.all()]
    return render_template('appareil/appareil.html', appareilform=appareilform, mode_de_marcheform=mode_de_marcheform)



#######################""" 05-02-2023
@app.route('/appareil_add',methods=['get','post'])
def appareil_add2():

    return render_template('appareil/appareil_old.html')



###

#   """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
@app.route('/appareil2/<int:appareil_id>',methods=['POST','GET'])
@app.route('/appareil/<int:appareil_id>', methods=['POST','GET'])
def edit_appareil2(appareil_id):
    appareil = Appareil.query.get(appareil_id)

    #instance_appareil = globals()[appareil.categorieappareil](appareil_id)
    form = App2Form(obj=appareil, data=request.form)

    if form.validate_on_submit():

        appareil.sonde_actived = form.sonde_actived.data
        appareil.sonde_id = form.sonde_id.data

        appareil.nom = form.nom.data
        appareil.description = form.description.data

        #appareil.sonde = Sonde.query.get(form.sonde.data)

        db.session.add(appareil)
        db.session.commit()

        return redirect('/')
    else:
        print(form.errors,'errrr')
    return render_template('appareil/edit2.html', appareil=appareil, form=form)


#   """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""@app.route('/appareil/<int:appareil_id>', methods=['POST','GET'])
def edit_appareil(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    appareilform = AppareilForm(obj=appareil, data=request.form)
    gpios = Gpio.query.order_by('mode','nom').all()


    instance_appareil = globals()[appareil.categorieappareil](appareil)

    composants = Composant.query.filter(Composant.description.in_(instance_appareil.composant_categorie)).all()


    # création d'un dictionnaire pour passer la liste des composant au template
    list_composant = {}
    for composant in composants:

        if composant.description in list_composant:
            if composant.description not in list_composant[composant.description]:
                list_composant[composant.description].append(composant)
        else:

            list_composant[composant.description] = []
            list_composant[composant.description].append(composant)


    if appareilform.validate_on_submit():


        appareil.sonde_id = appareilform.sonde_id.data
        appareil.nom = appareilform.nom.data
        appareil.categorieappareil = appareilform.categorieappareil.data
        appareil.description = appareilform.description.data
        appareil.sonde_actived = appareilform.sonde_actived.data
        #appareil.mode_de_marche = appareilform.mode_de_marche.data
        gpios_delete = Gpio.query.filter_by(appareil_id=appareil_id).all()
        gpios_order = list()
        if appareil.sonde_id:
            #gpios_order.append('ds1820_'+str(sonde.id))
            gpios_order.append('ds1820_' + 'rien')
        for data in gpios_delete:
            db.session.delete(data)
            db.session.commit()

        c_input = 0
        c_output = 0
        for data in appareilform.gpios.data:
            gpioform = GpioForm()

            if data['mode']=='Input':
                gpioform.nom.data = helpers.nameIO(data['mode'], instance_appareil.sortie, gpios)[c_input]
                c_input += 1
            elif data['mode'] == 'Output':
                gpioform.nom.data = helpers.nameIO(data['mode'], instance_appareil.sortie, gpios)[c_output]
                c_output += 1

            gpioform.mode.data = data['mode']

            # Numérotation automatique des entrées et sorties



            gpioform.valeur.data = data['valeur']
            gpioform.info.data = data['info']
            gpio = Gpio()
            gpios_order.append(data['valeur'])
            gpio.appareil_id = appareil_id
            if gpioform.validate_on_submit():

                gpioform.populate_obj(gpio)
                gpio.configbcm_used_in = ConfigBcm.query.filter_by(name=data['valeur']).first().id
                db.session.add(gpio)
        if instance_appareil.composant:
            save_composant = []
            toto = request.form.to_dict()
            for titi in toto:

                mat = re.search(r"composants",titi)
                if mat:
                    save_composant.append(Composant.query.get(toto[titi]))



            appareil.composants = save_composant

        appareil.order_gpio = json.dumps(gpios_order)

        db.session.add(appareil)
        db.session.commit()

        if reload():
            print('reload')

        return redirect(url_for('appareils'))
    else:
        print(appareilform.errors)

    appareilform = AppareilForm(obj=appareil, data=request.form)

    #gpio_free = Gpio()
    #gpio_free = gpio_free.get_free_gpio()

    if not appareilform.gpios:

        if not instance_appareil.sonde:
            for i in range(instance_appareil.entre):
                gpioform = GpioForm()
                gpioform.mode = 'Input'
                # Numérotation automatique des entrées et sorties
                gpioform.nom = helpers.nameIO('Input',instance_appareil.entre,gpios)[i]

                try:
                    gpioform.info = instance_appareil.infos_entre[i]
                except:
                    gpioform.info = ''
                appareilform.gpios.append_entry(gpioform)

        for i in range(instance_appareil.sortie):
            gpioform = GpioForm()
            gpioform.mode = 'Output'
            # Numérotation automatique des entrées et sorties
            gpioform.nom=helpers.nameIO('Output',instance_appareil.sortie,gpios)[i]

            try:
                gpioform.info = instance_appareil.infos_sortie[i]
            except:
                gpioform.info = ''
            appareilform.gpios.append_entry(gpioform)

    if instance_appareil.sonde :

        #sonde = Sonde.query.filter_by(appareil=appareil.id).first()
        try:
            sonde = appareil.sonde_id
        except:
            sonde = Sonde()




    #appareilform.categorie_appareil_id.choices = [(data.id, data.nom) for data in Categorieappareil.query.all()]
    return render_template('appareil/appareil_edit.html', composants=composants, appareilform=appareilform, gpios=gpios, appareil=appareil, instance_appareil=instance_appareil, list_composant=list_composant)"""

@app.route('/appareils')
def appareils():
    appareils = Appareil.query.order_by('nom')
    return render_template('appareil/appareils.html', appareils=appareils)


@app.route('/appareil/delete/<int:appareil_id>')
def delete_appareil(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    gpios = Gpio.query.filter_by(appareil_id=appareil_id)
    if gpios != None:
        for gpio in gpios:
            db.session.delete(gpio)

    programmations = Programmation.query.filter_by(appareil_id=appareil_id)
    if programmations != None:
        for programmation in programmations:
            db.session.delete(programmation)

    mode_de_marches = ModeDeMarche.query.filter_by(appareil_id=appareil_id)
    if mode_de_marches != None:
        for mode_de_marche in mode_de_marches:
            db.session.delete(mode_de_marche)
    db.session.delete(appareil)
    db.session.commit()
    reload()
    return redirect(url_for('appareils'))


@app.route('/appareil/test/<int:appareil_id>', methods=['POST','GET'])
def test(appareil_id):
    # liste des appareils pour affichage
    appareils = Appareil.query.all()

    appareil = Appareil.query.get(appareil_id)
    programmations = Programmation.query.filter_by(appareil_id=appareil_id).order_by(Programmation.day).all()

    if appareil.sonde_id:
        sonde = appareil.appareil_sonde
        sondeform = ReglageSondeForm(obj=sonde,data=request.form)
        if sondeform.validate_on_submit():
            sondeform.populate_obj(sonde)

            db.session.add(sonde)
            db.session.commit()
            print('commit')
        else:
            print('no commi')

    else:
        sondeform = False
        print('no form')

    instance_appareil = globals()[appareil.categorieappareil](appareil)
    mode_de_marche = ModeDeMarche.query.filter_by(appareil_id=appareil_id).first()

    mode_de_marcheform = ModeDeMarcheForm(obj=mode_de_marche, data=request.form)
    mode_de_marcheform.mode_de_marche.choices = instance_appareil.choices_mdm

    if mode_de_marcheform.validate_on_submit():
        mode_de_marcheform.populate_obj(mode_de_marche)
        # si passage en mode test=>passage de l'ordre à l'arrêt
        if mode_de_marcheform.mode_de_marche.data == 'test':
            manuel = Manuel.query.filter_by(appareil_id=appareil_id).first()

            if manuel == None:
                manuel = Manuel()
                manuel.appareil_id = appareil_id
                manuel.ordre = 'arret'

            else:
                manuel.ordre = 'arret'
            db.session.add(manuel)
        db.session.add(mode_de_marche)

    db.session.commit()
    #reload()

    tab2 = []
    gpios = Gpio.query.all()
    for gpio in gpios:
        var = gpio.valeur.split('_')[1]

        try:
            data = os.popen(f'raspi-gpio get {var}')
            dati = data.read()

            mode = dati.find('func=') + 5
            popo = dati.find('level=')

            toto = {
                'gpio': dati[5:popo - 2],
                'mode': dati[mode:mode + 6],
                'level': dati[popo + 6],
                'info': gpio.info
            }
            tab2.append(toto)
        except:
            print('no ds1820b')

    tab = []
    for gpio in appareil.gpios:

        var = gpio.valeur.split('_')[1]
        print(var)
        try:
            data = os.popen(f'raspi-gpio get {var}')
            dati = data.read()

            mode = dati.find('func=')+5
            popo = dati.find('level=')

            toto = {
                'gpio':dati[5:popo-2],
                'mode':dati[mode:mode+6],
                'level':dati[popo+6],
                'info': gpio.info
            }
            tab.append(toto)
        except:
            print('no ds1820b')

    tab2 = []
    return render_template('appareil/appareil_test.html', tab=tab, tab2=tab2, sondeform=sondeform, appareils=appareils, appareil=appareil, instance_appareil=instance_appareil, mode_de_marcheform=mode_de_marcheform, modedemarche=instance_appareil.choices_mdm, programmations=programmations)


# GPIO
@app.route('/gpio', methods=['POST', 'GET'])
def gpio():
    gpio = Gpio()
    gpioform = GpioForm(request.form)
    if gpioform.validate_on_submit():
        gpioform.populate_obj(gpio)
        gpio.configbcm_used_in = ConfigBcm.query.filter_by(name=gpioform.valeur.data).first().id
        db.session.add(gpio)
        #db.session.commit()
        return redirect(url_for('gpios'))
    gpioform.valeur.choices = gpio.get_free_gpio()
    #gpioform.appareils.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('gpio/gpio.html', gpioform=gpioform)


@app.route('/gpios')
def gpios():
    gpios_list = Gpio.query.order_by('appareil_id', 'mode').all()

    return render_template('gpio/gpios.html', gpio_list=gpios_list)


@app.route('/gpio/<int:gpio_id>', methods=['POST', 'GET'])
def edit_gpio(gpio_id):
    gpio = Gpio.query.get(gpio_id)
    gpioform = GpioForm(obj=gpio, data=request.form)
       
    if gpioform.validate_on_submit():
        gpioform.populate_obj(gpio)
        #db.session.add(gpio)
        #db.session.commit()
        return redirect(url_for('gpios'))
    gpioform.valeur.choices = gpio.get_free_gpio() 
    #gpioform.appareils.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('gpio/gpio.html', gpioform=gpioform)


@app.route('/gpio/delete/<int:gpio_id>')
def delete_gpio(gpio_id):
    gpio = Gpio.query.get(gpio_id)
    #db.session.delete(gpio)
    #db.session.commit()
    return redirect(url_for('gpios'))


# Programmation
@app.route('/c', methods=['POST', 'GET'])
def add_programmation():
    programmation = Programmation()

    programmationform = ProgrammationForm(request.form)
    if programmationform.validate_on_submit():
        programmationform.populate_obj(programmation)
        db.session.add(programmation)
        db.session.commit()
        return redirect(url_for('liste_programmations'))
    else:
        print(programmationform.errors)
    programmationform.appareil_id.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('programmation/programmation.html', programmationform=programmationform)


@app.route('/programmations')
def liste_programmations():
    programmations = Programmation.query.all()
    programmations = Appareil.query.all()
    datas = [datetime.datetime.fromtimestamp(h*60).time() for h in range(-60,24*60-45,15)]

    datasH = [toto(hour=h) for h in range(0,24)]
    datasFake = {
        'start':toto(hour=3),
        'end':toto(hour=5,minute=17)
    }
    #tab = [(k,list(g)) for k, g  in groupby(programmations, attrgetter('appareil_programmation'))]

    return render_template('programmation/programmations.html', programmations=programmations, datas=datas, datasH=datasH, datasFake=datasFake)

@app.route('/programmation/delete/<int:programmation_id>')
def delete_programmation(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    db.session.delete(programmation)
    db.session.commit()
    return redirect(url_for('liste_programmations'))

@app.route('/programmation/edit/<int:programmation_id>', methods=['POST','GET'])
def edit_programmation(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    programmationform = ProgrammationForm(obj=programmation, data=request.form)
    programmations = Programmation.query.filter_by(appareil_id=programmation.appareil_programmation.id).all()

    if programmationform.validate_on_submit():
        programmationform.populate_obj(programmation)
        db.session.add(programmation)
        db.session.commit()
        return redirect(url_for('liste_programmations'))
    programmationform.appareil_id.choices = [(data.id, data.nom) for data in Appareil.query.all()]
    return render_template('programmation/programmation.html', programmationform=programmationform, programmations=programmations)


# mode test
@app.route('/test_app', methods=['post'])
def test_app():
    ordre = (request.form.get('data').split('_'))[0]
    appareil = Appareil.query.get(int((request.form.get('data').split('_'))[1]))
    try:
       data = Manuel.query.filter_by(appareil_id=appareil.id).first()
       if data is None:     
            data = Manuel()
            data.appareil_id = appareil

       data.ordre = ordre
       db.session.add(data)
       db.session.commit()
    except:
        print('bug l587')
    return 'tata'

# déclaration des sondes type ds1820b
@app.route('/sondes')
def sondes():
    sondes = Sonde.query.all()
    return render_template('sonde/sonde.html', sondes=sondes)

@app.route('/sonde/<int:sonde_id>', methods=['get','post'])
def edit_sonde(sonde_id):
    sonde = Sonde.query.get(sonde_id)
    sondeform = Ds1820bForm(obj=sonde, data=request.form)
    if sondeform.validate_on_submit():
        sondeform.populate_obj(sonde)
        db.session.add(sonde)
        db.session.commit()
        return redirect(url_for('sondes'))
    return render_template('sonde/edit_sonde.html', sondeform=sondeform, sonde=sonde)

# delete sonde
@app.route('/delete_sondes')
def delete_sonde():
    sondes = Sonde.query.all()

    for sonde in sondes:
        db.session.delete(sonde)
        try:
            db.session.delete(sonde.sonde_valeur_id)
        except:
            pass
    db.session.commit()
    return 'true'

## Add programmation by a appareil
@app.route('/programmation/add/<int:appareil_id>', methods=['post','get'])
def add_programmation_by_app(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    form = ProgrammationForm(obj=appareil)
    if form.validate_on_submit():
        programmation = Programmation()
        form.populate_obj(programmation)

        db.session.add(programmation)
        db.session.commit()

        return redirect(url_for('test',appareil_id=appareil.id))
    else:
        print(form.errors);

    return render_template('programmation/add_programmation_by_app.html', form = form, appareil_id=appareil_id)


## Add programmation by a appareil
@app.route('/api/programmation/add/<int:appareil_id>', methods=['post','get'])
def add_programmation_by_app_api(appareil_id):
    appareil = Appareil.query.get(appareil_id)
    datas = dict(request.form.lists())
    for day in datas['day']:

        programmation = Programmation()
        programmation.day = day
        programmation.start = datetime.time(
            hour=int(datas['start'][0]),
            minute=int(datas['start_min'][0])
        )

        programmation.end = datetime.time(
            hour=int(datas['end'][0]),
            minute=int(datas['end_min'][0])
        )
        programmation.appareil_id = appareil_id
        db.session.add(programmation)

    db.session.commit()



    return jsonify({"app_id":appareil_id})



# Delete programmation from appareil
@app.route('/appareil/programmation/delete/<int:programmation_id>')
def delete_programmation_from_appareil(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    db.session.delete(programmation)
    db.session.commit()
    return redirect(url_for('test',appareil_id=programmation.appareil_id))

# Edit programmation from appareil
@app.route('/appareil/programmation/edit/<int:programmation_id>', methods=['get','post'])
def edit_programmation_from_appareil(programmation_id):
    programmation = Programmation.query.get(programmation_id)
    form = ProgrammationForm(obj=programmation)
    if form.validate_on_submit():
        form.populate_obj(programmation)
        db.session.add(programmation)
        db.session.commit()
    return render_template('programmation/programmation.html',programmationform=form)



@app.route('/api/programmation/<int:id>', methods=['get'])
def api_programmation(id):
    programmation = Programmation.query.filter_by(appareil_id=id).all()

    appareil = Appareil.query.get(id)

    datas = dict()
    datas['programmations'] = dict()
    datas['appareil'] = appareil.nom
    datas['id'] = id

    for data in programmation:
        datas['programmations'][data.id] = {
            'id':data.id,
            'heure_debut':data.start.hour,
            'min_debut':data.start.minute,
            'heure_fin':data.end.hour,
            'min_fin':data.end.minute,
            'day':data.day
        }

    return jsonify(datas)

@app.route('/api/mdm/<int:id>', methods=['post','get'])
def api_mdm(id):
    form = request.form
    if request.method == 'POST':
        print(request.form['mdm'])
        print(request.method)
        appareil = Appareil.query.get(id)
        appareil.mode_de_marche.mode_de_marche = request.form['mdm']
        db.session.add(appareil)
        db.session.commit()
    return render_template('test.html')

@app.route('/api/temp-min/<int:id>', methods=['get','post'])
def temp_mini(id):
    if request.method == 'POST':
        appareil = Appareil.query.get(id)
        #appareil.sonde_id.min = request.form['value']
        appareil.min = request.form['value']
        db.session.add(appareil)
        db.session.commit()
    return 'yes'

@app.route('/api/temp-max/<int:id>', methods=['get','post'])
def temp_max(id):
    if request.method == 'POST':
        appareil = Appareil.query.get(id)
        #appareil.sonde_id.max = request.form['value']
        appareil.max = request.form['value']
        db.session.add(appareil)
        db.session.commit()
    return 'yes'

@app.route('/api/programmation/delete', methods=['post'])
def api_delete_programmation():

    if request.method == 'POST':

        programmation = Programmation.query.get(request.form['appareil'])
        db.session.delete(programmation)
        db.session.commit()
    return 'nice'

@app.route('/api/delete/sonde', methods=['post'])
def api_delete_sonde():
    #sonde = Sonde.query.get(request)
    sonde = Sonde.query.get(request.form['sonde'])
    db.session.delete(sonde)
    db.session.commit()

    return redirect('/sondes')


@app.route('/api/getTime')
def api_getTime():

    tab1 = dict()
    

    # Time serveur
    dateMachine = Status.query.filter_by(identifiant='now_time').first().time_now
    
    machine = {
        'dateMachine': dateMachine,
        'connexion': tab1
    }
    return jsonify(machine)

@app.route('/api/gpios/status', methods=['get'])
def api_gpios_status():
    dateMachine = datetime.datetime.now()
    tab2 = []

    appareils = Appareil.query.all()

    myAppareils = []

    for md in appareils:
        toto = {'id_appareil': md.id, 'status': md.sortie,'status_prog':md.get_programmations()}

        if md.tempos:
            time_remaining = md.tempos.start_at+timedelta(seconds=md.tempos.consigne)-timedelta(hours=dateMachine.hour,minutes=dateMachine.minute, seconds=dateMachine.second)
            datas = str(time_remaining.hour).rjust(2,"0")+':'+str(time_remaining.minute).rjust(2,"0")+':' + str(time_remaining.second).rjust(2,"0")
            toto['tempo_start_at'] = md.tempos.start_at
            toto['tempo_start'] = md.tempos.start_at
            toto['tempo_consigne'] = md.tempos.consigne
            toto['tempo_finish'] = md.tempos.finish
            if md.tempos.start:
                toto['tempo_remaining'] = datas
            else:
                toto['tempo_remaining'] = None

        if md.mf is not None:
            toto['actived'] = md.mf.actived
            toto['debut'] = md.mf.debut
            toto['fin'] = md.mf.fin
        myAppareils.append(toto)

        # print(myAppareils)
    tab2.append({'appareils': myAppareils})
    #dateMachine = str(str(datetime.datetime.now()).split(' ')[1]).split('.')[0]

    machine = {'dateMachine': dateMachine}

    tab2.append(machine)
    gpios = Gpio.query.all()
    
    for gpio in gpios:
        try:
            status = {
                'gpio': int(gpio.valeur.split('_')[1]),
                'mode': gpio.mode,
                'level': gpio.status,
                'info': gpio.info
            }
            tab2.append(status)
        except:
            print('no ds1820b')

    sondes = Sonde.query.all()
    datas = {}
    for sonde in sondes:
        datas[sonde.nom] = {
            'temp':sonde.sonde_valeur_id.valeur,
            'nom':sonde.nom,
            'id':sonde.id,
            'sonde_info':sonde.info
        }
    tab2.append({'sondes': datas})

    # Gestion des messages
    test_messages = list()
    for message_app in appareils:
        for message in message_app.messages_app:
           test_messages.append(
               {
                   'message_id':message.id,
                   'message':message.message,
                   'message_recorded_at':message.recorded_at,
                   'message_appareil_id':message.appareil.id
               }
           )


    tab2.append({'messages':test_messages})
    return jsonify(tab2)

@app.route('/api/appareil/<int:id>', methods=['get'])
def api_appareil(id):
    appareil = Appareil.query.get(id)
    datas = {
        'appareil':appareil.nom,
        'id':id
    }
    return jsonify(datas)

#############" Marche forcée
@app.route('/api/marcheforce', methods=['post'])
def marcheforce():
    if request.method == 'POST':

        datas = {
            'name': request.form['appareil_mf'],
            'marcheforce' : request.form['marcheforce'],
            'debut' : request.form['debut']
        }


        mf = Mf.query.filter_by(appareil_mf=datas['name']).first()
        print(mf)
        if mf is None:
            mf = Mf()
            mf.appareil_mf = datas['name']


        mf.debut = datetime.datetime.strptime(datas['debut'],'%d-%m-%Y %H:%M:%S')
        mf.fin = datetime.datetime.strptime(datas['marcheforce'],'%d-%m-%Y %H:%M:%S')


        mf.actived = True
        db.session.add(mf)
        db.session.commit()

        return jsonify(datas)
    return "next"

@app.route('/api/mf/desactived/<int:id>', methods=['post','get'])
def mf_deactived(id):
    appareil = Appareil.query.get(id)
    appareil.mf.actived = False
    db.session.add(appareil)
    db.session.commit()
    return 'ik'


if __name__ == '__main__':
    app.debug = True
    #db.create_all()
    #app.run()
    app.run()
    
